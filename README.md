<<<<<<< HEAD
# Parsing & Monitoring System

Готовый модульный Python-проект для:

- мониторинга цен товаров;
- сбора контактов магазинов/продавцов;
- поиска потенциальных клиентов из открытых каталогов;
- хранения данных в SQLite;
- экспорта `products.csv`, `leads.csv`, `customers.csv`, `price_changes.csv`;
- уведомлений и команд через Telegram-бота.

> Важно: используйте систему только для открытых данных, соблюдайте robots.txt/ToS сайта, не обходите CAPTCHA и не перегружайте сайты. При 403/429/CAPTCHA проект останавливается безопасно.

## Структура

```text
parser_monitoring_system/
├── app/
│   ├── config.py
│   ├── db.py
│   ├── cleaner.py
│   ├── http_client.py
│   ├── notifier.py
│   ├── runner.py
│   ├── models.py
│   ├── exceptions.py
│   ├── parsers/
│   │   ├── base.py
│   │   ├── products.py
│   │   └── contacts.py
│   └── telegram_bot/
├── data/exports/
├── main.py
├── bot.py
├── scheduler.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Установка

```bash
cd parser_monitoring_system
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`. Реальные токены, ключи, логины и пароли храните только в `.env`; файл уже добавлен в `.gitignore`.

## Быстрый запуск

```bash
python main.py --site https://example.com --mode prices
python main.py --site https://example.com --mode leads
python main.py --site https://example.com --mode customers
python main.py --site https://example.com --mode all
```

Также режим и сайт можно задать в `.env`:

```dotenv
TARGET_SITE=https://example.com
MODE=all
```

## Режимы

- `prices` — парсит товары, сравнивает цены, пишет историю.
- `leads` — собирает контакты магазинов/продавцов.
- `customers` — собирает потенциальных клиентов из открытых каталогов.
- `all` — выполняет всё последовательно с увеличенными задержками и безопасной остановкой при блокировках.

## Telegram-бот

1. Создайте бота через BotFather.
2. В `.env` добавьте:

```dotenv
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=123456789
TELEGRAM_ALLOWED_USER_IDS=123456789
```

Запуск:

```bash
python bot.py
```

Команды:

```text
/prices      последние изменения цен
/new_leads   новые контакты
/summary     статистика
/run prices  ручной запуск режима
/run all     ручной запуск всего пайплайна
```

## Автоматический запуск

Через встроенный scheduler:

```bash
python scheduler.py
```

Период задаётся в `.env`:

```dotenv
RUN_EVERY_HOURS=6
TIMEZONE=Europe/Zaporozhye
```

Или через cron:

```cron
0 */6 * * * cd /path/parser_monitoring_system && /path/.venv/bin/python main.py --mode prices
```

## Как адаптировать под другой сайт

Основной код менять не нужно. Настройте в `.env` URL, пути и CSS-селекторы.

Пример для товаров:

```dotenv
TARGET_SITE=https://shop.example.com
PRODUCTS_PATH=/catalog
PRODUCT_CARD_SELECTOR=.product-card
PRODUCT_NAME_SELECTOR=.product-card__title
PRODUCT_PRICE_SELECTOR=.product-card__price
PRODUCT_AVAILABILITY_SELECTOR=.product-card__stock
PRODUCT_LINK_SELECTOR=a.product-card__link
NEXT_PAGE_SELECTOR=a.pagination__next
```

Пример для контактов:

```dotenv
LEADS_PATH=/stores
CONTACT_CARD_SELECTOR=.store-card
COMPANY_NAME_SELECTOR=.store-card__name
CONTACT_WEBSITE_SELECTOR=a.store-card__website
DEFAULT_REGION=UA
```

Если сайт динамический, сначала проверьте вкладку Network в DevTools: часто данные приходят JSON-запросом, который проще и безопаснее парсить через `requests`. Selenium оставлен как зависимость для расширения, но базовый шаблон работает через `requests + BeautifulSoup`.

## Что сохраняется

SQLite база: `data/parser_monitoring.db`.

Таблицы:

- `products`
- `price_history`
- `leads`
- `customers`

CSV экспорт после каждого запуска:

- `data/exports/products.csv`
- `data/exports/leads.csv`
- `data/exports/customers.csv`
- `data/exports/price_changes.csv`

## Безопасный парсинг

Настройки:

```dotenv
REQUEST_DELAY_MIN=3
REQUEST_DELAY_MAX=7
MAX_PAGES=10
MAX_ITEMS=200
MAX_RETRIES=3
STOP_ON_CAPTCHA=true
REQUEST_TIMEOUT=20
```

Система:

- ставит User-Agent;
- использует timeout;
- ограничивает страницы и количество записей;
- делает случайные задержки;
- повторяет запросы ограниченно;
- останавливается при 403, 429 или признаках CAPTCHA;
- не пишет секреты в код и логи.
=======
# 🔎 Parser Monitoring System

Система для парсинга сайтов, мониторинга цен и сбора контактов с уведомлениями в Telegram.

---

## 🚀 Возможности

- 📦 Мониторинг цен товаров
- 📉 Отслеживание изменений цен
- 🧲 Сбор контактов (email, телефон, сайт)
- 👥 Поиск потенциальных клиентов
- 💾 Хранение в SQLite + CSV
- 🤖 Telegram-бот с уведомлениями
- ⏱ Автоматический запуск

---

## ⚙️ Установка

```bash
git clone https://github.com/YOUR_USERNAME/parser_monitoring_system.git
cd parser_monitoring_system

python -m venv .venv
.venv\Scripts\activate  # Windows

pip install -r requirements.txt
>>>>>>> 6cb8f83f1a5db7de79f50160d44da6014a8d267c
