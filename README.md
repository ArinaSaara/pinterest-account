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

## Вогняний дракон (стікери і планер)

Базові стікери лежать поза git в `images/fire_dragon/` (крем) і
`images/fire_dragon/transparent/` (PNG з альфою). Промпти, ID медіа Canva і
концепція серії описані в `prompts/fire_dragon_stickers.md`.

Перебудувати аркуші, мокап, трекери і PDF-планер для GoodNotes:

```bash
python3 build_fire_dragon_assets.py
```

Потрібні Pillow і pypdf.

## Рік драконів (4 елементи)

Стікери лежать поза git у `images/fire`, `images/ice`, `images/water`,
`images/lightning` (крем + `transparent/`). Річний планер із сезонами,
4 сезонні PDF і аркуші для Pinterest:

```bash
python3 build_year_of_dragons.py
```

Мокапи для лістингу (iPad, квадрати 2000x2000 і піни 1000x1500) із
зібраних сторінок:

```bash
python3 build_mockups.py
```

Фотореалістичні мокапи: сцени з порожнім білим екраном iPad лежать у
`images/year_of_dragons/scenes/`, скрипт знаходить екран і накладає сторінку:

```bash
python3 build_photo_mockups.py
```

Відео для лістингу (15 с, без звуку, квадрат і вертикаль). Потрібні imageio
та imageio-ffmpeg, найпростіше у venv:

```bash
python3 -m venv .venv && .venv/bin/pip install imageio imageio-ffmpeg pillow numpy pypdf && .venv/bin/python build_video.py
```

## Tumblr

Ті самі піни з `pins.csv` можна постити в Tumblr. Створіть застосунок на
https://www.tumblr.com/oauth/apps (callback `http://localhost:8080/callback`),
впишіть `TUMBLR_CONSUMER_KEY` і `TUMBLR_CONSUMER_SECRET` у `.env`, потім:

```bash
python3 post_tumblr.py auth
python3 post_tumblr.py blogs
python3 post_tumblr.py publish pins.csv --dry-run
python3 post_tumblr.py publish pins.csv --queue
```

`--queue` кладе пости в чергу Tumblr, і він сам розтягує їх по часу (інтервал
налаштовується в блозі: Settings → Queue). Без `--queue` все виходить одразу.
Теги беруться з колонки `tags` у CSV, якщо вона є, інакше підбираються за назвою
картинки. Токен Tumblr живе обмежений час, скрипт оновлює його сам через
refresh-токен.

## Готичний дракон (окремий пак)

Стікери лежать поза git у `images/shadow` (крем + `transparent/`). Пак не
входить у річний планер і збирається окремо (PDF на 8 сторінок, аркуш для
Pinterest, пін): промпти, media ID і опис у `prompts/shadow_dragon_stickers.md`,
тексти лістингу в `prompts/etsy_listing_shadow.md`.

```bash
python3 build_year_of_dragons.py shadow
python3 build_pins.py
```

## Code & Cozy 2027 (щоденний планер для айтішниці)

Векторний PDF для GoodNotes (iPad, 3:4): 504 сторінки, клікабельні вкладки,
місяці, тижні, 365 денних сторінок, хаби Work / Health / Life / Notes.
Стікери беруться з `images/it_girl/src/*.webp` (10 аркушів по 8: work, fit, cozy, travel, home, hobby, social, dev, seasons, love); назви в `it_stickers.py`.

```bash
python3 -m venv .venv-planner && .venv-planner/bin/pip install reportlab pillow numpy scipy pypdf
.venv-planner/bin/python cut_it_girl_stickers.py      # 24 прозорі стікери
.venv-planner/bin/python build_it_planner.py          # старт тижня з понеділка
.venv-planner/bin/python build_it_planner.py sun      # старт тижня з неділі
.venv-planner/bin/python build_it_stickerpack.py      # стікерпак: PNG, стікербук PDF, аркуші, overview, zip
```

Шрифти в прототипі системні (Didot, Avenir Next); перед продажем замінити на
open-licence (рядки `registerFont` угорі скрипта).
