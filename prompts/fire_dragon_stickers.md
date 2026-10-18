# Вогняний дракон: стікери від народження до дорослішання

Серія з 8 стікерів у тому ж стилі, що й водяний дракон з референсу:
акварель, die-cut стікер із білою обвідкою, кремовий папір, один персонаж
на кожен вік. Промпти англійською, бо так генератори (Midjourney, DALL-E,
Canva, Ideogram, Leonardo) дають стабільніший результат.

## Спільний блок стилю (додавати до кожного промпту)

```
watercolor illustration, die-cut sticker with a thin white border, soft
textured cream paper background, loose wet-on-wet washes with fine ink
details, luminous glowing highlights, fantasy fire dragon, warm palette of
ember orange, coral red, golden yellow and soft peach with hints of violet
in the shadows, tiny floating sparks and embers around the character,
consistent character design across the series, clean isolated composition,
no text, no watermark
```

Негативний промпт (де підтримується):

```
text, watermark, logo, photorealistic, 3d render, dark background, blurry,
extra limbs, multiple characters, cropped, frame, border other than sticker edge
```

Параметри: Midjourney `--ar 2:3 --style raw --s 250` для пінів (2:3) або
`--ar 1:1` для аркуша стікерів. Для серії тримайте один seed, щоб дракон
не змінював зовнішність.

## 8 стікерів за віком

### 1. Яйце (ще до народження)

```
a single pale blue dragon egg with a crystalline faceted shell, thin glowing
orange cracks spreading across the surface, warm ember light shining from
inside, a few tiny flames flickering on the top of the shell, resting on a
small bed of glowing embers and soft smoke, cool blue shell contrasting with
the warm fire inside
```

### 2. Вилуплення (новонароджений)

```
a tiny chubby newborn fire dragon peeking out of a cracked blue egg, big
round amber eyes, soft coral-red scales, tiny stubby horns, little claws
gripping the broken shell edge, wisps of smoke and small sparks rising from
the egg, surprised cute expression
```

### 3. Малюк (перший вогник)

```
a baby fire dragon sitting in a small puff of flames, round body, oversized
head, big glowing amber eyes, mouth open in a joyful squeak with a tiny
puff of fire and smoke coming out, small undeveloped wings like little
flaming petals, scattered sparks and embers around it
```

### 4. Дитина (гра з вогнем)

```
a young fire dragon kneeling and holding a glowing fireball between its
front paws, happy curious expression, small translucent wings with ember
glow at the tips, a short tail ending in a little flame, coral and gold
scales, sparks drifting upward
```

### 5. Підліток (перший політ)

```
a slender juvenile fire dragon in a playful leaping pose, body starting to
stretch longer, growing crest of flame-like spines along the head and
back, medium-sized wings with a soft orange glow, tail trailing a ribbon
of fire, confident friendly expression, cascading embers below
```

### 6. Юнак (стихія)

```
an adolescent fire dragon with a long serpentine body coiled around a
curling wave of flame, like a fire version of a crashing ocean wave,
larger wings spread, longer snout and horns, spines along the spine
glowing like embers, swirling smoke and sparks around the body
```

### 7. Молодий дорослий (володар полум'я)

```
a young adult fire dragon, elegant elongated body rising upward through
swirling tongues of flame, large detailed wings with gradient from deep
red to golden yellow, long flowing whisker-like flames from the jaw,
intense but calm expression, spiraling fire tail, embers and sparks
spiraling around it
```

### 8. Дорослий (повна сила)

```
a majestic adult fire dragon with long branching antler-like horns, very
long serpentine body winding through a tall column of roaring flames and
dark smoke, pale golden belly scales, deep crimson and orange back scales
with a soft iridescent sheen, flowing mane of fire, wise and powerful
expression, a few embers drifting away
```

## Промпт для цілого аркуша (8 стікерів однією картинкою)

```
sticker sheet of 8 watercolor die-cut stickers arranged in two rows of
four on cream textured paper, showing the life stages of one fire dragon
from left to right: a pale blue egg with glowing orange cracks, a newborn
dragon hatching from the egg, a baby dragon with its first puff of fire,
a child dragon holding a fireball, a leaping juvenile with a flaming tail,
an adolescent coiled around a wave of fire, a young adult rising through
flames, a majestic antlered adult in a column of fire and smoke, each
sticker has a thin white border, consistent character design growing
older and larger in each step, warm palette of ember orange, coral red and
golden yellow, luminous glow, tiny sparks, no text
--ar 1:1
```

## Поради

- Згенеруйте спершу аркуш, щоб затвердити дизайн персонажа, а потім
  окремі стікери через той самий seed або image prompt з аркуша.
- Для Pinterest робіть окремі піни 1000x1500 (2:3) з кожного стікера і
  один пін з усім аркушем.
- Якщо яйце має бути не синім, а вогняним, замініть у першому промпті
  `pale blue` на `deep red and gold` і приберіть фразу про контраст.

## Згенеровано (Canva, 2026-10-18)

Файли 1000x1500 PNG лежать у images/fire_dragon/. Дизайн Canva з усіма 8 сторінками: https://www.canva.com/d/Zi2P_661YmjgZsy (ID DAHYYXpQPus). Оригінали 1024x1536 зберігаються в медіатеці Canva. Для редагування через
Canva generate-image (image-to-image) використовуйте ці media ID:

| # | Стікер | Файл | Canva media ID |
|---|--------|------|----------------|
| 1 | Яйце | images/fire_dragon/01_egg.png | MAHYYDZSpZY |
| 2 | Вилуплення | images/fire_dragon/02_hatching.png | MAHYYPje-WU |
| 3 | Малюк | images/fire_dragon/03_baby_first_flame.png | MAHYYD4M7bc |
| 4 | Дитина | images/fire_dragon/04_child_fireball.png | MAHYYJAJCCQ |
| 5 | Підліток | images/fire_dragon/05_juvenile_leap.png | MAHYYIJXl4c |
| 6 | Юнак | images/fire_dragon/06_adolescent_fire_wave.png | MAHYYH4S_cY |
| 7 | Молодий дорослий | images/fire_dragon/07_young_adult.png | MAHYYOBTnLc |
| 8 | Дорослий | images/fire_dragon/08_adult.png | MAHYYLNP-SA |

## Прозорі версії для GoodNotes

Папка `images/fire_dragon/transparent/`: 8 обрізаних PNG з альфа-каналом і
аркуш `fire_dragon_sheet_transparent.png` (4300x3180). Фон знято через Canva
remove-background, сторінки 9-16 того самого дизайну DAHYYXpQPus.
Media ID вирізаних версій: MAHYYX9rAZ8, MAHYYZIb9ac, MAHYYV1lsdM, MAHYYUzZR6Q,
MAHYYR86-W8, MAHYYYft6Sg, MAHYYeeZLy4, MAHYYTjZ9-Q.

## Сторінка-приклад для GoodNotes

`images/fire_dragon/goodnotes_usage_page.png` (2000x3000, 2:3) - мокап планера
зі стікерами: тижневий розворот, 30-денний стрік, де дракон росте з кожним
етапом, трекер звичок і підказка, як вставляти стікери. Зібрано локально
через Pillow, шрифти Avenir Next і Bradley Hand.

## Трекери для GoodNotes (1536x2048, iPad 3:4)

Папка `images/fire_dragon/trackers/`: habit (5 звичок x 31 день, 155 віх),
reading (сторінки до 5000), savings "Dragon Hoard" (50 монет по 2%),
focus (80 сесій по 25 хв). У кожного зверху смуга росту дракона з 8
стадіями: приглушені стікери, поверх яких вклеюють кольорові з аркуша.

Концепція серії: дракон як шкала прогресу. Вогняний - перший елемент,
далі водяний, земляний, крижаний, грозовий як окремі паки.

## Планер (PDF для GoodNotes)

`images/fire_dragon/planner/Fire_Dragon_Planner_GoodNotes.pdf` - 9 сторінок
1536x2048: обкладинка, зміст з клікабельними посиланнями, how it works,
аркуш стікерів, 4 трекери, порожня сторінка в крапку. На внутрішніх
сторінках заголовок веде назад на зміст. Зібрано Pillow + pypdf
(посилання через pypdf.annotations.Link), PNG сторінок лежать поряд.

## Тест стилів

`images/fire_dragon/style_tests/style_comparison.jpg`: A - поточний набір,
B - prompt-only "light & airy" (надто блідий), C - image-to-image з
крижаним аркушем як референсом (media MAHYYc_HU50). Сторінки 17-20 дизайну.

## Версія 2 (стиль C, 2026-10-18)

Увесь вогняний набір перегенеровано image-to-image з крижаним аркушем як
референсом стилю (media MAHYYc_HU50). Сторінки 21-28 (крем) і 29-36
(прозорі) дизайну DAHYYXpQPus. Стара версія лежить у images/fire_dragon/v1_old/.
Усі похідні файли (аркуші, мокап, трекери, планер) перебудовуються
скриптом `python3 build_fire_dragon_assets.py`.

| # | Крем (v2) | Прозорий (v2) |
|---|-----------|---------------|
| 1 | MAHYYakiM40 | MAHYYeLdzJs |
| 2 | MAHYYUvRRm4 | MAHYYUlnIVc |
| 3 | MAHYYe4kMgA | MAHYYXDd6Hc |
| 4 | MAHYYaAIe3c | MAHYYQulUjs |
| 5 | MAHYYTUsQcw | MAHYYUj1FpA |
| 6 | MAHYYYbgNUw | MAHYYRJ8A54 |
| 7 | MAHYYaITero | MAHYYZ-b0-A |  (перегенеровано: політ, без рогів; попередня версія у v1_old/v2_stage7_antlers)
| 8 | MAHYYRI7HaI | MAHYYQgbylI |

## Рік драконів (2026-10-18)

Лід, вода і гроза перегенеровано по 8 стадій image-to-image з аркушами
користувача як референсом (Canva media: лід MAHYYc_HU50, вода MAHYYpUihqA,
гроза MAHYYnZsKXU). Дизайн-контейнер DAHYYutJDEg: сторінки 2-9 лід крем,
10-17 лід прозорі, 18-25 вода крем, 26-33 вода прозорі, 34-41 гроза крем,
42-49 гроза прозорі. Файли: images/ice, images/water, images/lightning
(+ transparent/), images/fire -> symlink на fire_dragon.

Збірка: `python3 build_year_of_dragons.py` -> images/year_of_dragons/:
повний планер 33 сторінки, 4 сезонні PDF по 8 сторінок, аркуші для Pinterest.
Сезони: осінь вогонь (звички, фокус), зима лід (читання, сон), весна вода
(вода, настрій), літо гроза (навчання, заощадження). Рік у calendar: YEAR=2027.

## Імена драконів (лор у змісті планера)

Ember (вогонь, осінь), Lumi (лід, зима), Marin (вода, весна), Volt (гроза, літо).
Мокапи: images/year_of_dragons/mockups/, скрипт build_mockups.py.

## Фото-мокапи

Сцени згенеровано в Canva (media: стіл MAHYYkpAa0c, льон MAHYYqJX4Ic, руки
MAHYYlgGNdg; сторінки 50-52 дизайну DAHYYutJDEg), екран навмисно порожній
білий. build_photo_mockups.py знаходить білу пляму, бере 4 кути і
накладає сторінку перспективою. Результат у images/year_of_dragons/mockups_photo/.
