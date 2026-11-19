# -*- coding: utf-8 -*-
"""A7: детерминированный сборщик диска данных CtOS (сырой 32 МиБ raw-образ).

Это НЕ загрузочный диск. Одновременно делаются две вещи — «смесь 1 и 2»:

  1. FAT16 с папками, чтобы человек видел структуру и мог скопировать файлы
     с обычного ПК:
       CTOS/APPS/    — исполняемые модули .ctos (байткод нашего интерпретатора)
       CTOS/GAMES/   — игры .ctos
       CTOS/MUSIC/   — звуковые ассеты (сырые данные)
       CTOS/VIDEO/   — видео-ассеты (сырые данные)
     В каждой папке лежит README.TXT с объяснением, куда что класть; в APPS
     дополнительно скопированы готовые модули из CTMD.

  2. Свой каталог в зарезервированных секторах LBA 8..71 (вне FAT16-раздела).
     У него фиксированные смещения и CRC-32, поэтому загрузчику не нужен
     FAT-драйвер: он читает 64 сектора по INT 13h и проверяет CRC каталога.
     В хвосте этой области лежат тела модулей для A8.
     FAT — для человека, каталог — для машины.

Каталог (все числа LE):
  [0..8)    магия 'CTOSCAT1'
  [8..12)   версия = 1
  [12..16)  число записей
  [16..20)  зарезервировано = 0
  [20..24)  CRC-32 байт [0..24+64*count), при вычислении поле CRC = 0
  [24..]    записи по 64 Б:
              [0]     kind: 1=APPS, 2=GAMES, 3=MUSIC, 4=VIDEO
              [1..16) имя 8.3 ASCIIZ
              [16..20) LBA файла
              [20..24) число секторов
              [24..28) размер файла
              [28..32) CRC-32 файла
              [32..36) A8: смещение тела внутри CAT-области (0 = нет тела)
              [36..64) нули
  остаток 8 секторов — нули.

Запуск:
  python -X utf8 CtOs/native/build_data_image.py [out.img]
"""
import hashlib
import io
import os
import struct
import sys
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUT = os.path.join(REPO, "CtOs", "native", "ctos_data.img")

SECTOR = 512
IMAGE_SECTORS = 65536                 # 32 МиБ
PART_LBA = 2048
PART_SECTORS = IMAGE_SECTORS - PART_LBA
SPC = 4                               # секторов на кластер = 2 КиБ
RESERVED = 1
ROOT_ENTRIES = 512
ROOT_SECTORS = ROOT_ENTRIES * 32 // SECTOR
FAT_SECTORS = 62
FAT_COUNT = 2
DATA_START = RESERVED + FAT_COUNT * FAT_SECTORS + ROOT_SECTORS
DATA_SECTORS = PART_SECTORS - DATA_START
CLUSTERS = DATA_SECTORS // SPC
FAT_BYTES = (CLUSTERS + 2) * 2
assert 4085 <= CLUSTERS < 0xFFF0, CLUSTERS
assert FAT_BYTES <= FAT_SECTORS * SECTOR, (FAT_BYTES, FAT_SECTORS * SECTOR)

CAT_LBA = 8
CAT_SECTORS = 64                      # LBA 8..71: 32 КиБ, A7-каталог + A8-тела
CAT_MAGIC = b"CTOSCAT1"
A8_BODY_BASE = 0x1000                 # смещение первого тела внутри CAT-области
A8_BODY_ALIGN = 16
MARKER_OFF = 0x180
DATA_MARKER = b"CTOS-DATA-A7!\x00\x00\x00\x00"

# (имя для каталога <=15 байт, путь .ctos, имя 8.3 в FAT)
MODULES = [
    ("memmgr.CTS",   "CtOs/memmgr.ctos",                   "MEMMGR  CTS"),
    ("sched.CTS",    "CtOs/kernel_sched.ctos",             "SCHED   CTS"),
    ("syscall.CTS",  "Python_compiler/syscall_test.ctos",  "SYSCALL CTS"),
    ("stage1.CTS",   "Compiler/stage1_compiler.ctos",      "STAGE1  CTS"),
]
FOLDERS = ("APPS", "GAMES", "MUSIC", "VIDEO")
README = {
    "APPS": (b"CTOS DATA / APPS\r\n"
             b"Put .ctos bytecode modules here (8.3 names).\r\n"
             b"The installer copies the built-in modules here.\r\n"),
    "GAMES": (b"CTOS DATA / GAMES\r\n"
              b"Put game .ctos modules here (8.3 names).\r\n"
              b"Native x86/PE programs are NOT supported yet.\r\n"),
    "MUSIC": (b"CTOS DATA / MUSIC\r\n"
              b"Put raw audio assets here (8.3 names).\r\n"
              b"There is no audio decoder in the runtime yet.\r\n"),
    "VIDEO": (b"CTOS DATA / VIDEO\r\n"
              b"Put raw video assets here (8.3 names).\r\n"
              b"There is no video decoder in the runtime yet.\r\n"),
}
KIND = {"APPS": 1, "GAMES": 2, "MUSIC": 3, "VIDEO": 4}
README_NAME = "README  TXT"


def le16(v):
    return struct.pack("<H", v)


def le32(v):
    return struct.pack("<I", v)


def name11(s):
    """Имя ровно 11 байт — иначе срез в dirent сдвинет всю запись."""
    b = s.encode("ascii") if isinstance(s, str) else s
    if len(b) > 11:
        raise SystemExit("A7: имя длиннее 8.3: %r" % b)
    return b + b" " * (11 - len(b))


def dirent(name, attr, cluster, size):
    """Один 32-байтный entry FAT16; времена обнулены ради детерминизма."""
    e = bytearray(32)
    e[0:11] = name11(name)
    e[11] = attr
    struct.pack_into("<H", e, 26, cluster & 0xFFFF)
    struct.pack_into("<I", e, 28, size)
    return bytes(e)


class Fat16:
    def __init__(self):
        self.next_cluster = 2
        self.fat = [0] * (CLUSTERS + 2)
        self.fat[0] = 0xFFF8
        self.fat[1] = 0xFFFF
        self.img = bytearray(PART_SECTORS * SECTOR)

    def reserve(self, nbytes):
        """Только выделить номера кластеров, данные записать позже."""
        need = max(1, (nbytes + SECTOR * SPC - 1) // (SECTOR * SPC))
        if self.next_cluster + need > CLUSTERS + 2:
            raise SystemExit("A7: FAT16 переполнен")
        first = self.next_cluster
        for i in range(need):
            c = first + i
            self.fat[c] = 0xFFFF if i == need - 1 else c + 1
        self.next_cluster += need
        return first

    def write(self, first, data):
        pos = 0
        c = first
        while pos < len(data):
            off = (DATA_START + (c - 2) * SPC) * SECTOR
            chunk = data[pos:pos + SECTOR * SPC]
            self.img[off:off + len(chunk)] = chunk
            pos += len(chunk)
            c = self.fat[c]

    def lba_of(self, first):
        return PART_LBA + DATA_START + (first - 2) * SPC

    def finish(self, root):
        for i, v in enumerate(self.fat):
            struct.pack_into("<H", self.img, RESERVED * SECTOR + i * 2, v)
            struct.pack_into("<H", self.img,
                             (RESERVED + FAT_SECTORS) * SECTOR + i * 2, v)
        root_off = (RESERVED + FAT_COUNT * FAT_SECTORS) * SECTOR
        root_len = ROOT_ENTRIES * 32
        if len(root) > root_len:
            raise SystemExit("A7: root-каталог переполнен")
        # Срез фиксированной длины: короткая запись сжала бы весь bytearray
        # и съехали бы все последующие LBA.
        self.img[root_off:root_off + root_len] = (bytes(root) +
                                                  b"\x00" * (root_len - len(root)))
        return self.img


def catalog_entry(kind, name, lba, data, body_off=0):
    e = bytearray(64)
    e[0] = kind
    nm = name.encode("ascii")[:15]
    e[1:1 + len(nm)] = nm
    struct.pack_into("<IIIII", e, 16, lba,
                     (len(data) + SECTOR - 1) // SECTOR,
                     len(data), zlib.crc32(data) & 0xFFFFFFFF, body_off)
    return bytes(e)


def build(out_path):
    fs = Fat16()

    # 1. Файлы: сначала резервируем все кластеры, потом пишем данные.
    files = []          # (kind, имя в каталоге, 8.3, данные, cluster, LBA)
    for name, rel, fatname in MODULES:
        data = io.open(os.path.join(REPO, rel), "rb").read()
        cl = fs.reserve(len(data))
        files.append((1, name, fatname, data, cl))
    for folder in FOLDERS:
        data = README[folder]
        cl = fs.reserve(len(data))
        files.append((KIND[folder], folder + "/README",
                      README_NAME, data, cl))

    # 2. Каталоги: CTOS резервируем первым, чтобы дети знали "..".
    ctos_cl = fs.reserve(1)
    child_cl = {folder: fs.reserve(1) for folder in FOLDERS}

    # 3. Пишем тела файлов.
    for _kind, _cname, _fatname, data, cl in files:
        fs.write(cl, data)

    # 4. Пишем подкаталоги с правильными "." и "..".
    apps_entries = [dirent(".", 0x10, child_cl["APPS"], 0),
                    dirent("..", 0x10, ctos_cl, 0)]
    for kind, _cname, fatname, data, cl in files:
        if kind == 1:                       # модули + README папки APPS
            apps_entries.append(dirent(fatname, 0x20, cl, len(data)))
    fs.write(child_cl["APPS"], b"".join(apps_entries))

    for folder in FOLDERS:
        if folder == "APPS":
            continue
        entries = [dirent(".", 0x10, child_cl[folder], 0),
                   dirent("..", 0x10, ctos_cl, 0)]
        for _kind, _cname, fatname, data, cl in files:
            if fatname == README_NAME and _kind == KIND[folder]:
                entries.append(dirent(fatname, 0x20, cl, len(data)))
        fs.write(child_cl[folder], b"".join(entries))

    ctos_entries = [dirent(".", 0x10, ctos_cl, 0),
                    dirent("..", 0x10, 0, 0)]
    for folder in FOLDERS:
        ctos_entries.append(dirent(folder, 0x10, child_cl[folder], 0))
    fs.write(ctos_cl, b"".join(ctos_entries))

    root = bytearray()
    root += dirent("CTOSDATA", 0x08, 0, 0)            # volume label
    root += dirent("CTOS", 0x10, ctos_cl, 0)

    # 5. Загрузочный сектор FAT16.
    boot = bytearray(SECTOR)
    boot[0:3] = b"\xEB\x3C\x90"
    boot[3:11] = b"MSWIN4.1"
    struct.pack_into("<H", boot, 11, SECTOR)
    boot[13] = SPC
    struct.pack_into("<H", boot, 14, RESERVED)
    boot[16] = FAT_COUNT
    struct.pack_into("<H", boot, 17, ROOT_ENTRIES)
    struct.pack_into("<H", boot, 19, PART_SECTORS)
    boot[21] = 0xF8
    struct.pack_into("<H", boot, 22, FAT_SECTORS)
    struct.pack_into("<H", boot, 24, 63)
    struct.pack_into("<H", boot, 26, 255)
    struct.pack_into("<I", boot, 28, PART_LBA)
    boot[36] = 0x80
    boot[38] = 0x29
    struct.pack_into("<I", boot, 39, 0x43544F53)     # 'CTOS'
    boot[43:54] = b"CTOSDATA   "
    boot[54:62] = b"FAT16   "
    struct.pack_into("<H", boot, 510, 0xAA55)
    partition = fs.finish(root)
    partition[:SECTOR] = boot

    # 6. MBR: маркер роли и раздел FAT16.
    img = bytearray(IMAGE_SECTORS * SECTOR)
    img[MARKER_OFF:MARKER_OFF + len(DATA_MARKER)] = DATA_MARKER
    pt = 0x1BE                                       # таблица разделов в LBA0
    img[pt + 4] = 0x06                               # FAT16
    struct.pack_into("<II", img, pt + 8, PART_LBA, PART_SECTORS)
    struct.pack_into("<H", img, SECTOR - 2, 0xAA55)
    img[PART_LBA * SECTOR:PART_LBA * SECTOR + len(partition)] = partition

    # 7. Машинный каталог LBA 8..71 + A8-тела в хвосте этой же области.
    #    Тела — точная копия байт из FAT-файлов, но загрузчик читает их
    #    одним INT 13h вместе с каталогом, и PM получает их без INT 13h.
    bodies = bytearray()
    body_offsets = {}
    for kind, cname, _fatname, data, cl in files:
        body_off = 0
        if kind == 1 and "/" not in cname:
            bodies += b"\x00" * ((-len(bodies)) % A8_BODY_ALIGN)
            body_off = A8_BODY_BASE + len(bodies)
            bodies += data
        body_offsets[cname] = body_off
    if A8_BODY_BASE + len(bodies) > CAT_SECTORS * SECTOR:
        raise SystemExit("A8: тела модулей не помещаются в CAT-область")

    entries = bytearray()
    for kind, cname, _fatname, data, cl in files:
        entries += catalog_entry(kind, cname, fs.lba_of(cl), data,
                                 body_offsets[cname])
    cat = bytearray(CAT_MAGIC)
    cat += le32(1) + le32(len(files)) + le32(0) + le32(0)
    cat += entries
    # CRC по непрерывному [0..24+64*count), поле CRC на время счёта = 0.
    # Это позволяет stage2 вызвать crc32_body один раз без конкатенации.
    crc = zlib.crc32(bytes(cat)) & 0xFFFFFFFF
    struct.pack_into("<I", cat, 20, crc)
    cat += b"\x00" * (CAT_SECTORS * SECTOR - len(cat))
    # Тела лежат после каталога и НЕ входят в его CRC; каждое из них
    # покрывается CRC своей записи и перепроверяется в native_rt.c.
    cat[A8_BODY_BASE:A8_BODY_BASE + len(bodies)] = bodies
    img[CAT_LBA * SECTOR:CAT_LBA * SECTOR + len(cat)] = cat

    io.open(out_path, "wb").write(bytes(img))
    return bytes(img)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    img = build(out)
    print("CTOS DATA OK: %s — %d Б, md5 %s, папки CTOS/{APPS,GAMES,MUSIC,VIDEO}, "
          "каталог LBA8..%d" %
          (out, len(img), hashlib.md5(img).hexdigest(),
           CAT_LBA + CAT_SECTORS - 1))
