# Hot Girl Era: перименопаузальний планер і стікери з героїнею Марго

Четверта лінійка поруч із Code & Cozy, Soft Rebellion і драконами. Та сама
формула: героїня + ігрова механіка + undated GoodNotes-планер (3:4, вектор,
гіперлінки) + окремий стікерпак для Etsy.

Ідея: hot flash = hot girl. Жінка 42–52 як головна героїня, а не пацієнтка.
Тон: іронічний, теплий, unbothered. Слоган: "Not today, hormones."

## Героїня: Марго (Margo)

Одна фіксована героїня у всіх стікерах. Опис для промптів (англійською,
вставляється в кожен лист як `<MARGO>`):

```
Margo, a confident woman in her late forties, mid-size curvy body, warm
light-olive skin, dark chestnut chin-length bob with one bold silver streak
at the front, strong dark brows, red lipstick, tortoiseshell cat-eye
glasses, small gold hoop earrings. Outfit: cream ribbed knit top, high-waist
tangerine wide-leg trousers, bare feet or cream mules. Expression: wry,
amused, slightly tired but completely in charge.
```

Палітра (теж у кожен промпт):

```
Palette: warm cream #F6EEDF, tangerine #E8703A, hot pink #E5457A, mocha
brown #6B4A3A, soft peach #F8D9C3. No pastels, no lavender, no gold glitter.
```

Стиль:

```
Flat retro 1970s illustration with soft grainy texture, bold simple shapes,
thick confident outlines in mocha, limited palette, a little hand-drawn
wobble. Each sticker is a die-cut sticker with a thick white border.
Transparent background, no shadows, no text unless the sticker is a label.
```

## Як генерувати

Один лист = один запит. Спочатку лист 0 (character sheet), щоб зафіксувати
Марго, потім інші листи з тим же seed / референсом на лист 0. Кожен лист:
рівна сітка, однаковий розмір комірок, ніщо не торкається сусіда. Готові
листи (webp з прозорим фоном, кожен окремим повідомленням) кладемо в
`images/hot_girl/src/sheetN.webp`, потім `cut_hot_girl_stickers.py`.

Шаблон запиту:

```
A sticker sheet of <N> die-cut stickers arranged in a neat <cols> x <rows>
grid with equal spacing, nothing overlapping, transparent background.
<STYLE> <MARGO> <PALETTE>
Stickers, in reading order left to right, top to bottom:
1. ...
```

### Лист 0: character sheet (не ріжеться, лише референс)

```
Character design sheet for Margo. <MARGO> <PALETTE> <STYLE without sticker
border>. Front view full body, three-quarter view, side profile, and four
expression heads: wry smile, eyes-rolled annoyed, sweaty overheated with
pink cheeks, peaceful asleep. Cream background.
```

### Лист 1: Марго у сценах (4 x 6 = 24)

`sheet1`, cols 4. Імена в порядку читання:

| # | name | опис |
|---|------|------|
| 1 | m_fan | Margo fanning herself with a big tangerine folding fan, pink cheeks, eyes closed in relief |
| 2 | m_icewater | Margo hugging a huge glass of ice water with a straw like it is her best friend |
| 3 | m_window | Margo in pyjamas flinging a window wide open while it snows outside, blissful |
| 4 | m_thermostat | Margo glaring at a wall thermostat, finger on the dial, battle face |
| 5 | m_fog | Margo with a small fluffy cloud hovering around her head, holding keys, puzzled |
| 6 | m_lifting | Margo in a cream sports set lifting a dumbbell, proud grin |
| 7 | m_sleepmask | Margo in bed with a sleep mask pushed up, one leg out of the blanket |
| 8 | m_nightsweat | Margo sitting up in bed at night throwing off the blanket, hair stuck to forehead |
| 9 | m_rage | Margo with steam puffs rising from her head, fists clenched, comic anger |
| 10 | m_tears | Margo tearing up at her phone, tissue in hand, half-laughing at herself |
| 11 | m_shrug | Margo in sunglasses, shrugging, totally unbothered |
| 12 | m_crown | Margo wearing a small tangerine crown, chin up, queen pose |
| 13 | m_doctor | Margo holding a folder of notes, ready for the doctor, determined |
| 14 | m_nocoffee | Margo pushing away a coffee cup with one hand, sad but firm |
| 15 | m_nowine | Margo holding a wine glass at arm's length, suspicious squint |
| 16 | m_protein | Margo drinking from a shaker bottle, flexing the other arm |
| 17 | m_pills | Margo holding a pill organiser like a treasure box |
| 18 | m_walk | Margo walking fast in sneakers with headphones, hoops swinging |
| 19 | m_bath | Margo in a bubble bath with a book and a glass of ice water |
| 20 | m_reading | Margo curled in an armchair with a book, glasses on, cat on lap |
| 21 | m_scroll3am | Margo in the dark lit by a phone screen, wide awake, blanket over head |
| 22 | m_dance | Margo dancing in the kitchen with a wooden spoon as a mic |
| 23 | m_hug | Margo hugging herself, soft smile, eyes closed |
| 24 | m_coffee_ok | Margo happily holding a cup of herbal tea with both hands |

### Лист 2: лейбли симптомів і секцій (5 x 6 = 30)

`sheet2`, cols 5. Кожен лейбл: заокруглена таблетка з текстом великими
літерами, два стилі навпереміну: залитий tangerine з кремовим текстом і
кремовий з mocha-обвідкою та mocha-текстом. Лист пишемо без Марго, лише
`<PALETTE>` і `<STYLE>`.

`l_hotflash` HOT FLASH, `l_nightsweat` NIGHT SWEAT, `l_sleep` SLEEP,
`l_mood` MOOD, `l_brainfog` BRAIN FOG,
`l_headache` HEADACHE, `l_joints` JOINTS, `l_bloating` BLOATING,
`l_palpitations` PALPITATIONS, `l_energy` ENERGY,
`l_libido` LIBIDO, `l_period` PERIOD, `l_spotting` SPOTTING,
`l_skipped` SKIPPED, `l_heavy` HEAVY,
`l_cramps` CRAMPS, `l_anxiety` ANXIETY, `l_irritable` IRRITABLE,
`l_tears` TEARS, `l_dry` DRY SKIN,
`l_doctor` DOCTOR, `l_labs` LABS, `l_meds` MEDS, `l_hrt` HRT,
`l_supplements` SUPPLEMENTS,
`l_water` WATER, `l_protein` PROTEIN, `l_workout` WORKOUT,
`l_steps` STEPS, `l_win` WIN

### Лист 3: нагороди, героїня-база, шкали (4 x 6 = 24)

`sheet3`, cols 4. Це механіка "Build your Hot Girl": базова Марго + 8
аксесуарів, які наклеюються на неї на сторінці профілю. Аксесуари малюються
окремо, кожен як самостійний стікер приблизно в масштабі до бази.

| # | name | опис |
|---|------|------|
| 1 | base_margo | Margo full body standing, neutral relaxed pose, arms slightly away from the body so accessories can be placed on her, no accessories |
| 2 | a_sleepmask | a cream sleep mask with a tangerine trim and a tiny moon, standalone |
| 3 | a_dumbbell | a hot pink dumbbell, standalone |
| 4 | a_shaker | a cream protein shaker bottle with a tangerine lid, standalone |
| 5 | a_bottle | a tall water bottle full of ice cubes, standalone |
| 6 | a_potion | a small brown apothecary bottle labelled MG with a tiny sparkle, standalone |
| 7 | a_folder | a cream folder of papers with a pink paperclip and a check mark, standalone |
| 8 | a_fan | an open tangerine folding fan with hot pink edge, standalone |
| 9 | a_crown | a small tangerine crown with pink gems, standalone |
| 10 | f1 | a cute thermometer with a tiny fan icon, level 1 of 5, mostly cream |
| 11 | f2 | the same thermometer, level 2 of 5 |
| 12 | f3 | the same thermometer, level 3 of 5, peach |
| 13 | f4 | the same thermometer, level 4 of 5, tangerine |
| 14 | f5 | the same thermometer, level 5 of 5, hot pink and bursting at the top |
| 15 | moon_new | a new moon, dark mocha circle with cream outline |
| 16 | moon_wax | a waxing crescent moon, cream |
| 17 | moon_full | a full moon, cream with a tiny face |
| 18 | moon_wane | a waning crescent moon, cream |
| 19 | drop1 | one small hot pink drop |
| 20 | drop2 | two hot pink drops |
| 21 | drop3 | three hot pink drops |
| 22 | x_ice | a stack of three ice cubes, cream and peach |
| 23 | x_thermostat | a round wall thermostat with an angry little face |
| 24 | x_window | an open window with snowflakes blowing in |

### Лист 4: цитати і декор (4 x 6 = 24)

`sheet4`, cols 4. Цитати: короткі фрази в рукописному або ретро-гротеску в
кремовій таблетці або на хвилястій стрічці, `<PALETTE>`, без Марго.

| # | name | текст / опис |
|---|------|--------------|
| 1 | q_nottoday | "not today, hormones" |
| 2 | q_estrogen | "it's not me, it's estrogen" |
| 3 | q_maincharacter | "main character, still" |
| 4 | q_openwindow | "open the window" |
| 5 | q_hotgirlera | "hot girl era" in bold retro letters |
| 6 | q_unbothered | "unbothered" |
| 7 | q_imfine | "I'm fine" with little flames around it |
| 8 | q_fogmode | "fog mode: on" |
| 9 | q_plottwist | "plot twist" |
| 10 | q_stillhot | "still hot. literally." |
| 11 | q_rest | "rest is productive" |
| 12 | q_askdoctor | "ask the doctor" |
| 13 | washi_tang | a strip of tangerine washi tape with cream polka dots |
| 14 | washi_pink | a strip of hot pink washi tape with thin cream stripes |
| 15 | washi_check | a strip of cream and mocha gingham washi tape |
| 16 | d_frame | a cream retro rounded photo frame with a tangerine border |
| 17 | d_banner | a wavy hot pink ribbon banner, empty |
| 18 | d_arrow | a chunky curved tangerine arrow |
| 19 | d_heart | a chunky hot pink heart with a cream highlight |
| 20 | d_lipstick | an open red lipstick |
| 21 | d_sunglasses | tortoiseshell cat-eye sunglasses |
| 22 | d_icedcoffee | a tall iced drink with a straw |
| 23 | d_cat | a round orange cat asleep in a loaf |
| 24 | d_flame | a small friendly flame with a cute face |

Усього 102 стікери.

## Збірка

```bash
.venv-planner/bin/python cut_hot_girl_stickers.py      # коли листи на диску
.venv-planner/bin/python build_hot_girl_planner.py     # працює і без стікерів (пропуски)
```

Результат у `images/hot_girl/`: `Hot_Girl_Era_Perimenopause_Planner.pdf`
і `Hot_Girl_Era_Sticker_Pack.pdf`.

Обов'язкове в лістингу та на сторінці "How it works": "This planner is a
tracking tool, not medical advice." Жодних обіцянок полегшити симптоми.
