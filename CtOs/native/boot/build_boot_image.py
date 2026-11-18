# -*- coding: utf-8 -*-
"""A3b: детерминированный сборщик legacy-BIOS образа CtOS (сырой диск).

Раскладка секторов (512 Б каждый):
  LBA 0      MBR: 16-битный код + сигнатура 55 AA
  LBA 1..4   stage2: 4 сектора, загружается в 0x1000:0000
  LBA 5..7   зарезервированная пустота
  LBA 8..71  CTMD v1: 64 сектора, загружается в 0x2000:0000
  ...        нулевое заполнение до 128 секторов

Образ `*.img` и промежуточные `*.bin` не отслеживаются VCS: builder
воспроизводит их по требованию из исходников `mbr.S`/`stage2.S` и CTMD.
"""
import hashlib
import io
import os
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NATIVE = os.path.dirname(HERE)
if NATIVE not in sys.path:
    sys.path.insert(0, NATIVE)
import build_modules_image as ctmd_builder  # noqa: E402

SECTOR = 512
MBR_LBA = 0
STAGE2_LBA = 1
STAGE2_SECTORS = 4
CTMD_LBA = 8
CTMD_SECTORS = 64
TOTAL_SECTORS = 128


def tool(name):
    p = shutil.which(name)
    if not p:
        raise SystemExit("A3b: не найден инструмент %s в PATH" % name)
    return p


def flat_binary(src, ldscript, base, obj, exe, out):
    as_p, ld_p, cp_p = tool("as"), tool("ld"), tool("objcopy")
    subprocess.run([as_p, "--32", "-o", obj, src], check=True)
    subprocess.run([ld_p, "-m", "i386pe", "--image-base=0x%X" % base,
                    "-T", ldscript, "-o", exe, obj], check=True)
    subprocess.run([cp_p, "-O", "binary", "--only-section=.text", exe, out],
                   check=True)
    return io.open(out, "rb").read()


def build(out_path, tmp=None):
    # Внешний верификатор передаёт свой TEMP-каталог; по умолчанию — рядом.
    if tmp is None:
        tmp = os.path.join(HERE, "_build_tmp")
    os.makedirs(tmp, exist_ok=True)
    base = "a3b"

    mbr = flat_binary(os.path.join(HERE, "mbr.S"),
                      os.path.join(HERE, "mbr.ld"), 0x7C00,
                      os.path.join(tmp, base + "_mbr.o"),
                      os.path.join(tmp, base + "_mbr.exe"),
                      os.path.join(tmp, base + "_mbr.bin"))
    if len(mbr) > SECTOR - 2:
        raise SystemExit("A3b: MBR не помещается: %d Б" % len(mbr))
    stage2 = flat_binary(os.path.join(HERE, "stage2.S"),
                         os.path.join(HERE, "stage2.ld"), 0,
                         os.path.join(tmp, base + "_s2.o"),
                         os.path.join(tmp, base + "_s2.exe"),
                         os.path.join(tmp, base + "_s2.bin"))
    if len(stage2) > STAGE2_SECTORS * SECTOR:
        raise SystemExit("A3b: stage2 не помещается: %d Б" % len(stage2))

    ctmd_path = os.path.join(tmp, base + "_modules.ctmd")
    ctmd = ctmd_builder.build(ctmd_path)
    ctmd_builder.verify(ctmd)
    if len(ctmd) > CTMD_SECTORS * SECTOR:
        raise SystemExit("A3b: CTMD не помещается: %d Б" % len(ctmd))

    img = bytearray(TOTAL_SECTORS * SECTOR)
    # MBR
    img[:len(mbr)] = mbr
    struct.pack_into("<H", img, SECTOR - 2, 0xAA55)
    # stage2
    s2off = STAGE2_LBA * SECTOR
    img[s2off:s2off + len(stage2)] = stage2
    # CTMD
    coff = CTMD_LBA * SECTOR
    img[coff:coff + len(ctmd)] = ctmd

    io.open(out_path, "wb").write(img)
    for p in (os.path.join(tmp, base + "_mbr.o"),
              os.path.join(tmp, base + "_mbr.exe"),
              os.path.join(tmp, base + "_s2.o"),
              os.path.join(tmp, base + "_s2.exe")):
        if os.path.exists(p):
            os.remove(p)
    return {
        "image": bytes(img),
        "mbr": mbr,
        "stage2": stage2,
        "ctmd": ctmd,
        "path": out_path,
    }


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(HERE, "ctos_boot.img")
    tmp = sys.argv[2] if len(sys.argv) > 2 else None
    r = build(out, tmp)
    print("A3b BOOT OK: %s — %d Б, md5 %s" %
          (out, len(r["image"]),
           hashlib.md5(r["image"]).hexdigest()))
    print("  MBR=%d Б, stage2=%d Б, CTMD=%d Б; LBA: 0/%d..%d/8..%d" %
          (len(r["mbr"]), len(r["stage2"]), len(r["ctmd"]),
           STAGE2_LBA, STAGE2_LBA + STAGE2_SECTORS - 1,
           CTMD_LBA + CTMD_SECTORS - 1))
