from __future__ import annotations

import random
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import Settings
from app.exceptions import ScrapingBlockedError

CAPTCHA_MARKERS = ("captcha", "cf-challenge", "g-recaptcha", "hcaptcha", "verify you are human")


class SafeHttpClient:
    """HTTP client with safe delays, browser-like headers, retries and block detection."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        retry = Retry(
            total=settings.max_retries,
            connect=settings.max_retries,
            read=settings.max_retries,
            status=settings.max_retries,
            backoff_factor=0.7,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=("GET", "HEAD"),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        }

    def absolute_url(self, url: str) -> str:
        return urljoin(self.settings.target_site + "/", url)

    def wait(self, multiplier: float = 1.0) -> None:
        time.sleep(random.uniform(self.settings.request_delay_min, self.settings.request_delay_max) * multiplier)

    def get(self, url: str) -> requests.Response:
        response = self.session.get(
            self.absolute_url(url),
            headers=self.headers,
            timeout=self.settings.request_timeout,
        )
        if response.status_code in (403, 429):
            raise ScrapingBlockedError(f"Blocked by status code {response.status_code}")
        if self.settings.stop_on_captcha and self.looks_like_captcha(response.text):
            raise ScrapingBlockedError("CAPTCHA or anti-bot page detected")
        response.raise_for_status()
        return response

    def soup(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(self.get(url).text, "lxml")

    @staticmethod
    def looks_like_captcha(html: str) -> bool:
        lower = html.lower()
        return any(marker in lower for marker in CAPTCHA_MARKERS)
