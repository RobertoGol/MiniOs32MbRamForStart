# 📦 APPS_SPEC — базовые приложения и честная структура \APPs / \Data

Место: `CtOs/apps/`. Статус: спека + **реализация стадии-0**
(`CtOs/apps/apps.kt` → `apps.ctos`, 2026-11-01, [[TKT-041_apps_base_layout]]).
UI-слой (иконки/запуск из XMB) — прикладной слой CtMusic.

## Список 31 приложения (как дал владелец, не додумываем)

| # | Приложение | Категория | Слой CtOS |
|---|---|---|---|
| 1 | VLC media player | Мультимедиа | audio/gfx |
| 2 | 7-Zip | Архиватор | fs |
| 3 | WinRAR | Архиватор | fs |
| 4 | Google Chrome | Браузер | net/gfx |
| 5 | Gmail | Веб-почта | net |
| 6 | Gemini | Веб-помощник | net |
| 7 | DuckDuckGo | Поиск | net |
| 8 | Google Drive | Облако | net/fs |
| 9 | Firefox | Браузер | net/gfx |
| 10 | Notepad++ | Редактор | fs/gfx |
| 11 | Telegram | Мессенджер | net |
| 12 | Steam | Игровая платформа | gfx/net/fs |
| 13 | Winamp | Мультимедиа | audio/gfx |
| 14 | Download Software | Загрузчик | net/fs |
| 15 | Git | VCS | fs/dev |
| 16 | Node.js | JS-рантайм | dev |
| 17 | XAMPP | Веб-стек | net/dev |
| 18 | phpMyAdmin | Админ БД | net/dev |
| 19 | Wireshark | Анализ сети | net |
| 20 | qBittorrent | Торренты | net/fs |
| 21 | Everything Software | Поиск ФС | fs |
| 22 | Transmission | Торренты | net/fs |
| 23 | LibreOffice | Офис | gfx/fs |
| 24 | Mobile app Computer program | APK | честная зависимость ART |
| 25 | Listary Software | Лаунчер | fs |
| 26 | Visual Studio Codeium | Редактор кода | gfx/dev |
| 27 | Github Store | Магазин/платформа | net/dev |
| 28 | Dropbox Software | Облако | net/fs |
| 29 | Aquilum | — | ждёт уточнения владельца |
| 30 | Discord | Мессенджер/войс | net/audio |
| 31 | Gimp | Графика | gfx |

Честные три пути (по приложению): порт/сборка открытого кода, наш честный
аналог, веб-слой. Чужой проприетарный код не выдаём за свой.

## Структура

- `\APPs\<ИмяПак>\` — `app.bin` (магия TKT-009 + контрольное слово TKT-040)
  и `manifest` (имя/версия/Data-папка/типы/сечение XMB/значок/ресурсы).
- `\Data\<ИмяПак>\` — `config/`, `cache/`, `logs/`, `user/`; запись только в
  СВОЮ Data (в чужую — честный отказ 0x7050).
- `\APPs` — read-mostly, `\Data` — read/write ([[TKT-019_mount_routes]]).
- Реестр: `APP\<ИмяПак>` ([[TKT-039_regedit_ctos]]), снимается при uninstall.
- `uninstall` убирает `\APPs\` и ветку реестра, `\Data\` ОСТАЁТСЯ;
  `purge` — только явным флагом владельца (0x7048 без него).

## Реализация стадии-0 (2026-11-01)

`apps.kt` (5430 Б, 23968 опкодов, VM exit 0):

- таблица 31 записи по 32 Б: `id/cat/layer/installed/state_addr/reg_addr/section/seal`,
  курсор `0x00E503E0`;
- честные отказы установки: неизвестный 0x7041, уже стоит 0x7042, битое
  контрольное слово 0x7043 (0 папок), APK без ART 0x7044, Aquilum 0x7045;
- установлено 28 из 31 (3 — битый WinRAR, 24, 29), после uninstall+purge VLC — 27;
- uninstall: app_dir/app.bin/manifest = 0, Data-слова не тронуты (последовательность
  записей data_dir `[1,0]` — 1 при install, 0 только при purge);
- purge без флага 0x7048 (Data цела), с флагом — все 8 слов 0;
- полиция записи: своя Data 0x9C1B, чужая 0x7050;
- реестр: 27 веток после uninstall, 0 для неустановленных;
- XMB-сечение одним блоком: Photo 1 / Music 1 / Video 0 / Game 1 /
  Network 15 / Extras 9 = 27 (сходится с числом установленных).

Честный остаток: UI-иконки, текстовые имена/manifest-строки, реальные
app.bin (пока модель), XMB-запуск — прикладной слой.

## Связи
- Файлы/папки: [[TKT-038_file_explorer]]; реестр: [[TKT-039_regedit_ctos]];
  целостность: [[TKT-040_integrity_check]]; установщик: [[TKT-025_installer_tui]];
  терминал: [[TKT-018_terminal_rootcmd]]; контракт: [[TKT-009_ctos_bytecode_contract]].
