# pinterest-account

Генерація і публікація пінів у Pinterest.

## Налаштування

1. Створіть застосунок на https://developers.pinterest.com/ і отримайте access token зі scope `boards:read`, `pins:read`, `pins:write`.
2. Скопіюйте `.env.example` у `.env` і впишіть токен. Файл `.env` не потрапляє в git.
3. Покладіть картинки пінів у `images/` (рекомендовано 1000x1500, формат 2:3).
4. Заповніть `pins.csv`: картинка, назва, опис, посилання, назва дошки, alt-текст.

## Команди

```bash
python3 publish_pins.py boards
python3 publish_pins.py publish pins.csv --dry-run
python3 publish_pins.py publish pins.csv
```

Trial access у Pinterest має ліміти, для повноцінної роботи подайте заявку на Standard access.
