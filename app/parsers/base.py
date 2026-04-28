from __future__ import annotations

from urllib.parse import urljoin

from bs4 import Tag

from app.config import Settings
from app.http_client import SafeHttpClient


class BaseParser:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = SafeHttpClient(settings)

    def paginate(self, start_path: str):
        """Yield soup pages. Stops by MAX_PAGES or missing next link."""
        path = start_path

        for page_no in range(1, self.settings.max_pages + 1):
            soup = self.client.soup(path)
            page_url = self.client.absolute_url(path)

            yield soup, page_url, page_no

            next_link = soup.select_one(self.settings.next_page_selector)
            if not next_link or not next_link.get("href"):
                break

            href = next_link["href"]

            # Важно: строим следующую страницу относительно текущей страницы,
            # а не относительно главного домена.
            path = urljoin(page_url, href)

            self.client.wait(
                multiplier=2.0 if self.settings.mode == "all" else 1.0
            )

    @staticmethod
    def text(node: Tag | None) -> str | None:
        return node.get_text(" ", strip=True) if node else None

    def abs_href(self, node: Tag | None, fallback: str | None = None) -> str | None:
        if node and node.get("href"):
            return self.client.absolute_url(node["href"])
        return fallback