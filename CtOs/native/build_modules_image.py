# -*- coding: utf-8 -*-
"""A3: сборщик контейнера модулей ядра CTMD v1 (детерминированный).

Формат (все числа LE):
  [0..4)    магия 'CTMD'
  [4..8)    версия = 1
  [8..12)   число модулей
  [12..]    каталог, по 48 Б на модуль:
              [0..32)   имя, ASCIIZ с нулевым заполнением
              [32..36)  смещение тела от начала файла
              [36..40)  длина тела
              [40..44)  CRC-32 тела (zlib, тот же что в .ctos v1.1)
              [44..48)  зарезервировано = 0
  тела модулей подряд, каждое выровнено по 16 Б нулями.

Запуск:
  python -X utf8 CtOs/native/build_modules_image.py [out.ctmd]
"""
import hashlib
import io
import os
import struct
import sys
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUT = os.path.join(REPO, "CtOs", "native", "kernel_modules.ctmd")

MODULES = [
    ("memmgr",       "CtOs/memmgr.ctos"),
    ("sched",        "CtOs/kernel_sched.ctos"),
    ("syscall_test", "Python_compiler/syscall_test.ctos"),
    ("stage1",       "Compiler/stage1_compiler.ctos"),
]

MAGIC = b"CTMD"
VERSION = 1
ENTSZ = 48
NAMESZ = 32


def build(out_path):
    entries = []
    body = bytearray()
    for name, rel in MODULES:
        path = os.path.join(REPO, rel)
        data = io.open(path, "rb").read()
        if len(name) > NAMESZ - 1:
            raise SystemExit("имя модуля слишком длинное: %s" % name)
        while len(body) % 16:
            body.append(0)
        off = 12 + ENTSZ * len(MODULES) + len(body)
        crc = zlib.crc32(data) & 0xFFFFFFFF
        rec = bytearray(ENTSZ)
        rec[:len(name)] = name.encode("ascii")
        struct.pack_into("<III", rec, NAMESZ, off, len(data), crc)
        entries.append(bytes(rec))
        body.extend(data)
    img = bytearray(MAGIC)
    img.extend(struct.pack("<II", VERSION, len(MODULES)))
    for rec in entries:
        img.extend(rec)
    img.extend(body)
    io.open(out_path, "wb").write(img)
    return bytes(img)


def verify(img):
    """Честная самопроверка каталога: границы, CRC, уникальность имён."""
    if img[:4] != MAGIC:
        raise SystemExit("CTMD: нет магии")
    ver, count = struct.unpack_from("<II", img, 4)
    if ver != VERSION:
        raise SystemExit("CTMD: версия %d != %d" % (ver, VERSION))
    seen = set()
    for i in range(count):
        e = img[12 + i * ENTSZ: 12 + (i + 1) * ENTSZ]
        name = e[:NAMESZ].split(b"\0", 1)[0].decode("ascii")
        off, ln, crc = struct.unpack_from("<III", e, NAMESZ)
        if name in seen:
            raise SystemExit("CTMD: дубль имени %s" % name)
        seen.add(name)
        if off + ln > len(img):
            raise SystemExit("CTMD: %s выходит за файл" % name)
        got = zlib.crc32(img[off:off + ln]) & 0xFFFFFFFF
        if got != crc:
            raise SystemExit("CTMD: %s CRC 0x%08X != 0x%08X" % (name, got, crc))
        print("  %-14s off=%-7d len=%-6d crc=0x%08X" % (name, off, ln, crc))
    return seen


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    img = build(out)
    seen = verify(img)
    print("CTMD OK: %s — %d Б, md5 %s, модулей %d" %
          (out, len(img), hashlib.md5(img).hexdigest(), len(seen)))
