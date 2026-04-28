from __future__ import annotations

from app.cleaner import normalize_text, parse_price
from app.config import Settings
from app.models import Product
from app.parsers.base import BaseParser


class ProductParser(BaseParser):
    """Generic product parser configured by CSS selectors from .env."""

    def parse(self) -> list[Product]:
        products: list[Product] = []
        for soup, page_url, page_no in self.paginate(self.settings.products_path):
            cards = soup.select(self.settings.product_card_selector)
            if not cards:
                break
            for card in cards:
                name = normalize_text(self.text(card.select_one(self.settings.product_name_selector)))
                price = parse_price(self.text(card.select_one(self.settings.product_price_selector)))
                availability = normalize_text(self.text(card.select_one(self.settings.product_availability_selector)))
                link = self.abs_href(card.select_one(self.settings.product_link_selector), fallback=page_url)
                if not name or not link:
                    continue
                products.append(Product(
                    site=self.settings.target_site,
                    name=name,
                    price=price,
                    availability=availability,
                    url=link,
                ))
                if len(products) >= self.settings.max_items:
                    return products
        return products
