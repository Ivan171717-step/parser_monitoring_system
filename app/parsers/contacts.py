from __future__ import annotations

from app.cleaner import find_email, find_phone, normalize_text
from app.config import Settings
from app.models import Contact
from app.parsers.base import BaseParser


class ContactParser(BaseParser):
    """Generic contact parser for leads/customers from public catalog-like pages."""

    def parse(self, path: str, source_type: str) -> list[Contact]:
        contacts: list[Contact] = []
        for soup, page_url, page_no in self.paginate(path):
            cards = soup.select(self.settings.contact_card_selector)
            if not cards:
                # Fallback: treat full page as one card, useful for simple pages.
                cards = [soup]
            for card in cards:
                text = card.get_text(" ", strip=True)
                name = normalize_text(self.text(card.select_one(self.settings.company_name_selector)))
                if not name:
                    continue
                email = find_email(text)
                phone = find_phone(text, region=self.settings.default_region)
                website_node = card.select_one(self.settings.contact_website_selector)
                website = self.abs_href(website_node) if website_node else None
                contact_url = website or page_url
                contacts.append(Contact(
                    source=source_type,
                    name=name,
                    email=email,
                    phone=phone,
                    website=website,
                    url=contact_url,
                ))
                if len(contacts) >= self.settings.max_items:
                    return contacts
        return contacts
