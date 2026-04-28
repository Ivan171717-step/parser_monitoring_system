from __future__ import annotations

import asyncio
from telegram import Bot

from app.config import Settings


class TelegramNotifier:
    def __init__(self, settings: Settings):
        self.enabled = bool(settings.telegram_bot_token and settings.telegram_chat_id)
        self.chat_id = settings.telegram_chat_id
        self.bot = Bot(settings.telegram_bot_token) if self.enabled else None

    async def send(self, text: str) -> None:
        if not self.enabled or not self.bot or not self.chat_id:
            return
        await self.bot.send_message(chat_id=self.chat_id, text=text, disable_web_page_preview=True)

    def send_sync(self, text: str) -> None:
        if not self.enabled:
            return
        try:
            asyncio.run(self.send(text))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.create_task(self.send(text))

    def price_drop(self, product_name: str, old_price: float | None, new_price: float | None, url: str) -> None:
        self.send_sync(f"🔻 Цена снизилась\n{product_name}\n{old_price} → {new_price}\n{url}")

    def new_lead(self, name: str, email: str | None, phone: str | None, website: str | None) -> None:
        parts = [f"🆕 Новый контакт: {name}"]
        if email:
            parts.append(f"Email: {email}")
        if phone:
            parts.append(f"Телефон: {phone}")
        if website:
            parts.append(f"Сайт: {website}")
        self.send_sync("\n".join(parts))
