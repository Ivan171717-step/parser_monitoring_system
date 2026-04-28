from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Product:
    site: str
    name: str
    price: Optional[float]
    availability: Optional[str]
    url: str


@dataclass(slots=True)
class Contact:
    source: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    url: Optional[str] = None
