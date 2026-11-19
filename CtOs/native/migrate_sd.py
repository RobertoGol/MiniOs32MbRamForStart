# -*- coding: utf-8 -*-
"""A12: «наш скрипт» переноса флэшки на единый SD-диск (только модель/сборка).

Сценарий пользователя: BIOS увидел загрузчик на флэшке -> скрипт переносит
ВСЁ на SD-карту -> флэшку можно убрать -> загрузка и все модули продолжаются
уже с SD. Здесь делается ровно перенос байт-в-байт, без «магического» pin:

  flash.img  = boot-образ (LBA 0..135) + data-образ целиком с LBA 2048
               + маркер CTOS-INST-A5 в LBA0+0x180
  sd.img     = полная копия flash.img, но в LBA0+0x180 стоит CTOS-TGT-A5!,
               чтобы штатный A5-установщик закрепил загрузку уже в госте.

Семантику native_rt.c не трогаем. NIC/network/шифрования нет.
QEMU — только локальная эмуляционная контрольная точка; на R3700 НЕ заявляется.
Физически R3700 сейчас не подключён (нет диска, SD и питания), SD-загрузка
BIOS на нём не проверялась.

Запуск: python -X utf8 CtOs/native/migrate_sd.py <flash.img> <sd.img>
"""
import hashlib
import io
import os
import struct
import sys

SECTOR = 512
DATA_LBA = 2048
CAT_LBA = DATA_LBA + 8
DATA_IMG_SECTORS = 65536
MARKER_OFF = 0x180
SRC_MARKER = b"CTOS-INST-A5\x00\x00\x00\x00"
TGT_MARKER = b"CTOS-TGT-A5!\x00\x00\x00\x00"
DATA_MARKER = b"CTOS-DATA-A7!"
CAT_MAGIC = b"CTOSCAT1"
NEED_LEN = (DATA_LBA + DATA_IMG_SECTORS) * SECTOR


def migrate(flash, verbose=True):
    """Вернуть байты SD-образа или бросить ValueError с честной причиной."""
    if len(flash) < NEED_LEN:
        raise ValueError("flash слишком мал: %d Б, нужно >= %d Б"
                         % (len(flash), NEED_LEN))
    if flash[MARKER_OFF:MARKER_OFF + 16] != SRC_MARKER:
        raise ValueError("нет маркера CTOS-INST-A5 в LBA0+0x180 — "
                         "это не установочная флэшка")

    dbase = DATA_LBA * SECTOR
    if flash[dbase + MARKER_OFF:dbase + MARKER_OFF + 13] != DATA_MARKER:
        raise ValueError("нет маркера CTOS-DATA-A7! в LBA%d+0x180 — "
                         "на флэшке нет данных для переноса" % DATA_LBA)
    cbase = CAT_LBA * SECTOR
    if flash[cbase:cbase + 8] != CAT_MAGIC:
        raise ValueError("нет CTOSCAT1 в LBA%d — каталог данных повреждён"
                         % CAT_LBA)
    version, count = struct.unpack_from("<II", flash, cbase + 8)
    if version != 1 or not (1 <= count <= 63):
        raise ValueError("каталог данных: version=%d count=%d" %
                         (version, count))

    sd = bytearray(flash)          # <<< всё: boot, data, CAT — один диск SD
    sd[MARKER_OFF:MARKER_OFF + 16] = TGT_MARKER
    if verbose:
        print("A12 MIGRATE: flash=%d Б -> sd=%d Б, md5 %s -> %s" %
              (len(flash), len(sd),
               hashlib.md5(bytes(flash)).hexdigest(),
               hashlib.md5(bytes(sd)).hexdigest()))
        print("  boot LBA0..135, data LBA%d..%d, CAT LBA%d" %
              (DATA_LBA, DATA_LBA + DATA_IMG_SECTORS - 1, CAT_LBA))
    return bytes(sd)


def main(argv):
    if len(argv) != 3:
        print("usage: python -X utf8 migrate_sd.py <flash.img> <sd.img>",
              file=sys.stderr)
        return 2
    src, dst = argv[1], argv[2]
    try:
        flash = io.open(src, "rb").read()
        sd = migrate(flash)
    except (OSError, ValueError) as e:
        print("A12 MIGRATE REFUSED: %s" % e, file=sys.stderr)
        return 1
    if os.path.abspath(src) == os.path.abspath(dst):
        print("A12 MIGRATE REFUSED: источник и цель — один файл",
              file=sys.stderr)
        return 2
    io.open(dst, "wb").write(sd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
