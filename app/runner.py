from __future__ import annotations

import logging

from app.config import Settings
from app.db import DBManager
from app.exceptions import ScrapingBlockedError
from app.notifier import TelegramNotifier
from app.parsers.contacts import ContactParser
from app.parsers.products import ProductParser

logger = logging.getLogger(__name__)


def run_prices(settings: Settings, db: DBManager, notifier: TelegramNotifier) -> None:
    parser = ProductParser(settings)
    products = parser.parse()
    for product in products:
        event = db.upsert_product(product)
        if event and event["type"] == "drop":
            notifier.price_drop(product.name, event["old_price"], event["new_price"], product.url)
    logger.info("Processed products: %s", len(products))


def run_leads(settings: Settings, db: DBManager, notifier: TelegramNotifier) -> None:
    parser = ContactParser(settings)
    contacts = parser.parse(settings.leads_path, source_type="lead")
    new_count = 0
    for contact in contacts:
        if db.insert_lead(contact):
            new_count += 1
            notifier.new_lead(contact.name, contact.email, contact.phone, contact.website)
    logger.info("Processed leads: %s, new: %s", len(contacts), new_count)


def run_customers(settings: Settings, db: DBManager, notifier: TelegramNotifier) -> None:
    parser = ContactParser(settings)
    contacts = parser.parse(settings.customers_path, source_type="customer")
    new_count = 0
    for contact in contacts:
        if db.insert_customer(contact):
            new_count += 1
    logger.info("Processed customers: %s, new: %s", len(contacts), new_count)


def run_once(settings: Settings) -> None:
    db = DBManager(settings.db_path)
    notifier = TelegramNotifier(settings)
    try:
        if settings.mode == "prices":
            run_prices(settings, db, notifier)
        elif settings.mode == "leads":
            run_leads(settings, db, notifier)
        elif settings.mode == "customers":
            run_customers(settings, db, notifier)
        elif settings.mode == "all":
            run_prices(settings, db, notifier)
            run_leads(settings, db, notifier)
            run_customers(settings, db, notifier)
        db.export_csv(settings.export_dir)
    except ScrapingBlockedError as exc:
        logger.error("Stopped safely: %s", exc)
        notifier.send_sync(f"⛔ Парсинг остановлен безопасно: {exc}")
        raise
