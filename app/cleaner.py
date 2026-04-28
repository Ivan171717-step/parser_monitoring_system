from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

import phonenumbers
from email_validator import EmailNotValidError, validate_email

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", value).strip()
    return text or None


def parse_price(raw: str | None) -> float | None:
    if not raw:
        return None
    text = raw.replace("\xa0", " ")
    text = re.sub(r"[^\d,\.]+", "", text)
    if not text:
        return None
    if text.count(",") == 1 and text.count(".") == 0:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")
    try:
        return float(Decimal(text))
    except (InvalidOperation, ValueError):
        return None


def find_email(text: str | None) -> str | None:
    if not text:
        return None
    match = EMAIL_RE.search(text)
    return normalize_email(match.group(0)) if match else None


def normalize_email(email: str | None) -> str | None:
    if not email:
        return None
    try:
        return validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        return None


def find_phone(text: str | None, region: str = "US") -> str | None:
    if not text:
        return None
    for match in PHONE_RE.findall(text):
        phone = normalize_phone(match, region=region)
        if phone:
            return phone
    return None


def normalize_phone(raw_phone: str | None, region: str = "US") -> str | None:
    if not raw_phone:
        return None
    try:
        number = phonenumbers.parse(raw_phone, region)
    except phonenumbers.NumberParseException:
        return None
    if not phonenumbers.is_valid_number(number):
        return None
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
