from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import load_settings
from app.db import DBManager
from app.runner import run_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
settings = load_settings([])
db = DBManager(settings.db_path)


def authorized(update: Update) -> bool:
    if not settings.telegram_allowed_user_ids:
        return True
    user = update.effective_user
    return bool(user and user.id in settings.telegram_allowed_user_ids)


async def guard(update: Update) -> bool:
    if authorized(update):
        return True
    if update.message:
        await update.message.reply_text("Доступ запрещён.")
    return False


async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update):
        return
    rows = db.latest_price_changes(limit=10)
    if not rows:
        await update.message.reply_text("Изменений цен пока нет.")
        return
    text = "Последние изменения цен:\n" + "\n".join(
        f"• {r['name']}: {r['old_price']} → {r['new_price']} ({r['change_type']})"
        for r in rows
    )
    await update.message.reply_text(text[:3900], disable_web_page_preview=True)


async def new_leads(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update):
        return
    rows = db.latest_contacts(table="leads", limit=10)
    if not rows:
        await update.message.reply_text("Новых контактов пока нет.")
        return
    text = "Новые контакты:\n" + "\n".join(
        f"• {r['name']} | {r['email'] or '-'} | {r['phone'] or '-'} | {r['website'] or '-'}"
        for r in rows
    )
    await update.message.reply_text(text[:3900], disable_web_page_preview=True)


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update):
        return
    s = db.summary()
    await update.message.reply_text(
        "Сводка:\n"
        f"Товаров: {s['products']}\n"
        f"Изменений цен: {s['price_changes']}\n"
        f"Лидов: {s['leads']}\n"
        f"Клиентов: {s['customers']}\n"
        f"Средняя цена: {s['avg_price'] or 0:.2f}"
    )


async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await guard(update):
        return
    mode = context.args[0] if context.args else settings.mode
    if mode not in {"prices", "leads", "customers", "all"}:
        await update.message.reply_text("Использование: /run prices|leads|customers|all")
        return
    local_settings = load_settings(["--mode", mode])
    try:
        run_once(local_settings)
        await update.message.reply_text(f"Готово. Режим: {mode}")
    except Exception as exc:
        await update.message.reply_text(f"Остановлено: {exc}")


def main() -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("prices", prices))
    app.add_handler(CommandHandler("new_leads", new_leads))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("run", run_cmd))
    app.run_polling()


if __name__ == "__main__":
    main()
