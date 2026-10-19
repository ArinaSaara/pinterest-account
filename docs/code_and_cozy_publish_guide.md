# Code & Cozy: як заповнити лістинг на Etsy і запостити піни

Усі готові тексти (назва, теги, опис) лежать у `prompts/etsy_listing_code_and_cozy.md`. Файли лежать у `images/it_girl/`.

## 1. Створення лістингу на Etsy

1. Відкрий https://www.etsy.com/your/shops/me/tools/listings і натисни **Add a listing** (прямий лінк: https://www.etsy.com/your/shops/me/listing-editor/create).
2. **Photos (до 10):** з `images/it_girl/mockups/` у цьому порядку: `01_hero_square`, `02_daily_page`, `03_everything_linked`, `04_whats_inside`, `05_work_hub`, `06_health_life`, `07_all_stickers`, `08_sticker_sets`, `09_year_view`, `10_how_it_works`. Перше фото стає обкладинкою.
3. **Video:** `images/it_girl/video/video_listing_square.mp4` (14,9 с, без звуку).
4. **Title:** скопіюй з `prompts/etsy_listing_code_and_cozy.md`, розділ Title (до 140 символів).
5. **About this listing:** Who made it: *I did*; What is it: *A finished product*; When was it made: *2020–2026* (або поточний період, який Etsy запропонує). Тут же Etsy просить розкрити AI: познач, що в зображеннях використано AI-інструменти.
6. **Category:** Paper & Party Supplies > Paper > Calendars & Planners (або почни писати «planner» і вибери з підказок).
7. **Primary colour:** Green, **secondary:** Brown. Occasion і Holiday порожні.
8. **Description:** блок між потрійними лапками з того ж файлу.
9. **Tags:** 13 тегів з файлу (вставляй по одному, до 20 символів).
10. **Price:** 14 USD на старті, потім 16–18. Quantity 999.
11. **Type of item:** *Digital*. Завантаж 5 файлів (по ≤ 20 МБ):
    - `Code_and_Cozy_Planner_2027_Mon.pdf`
    - `Code_and_Cozy_Planner_2027_Sun.pdf`
    - `sticker_pack/Code_and_Cozy_Stickers_Part1.zip`
    - `sticker_pack/Code_and_Cozy_Stickers_Part2.zip`
    - `sticker_pack/Code_and_Cozy_Sticker_Book.pdf`
12. **Shipping/Returns:** для цифрових товарів доставка не потрібна; поверненнь немає (так і написано в описі).
13. Натисни **Publish**. Скопіюй URL лістингу, він має вигляд `https://www.etsy.com/listing/<ID>/<slug>`.

Довідка Etsy про цифрові товари: https://help.etsy.com/hc/en-us/articles/115015628347

## 2. Піни в Pinterest

12 пінів лежать у `images/it_girl/pins/` (1000×1500, до 1 МБ). Тексти й alt-текст у `pins_code_and_cozy.csv`.

**Спосіб А, вручну** (надійніше, поки Trial-доступ API обмежений):
1. https://www.pinterest.com/pin-creation-tool/ → завантаж зображення.
2. Title, Description і Alt text візьми з CSV, у Destination link встав URL лістингу.
3. Борди: *Digital Planners* (піни 01–07) і *Digital Stickers* (08–12). Створи їх на https://www.pinterest.com/<твій_профіль>/_created/, якщо їх ще немає.
4. Публікуй по 1–2 піни на день, а не всі одразу.

**Спосіб Б, скриптом** (як для Year of Dragons):
```bash
LISTING_URL="https://www.etsy.com/listing/<ID>/<slug>" .venv-planner/bin/python build_it_pins.py
python3 publish_pins.py publish pins_code_and_cozy.csv --dry-run
python3 publish_pins.py publish pins_code_and_cozy.csv
```
Потрібен токен у `.env` (див. README). Борди з CSV мають існувати.

## 3. Після публікації

- Додай лінк на лістинг у біо Pinterest і Tumblr.
- Перший тиждень: знижка 20 % (Etsy: Marketing > Sales and discounts) і запит на відгуки покупцям.
