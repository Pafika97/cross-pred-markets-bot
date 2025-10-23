# Cross-Platform Prediction Markets Watcher

Скрипт сравнивает темы (markets) на трех платформах — **Polymarket**, **Kalshi**, **Myriad** — и отправляет сообщение в телеграм‑чат, если одна и та же тема появляется хотя бы на двух платформах.

## Что делает
1. Забирает список активных рынков:
   - Polymarket — публичный Gamma API (`GET https://gamma-api.polymarket.com/markets`).
   - Kalshi — публичный API без ключа (`GET https://api.elections.kalshi.com/trade-api/v2/markets?limit=1000`).
   - Myriad — *опционально*. Требуется ключ к partner REST API (см. `MYRIAD_API_BASE` и `MYRIAD_API_KEY`). Если ключ не задан — адаптер пропускается.
2. Нормализует заголовки рынков (приводит к нижнему регистру, удаляет знаки препинания, убирает стоп-слова).
3. Сопоставляет рынки по схожести заголовков, используя RapidFuzz `token_set_ratio`.
4. Если есть совпадения с порогом схожести ≥ `TITLE_SIM_THRESHOLD` и количество платформ в кластере ≥ `REQUIRE_AT_LEAST`, отправляет сообщение в Telegram Bot API.

## Быстрый старт
1. Установите Python 3.10+
2. Скачайте архив из этого чата и распакуйте.
3. В папке проекта выполните:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
4. Откройте `.env` и заполните:
   - `TELEGRAM_BOT_TOKEN` — токен вашего бота (от BotFather)
   - `TELEGRAM_CHAT_ID` — ID вашего чата/канала (можно узнать у @userinfobot)
   - При необходимости измените `POLL_SECONDS`, `TITLE_SIM_THRESHOLD`.
   - Если у вас есть доступ к Myriad API — задайте `MYRIAD_API_BASE` и `MYRIAD_API_KEY`. Иначе оставьте пустым.

5. Запуск:
   ```bash
   python main.py
   ```

## Как это работает (детали)
- **Polymarket**: используется публичный Gamma API `GET /markets` (документация в `docs.polymarket.com`).
- **Kalshi**: используется публичная область `https://api.elections.kalshi.com/trade-api/v2`. Эндпоинт `GET /markets?limit=` возвращает массив `markets` с полями `title`, `ticker`, `close_time` и т.д.
- **Myriad**: у некоторых интеграций — партнёрский REST API (с токеном). В адаптере оставлен универсальный запрос к `GET {MYRIAD_API_BASE}/markets`. При необходимости подправьте путь полей `title/url/endDate` под ваш фактический ответ API.

## Настройка оповещений
Сообщения отправляются в **тот чат**, чей ID указан в `.env`:
- Включено `parse_mode=HTML`, поэтому можно безопасно вставлять ссылки и выделение.
- Если переменные Telegram не заданы — скрипт просто печатает сообщение в консоль (для отладки).

## Алгоритм сопоставления
- Нормализация заголовков + RapidFuzz `token_set_ratio`.
- Порог схожести по умолчанию `86` (регулируется в `.env`).
- Требуемое число платформ в кластере: `REQUIRE_AT_LEAST=2`.
- Логирование найденных совпадений опционально в CSV — `MATCH_LOG_PATH`.

## Prod‑советы
- Поставьте скрипт как systemd‑сервис или в Docker/cron.
- Добавьте retry/backoff для нестабильных сетей.
- Расширьте `STOPWORDS` в `matcher.py` под ваши типовые темы (например, общие слова “prediction”, “market”, “yes/no”).
- При необходимости реализуйте хранение seen‑hashes, чтобы не спамить один и тот же кластер повторно.

## Лицензия
MIT
