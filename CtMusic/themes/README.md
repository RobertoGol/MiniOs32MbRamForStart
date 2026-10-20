# 🎨 Темы оболочки CtOs (XMB)

Папка — дом тем оболочки. Два слоя:

```
CtMusic/themes/
├── builtin/            ← встроенные темы (зафиксированные заимствования из PSP)
│   ├── xmb_classic/    ← официальная прошивка Sony (6.35/6.60)
│   ├── ark4_dark/      ← кастом ARK-4 / cIPL
│   ├── gen_d3_orange/  ← кастом 5.50 GEN-D3
│   └── mac_leopard/    ← кастомная «Mac OS X Leopard»
└── custom/             ← КАСТОМНЫЕ ТЕМЫ ПОЛЬЗОВАТЕЛЕЙ (для нашей ОС)
```

## Правило «скинул — привязалось»
1. Пользователь кладёт папку темы в `themes/custom/<имя_темы>/`.
2. Оболочка при старте (или Settings → Theme Settings → «Обновить темы»)
   сканирует `custom/` и добавляет каждую валидную тему в список.
3. Переключение: **Settings → Theme Settings → <тема>** — как на PSP.
4. Битые темы (нет `theme.json` или не хватает файлов) не падают системой:
   они помечаются как `invalid` в логе Early Boot и пропускаются.

## Формат темы
```
<имя_темы>/
├── theme.json          ← манифест (обязателен)
├── wallpaper.png       ← фон XMB (480×272, или больше — оболочка ужмёт)
├── wave.png            ← «волна» фона (полоса-градиент, можно прозрачный PNG)
├── icons/              ← иконки категорий и пунктов (PNG 48×48 и 24×24)
│   ├── settings.png
│   ├── extras.png
│   ├── photo.png
│   ├── music.png
│   ├── video.png
│   ├── game.png
│   └── network.png
├── boot.webm           ← (опционально) свой загрузочный ролик, см. Readme
└── sounds/             ← (опционально) звуки навигации: select.wav, back.wav
```

## Манифест `theme.json`
```json
{
  "name": "My Night Theme",
  "author": "RJ",
  "version": "1.0",
  "base": "ark4_dark",
  "colors": {
    "highlight":      "#FF9A1F",
    "text":           "#FFFFFF",
    "text_dim":       "#B8B8C8",
    "wave_top":       "#1A1A2E",
    "wave_bottom":    "#16213E",
    "info_panel":     "#202040"
  },
  "fonts": { "main": "system", "size": "normal" },
  "visualizer": { "style": "wave", "color": "#00FF66" }
}
```

Поля:
*   `name` / `author` / `version` — показываются в Theme Settings;
*   `base` — тема-родитель: недостающие файлы наследуются у неё
    (кастомная тема может состоять из одного `theme.json` с цветами);
*   `colors` — палитра оболочки (подсветка, текст, волна, инфо-панель);
*   `visualizer` — стиль и цвет визуализатора плеера (референс: зелёная
    осциллограмма PSP-Go).

## Список встроенных тем (зафиксировали — не трогаем без обсуждения)
| Папка | Источник | Что берём |
|---|---|---|
| `builtin/xmb_classic` | официальная Sony 6.35/6.60 | синяя волна, серебро, System Information |
| `builtin/ark4_dark` | ARK-4 / cIPL | тёмное меню, оранжевый акцент, ★ CFW Settings |
| `builtin/gen_d3_orange` | 5.50 GEN-D3 | оранжевый градиент, красные акценты |
| `builtin/mac_leopard` | кастом «Mac OS X Leopard» | логин-панель, Finder-менюбар, док |
