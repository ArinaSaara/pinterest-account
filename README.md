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
