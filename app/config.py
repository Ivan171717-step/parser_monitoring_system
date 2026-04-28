from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

VALID_MODES = {"prices", "leads", "customers", "all"}


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "y", "on"}


def _csv_ints(name: str) -> set[int]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return set()
    return {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}


@dataclass(frozen=True)
class Settings:
    target_site: str
    mode: str
    request_delay_min: float
    request_delay_max: float
    max_pages: int
    max_items: int
    max_retries: int
    stop_on_captcha: bool
    request_timeout: int
    use_selenium: bool
    default_region: str
    products_path: str
    leads_path: str
    customers_path: str
    db_path: str
    export_dir: str
    telegram_bot_token: str | None
    telegram_chat_id: str | None
    telegram_allowed_user_ids: set[int]
    run_every_hours: int
    timezone: str

    # Product selectors
    product_card_selector: str
    product_name_selector: str
    product_price_selector: str
    product_availability_selector: str
    product_link_selector: str
    next_page_selector: str

    # Contact selectors
    contact_card_selector: str
    company_name_selector: str
    contact_website_selector: str


def load_settings(argv: list[str] | None = None) -> Settings:
    parser = argparse.ArgumentParser(description="Parsing and monitoring system")
    parser.add_argument("--site", default=os.getenv("TARGET_SITE", "https://example.com"))
    parser.add_argument("--mode", default=os.getenv("MODE", "all"), choices=sorted(VALID_MODES))
    parser.add_argument("--max-pages", type=int, default=int(os.getenv("MAX_PAGES", 10)))
    parser.add_argument("--max-items", type=int, default=int(os.getenv("MAX_ITEMS", 200)))
    parser.add_argument("--use-selenium", action="store_true", default=_bool("USE_SELENIUM", False))
    args = parser.parse_args(argv)

    delay_min = float(os.getenv("REQUEST_DELAY_MIN", 3))
    delay_max = float(os.getenv("REQUEST_DELAY_MAX", 7))
    if delay_max < delay_min:
        delay_max = delay_min

    return Settings(
        target_site=args.site.rstrip("/"),
        mode=args.mode,
        request_delay_min=delay_min,
        request_delay_max=delay_max,
        max_pages=args.max_pages,
        max_items=args.max_items,
        max_retries=int(os.getenv("MAX_RETRIES", 3)),
        stop_on_captcha=_bool("STOP_ON_CAPTCHA", True),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", 20)),
        use_selenium=args.use_selenium,
        default_region=os.getenv("DEFAULT_REGION", "US"),
        products_path=os.getenv("PRODUCTS_PATH", "/products"),
        leads_path=os.getenv("LEADS_PATH", "/stores"),
        customers_path=os.getenv("CUSTOMERS_PATH", "/directory"),
        db_path=os.getenv("DB_PATH", "data/parser_monitoring.db"),
        export_dir=os.getenv("EXPORT_DIR", "data/exports"),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN") or None,
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID") or None,
        telegram_allowed_user_ids=_csv_ints("TELEGRAM_ALLOWED_USER_IDS"),
        run_every_hours=int(os.getenv("RUN_EVERY_HOURS", 6)),
        timezone=os.getenv("TIMEZONE", "Europe/Zaporozhye"),
        product_card_selector=os.getenv("PRODUCT_CARD_SELECTOR", ".product-item"),
        product_name_selector=os.getenv("PRODUCT_NAME_SELECTOR", ".name"),
        product_price_selector=os.getenv("PRODUCT_PRICE_SELECTOR", ".price"),
        product_availability_selector=os.getenv("PRODUCT_AVAILABILITY_SELECTOR", ".stock"),
        product_link_selector=os.getenv("PRODUCT_LINK_SELECTOR", "a"),
        next_page_selector=os.getenv("NEXT_PAGE_SELECTOR", "a.next"),
        contact_card_selector=os.getenv("CONTACT_CARD_SELECTOR", ".company,.store,.seller,.listing"),
        company_name_selector=os.getenv("COMPANY_NAME_SELECTOR", ".company-name,.store-name,.title,h2,h3"),
        contact_website_selector=os.getenv("CONTACT_WEBSITE_SELECTOR", "a.website,a[href^='http']"),
    )
