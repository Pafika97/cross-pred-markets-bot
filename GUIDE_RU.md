# Пошаговая инструкция (RU)

Эта инструкция поможет запустить бота, который ищет одинаковые темы (новости/рынки) на **Polymarket**, **Kalshi** и **Myriad** и присылает уведомления в Telegram‑чат.

---

## 1) Требования
- Python 3.10 или выше
- Доступ в интернет
- (Опционально) ключ к партнёрскому API Myriad

---

## 2) Скачать и распаковать проект
1. Скачайте архив из чата (`cross_pred_markets_bot.zip`).
2. Распакуйте в удобную папку. Пример: `C:\projects\cross_pred_markets_bot` или `/home/you/cross_pred_markets_bot`.

Структура папки:
```
cross_pred_markets_bot/
  adapters/
    kalshi_adapter.py
    myriad_adapter.py
    polymarket_adapter.py
  matcher.py
  notifier.py
  main.py
  README.md
  requirements.txt
  .env.example
  GUIDE_RU.md   <-- эта инструкция
```

---

## 3) Создать Telegram‑бота и получить токен
1. В Telegram найдите `@BotFather`.
2. Команда `/newbot` → укажите название и username для бота.
3. Скопируйте выданный **BOT TOKEN**, он понадобится в `.env`.

---

## 4) Узнать ID чата (куда слать сообщения)
- Если это приватный чат с вами: напишите любому боту `@userinfobot` → он покажет ваш **chat id**.
- Если это группа/канал:
  1) Добавьте своего бота в группу/канал и дайте право “писать сообщения”.  
  2) Отправьте любое сообщение в этот чат.  
  3) Используйте бота `@RawDataBot` или `@getidsbot` → он вернёт **chat id** (обычно начинается с `-100...` для каналов).

---

## 5) Установить зависимости проекта
Откройте терминал/PowerShell в папке проекта и выполните:

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux (bash/zsh)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Примечание: Если `python` указывает на Python 2, используйте `python3`.

---

## 6) Настроить переменные окружения
1. Скопируйте файл пример конфигурации:
   ```bash
   cp .env.example .env
   ```
   На Windows можно сделать это вручную через проводник (скопировать и переименовать).

2. Откройте `.env` и заполните:
   - `TELEGRAM_BOT_TOKEN` — токен бота от BotFather.
   - `TELEGRAM_CHAT_ID` — ID чата/канала.
   - `POLL_SECONDS` — период опроса рынков (в секундах), по умолчанию `300`.
   - `TITLE_SIM_THRESHOLD` — порог схожести заголовков (0..100), по умолчанию `86`.
   - `REQUIRE_AT_LEAST` — минимальное число платформ для оповещения (обычно `2`).

3. (Опционально) если у вас есть доступ к Myriad API:
   - `MYRIAD_API_BASE` — базовый URL партнёрского REST.
   - `MYRIAD_API_KEY` — ключ авторизации.

---

## 7) Запуск
Из активированного окружения:
```bash
python main.py
```
В консоли вы увидите логи вида:
```
[START] Cross-platform watcher (every 300s). Press Ctrl+C to stop.
[INFO] fetched 123 from Polymarket
[INFO] fetched 456 from Kalshi
[INFO] fetched 0 from Myriad
[INFO] No cross-platform matches found this run.
```
Когда найдены совпадающие темы на ≥2 платформах — придёт сообщение в Telegram.

---

## 8) Формат уведомления
Сообщение содержит список платформ, заголовки и ссылки на соответствующие рынки. Пример:
```
Совпадение темы на нескольких платформах — Polymarket, Kalshi
• Polymarket: <заголовок>
  https://polymarket.com/event/...
• Kalshi: <заголовок>
  https://kalshi.com/markets/...
```

---

## 9) Логирование совпадений (CSV)
В `.env` можно указать путь `MATCH_LOG_PATH` (например, `matches_log.csv`). Тогда каждый найденный кластер сохраняется в CSV.

---

## 10) Частые проблемы и решения
- **Сообщений нет**:  
  - Проверьте, что бот добавлен в чат/канал и ему разрешено писать.  
  - Убедитесь, что `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` верны.  
  - Возможно, схожесть заголовков недостаточна — уменьшите `TITLE_SIM_THRESHOLD` (например, 80).  
  - Проверьте сеть/блокировки, подождите один‑два цикла опроса.

- **SSL/Cert ошибки при `pip install`**:  
  - Повторите позже, обновите `pip` (`python -m pip install --upgrade pip`).

- **Myriad не работает**:  
  - Если нет ключа/базы, адаптер отключится автоматически — это нормально.  
  - Если ключ есть — проверьте правильность полей `title/url/endDate` в `adapters/myriad_adapter.py` под ваш ответ API.

---

## 11) Автозапуск на сервере (кратко)
### systemd (Linux)
Создайте юнит `/etc/systemd/system/cross-pred.service`:
```
[Unit]
Description=Cross Prediction Markets Bot
After=network-online.target

[Service]
WorkingDirectory=/home/you/cross_pred_markets_bot
ExecStart=/home/you/cross_pred_markets_bot/.venv/bin/python /home/you/cross_pred_markets_bot/main.py
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cross-pred.service
journalctl -u cross-pred.service -f
```

### cron (Linux/macOS) — вариант с периодическим запуском
Можно запускать `python main.py` внутри скрипта‑обёртки, но предпочтительнее `systemd` (он рестартит процесс при сбоях).

---

## 12) Тонкая настройка сопоставления
Откройте `matcher.py`:
- Добавляйте/убирайте слова в `STOPWORDS`.
- Меняйте алгоритм на `fuzz.partial_ratio`/`fuzz.WRatio`, если это даёт больше точности для ваших сценариев.

---

## 13) Обновления и расширения
- Добавить “seen‑hashes”, чтобы не дублировать один и тот же кластер.
- Расширить список платформ (например, Manifold/Metaculus с новостными событиями — потребуется свой адаптер и API).
- Перейти на webhooks, если платформы их поддержат.

Удачной работы!
