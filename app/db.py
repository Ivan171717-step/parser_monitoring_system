from __future__ import annotations

import csv
import os
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from app.models import Contact, Product


class DBManager:
    def __init__(self, db_path: str = "data/parser_monitoring.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                name TEXT NOT NULL,
                price REAL,
                availability TEXT,
                url TEXT NOT NULL UNIQUE,
                first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                old_price REAL,
                new_price REAL NOT NULL,
                change_type TEXT NOT NULL,
                changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                company_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                website TEXT,
                url TEXT,
                added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                website TEXT,
                url TEXT,
                added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_price_history_changed_at ON price_history(changed_at);
            CREATE INDEX IF NOT EXISTS idx_leads_added_at ON leads(added_at);
            CREATE INDEX IF NOT EXISTS idx_customers_added_at ON customers(added_at);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_leads_unique ON leads(source, company_name, COALESCE(email, ''), COALESCE(phone, ''), COALESCE(website, ''));
            CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_unique ON customers(source, name, COALESCE(email, ''), COALESCE(phone, ''), COALESCE(website, ''));
            """
        )
        self.conn.commit()

    def upsert_product(self, product: Product) -> dict | None:
        """Insert/update product. Return price-change event if price changed."""
        cur = self.conn.cursor()
        old = cur.execute("SELECT id, price FROM products WHERE url = ?", (product.url,)).fetchone()
        if old is None:
            cur.execute(
                """
                INSERT INTO products(site, name, price, availability, url)
                VALUES (?, ?, ?, ?, ?)
                """,
                (product.site, product.name, product.price, product.availability, product.url),
            )
            product_id = cur.lastrowid
            if product.price is not None:
                cur.execute(
                    """
                    INSERT INTO price_history(product_id, old_price, new_price, change_type)
                    VALUES (?, NULL, ?, 'new')
                    """,
                    (product_id, product.price),
                )
            self.conn.commit()
            return {"type": "new", "product": product, "old_price": None, "new_price": product.price}

        product_id = int(old["id"])
        old_price = old["price"]
        change = None
        if product.price is not None and old_price != product.price:
            change_type = "drop" if old_price is not None and product.price < old_price else "increase"
            cur.execute(
                """
                INSERT INTO price_history(product_id, old_price, new_price, change_type)
                VALUES (?, ?, ?, ?)
                """,
                (product_id, old_price, product.price, change_type),
            )
            change = {"type": change_type, "product": product, "old_price": old_price, "new_price": product.price}

        cur.execute(
            """
            UPDATE products
            SET site=?, name=?, price=?, availability=?, last_checked_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (product.site, product.name, product.price, product.availability, product_id),
        )
        self.conn.commit()
        return change

    def insert_lead(self, contact: Contact) -> bool:
        return self._insert_contact("leads", contact, name_column="company_name")

    def insert_customer(self, contact: Contact) -> bool:
        return self._insert_contact("customers", contact, name_column="name")

    def _insert_contact(self, table: str, contact: Contact, name_column: str) -> bool:
        cur = self.conn.cursor()
        try:
            cur.execute(
                f"""
                INSERT INTO {table}(source, {name_column}, email, phone, website, url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (contact.source, contact.name, contact.email, contact.phone, contact.website, contact.url),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def latest_price_changes(self, limit: int = 10) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT ph.changed_at, ph.change_type, p.name, p.url, ph.old_price, ph.new_price
            FROM price_history ph
            JOIN products p ON p.id = ph.product_id
            ORDER BY ph.changed_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    def latest_contacts(self, table: str = "leads", limit: int = 10) -> list[sqlite3.Row]:
        if table not in {"leads", "customers"}:
            raise ValueError("table must be leads or customers")
        name_col = "company_name" if table == "leads" else "name"
        return self.conn.execute(
            f"SELECT added_at, {name_col} AS name, email, phone, website, url FROM {table} ORDER BY added_at DESC LIMIT ?",
            (limit,),
        ).fetchall()

    def summary(self) -> dict[str, int | float | None]:
        row = self.conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM products) AS products,
                (SELECT COUNT(*) FROM price_history WHERE change_type != 'new') AS price_changes,
                (SELECT COUNT(*) FROM leads) AS leads,
                (SELECT COUNT(*) FROM customers) AS customers,
                (SELECT AVG(price) FROM products WHERE price IS NOT NULL) AS avg_price
            """
        ).fetchone()
        return dict(row)

    def export_csv(self, export_dir: str) -> None:
        Path(export_dir).mkdir(parents=True, exist_ok=True)
        exports = {
            "products.csv": "SELECT * FROM products ORDER BY id",
            "leads.csv": "SELECT * FROM leads ORDER BY id",
            "customers.csv": "SELECT * FROM customers ORDER BY id",
            "price_changes.csv": """
                SELECT ph.id, p.name, p.url, ph.old_price, ph.new_price, ph.change_type, ph.changed_at
                FROM price_history ph JOIN products p ON p.id = ph.product_id
                ORDER BY ph.changed_at DESC
            """,
        }
        for filename, query in exports.items():
            rows = self.conn.execute(query).fetchall()
            path = Path(export_dir) / filename
            with path.open("w", encoding="utf-8", newline="") as f:
                if not rows:
                    f.write("")
                    continue
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows([dict(r) for r in rows])
