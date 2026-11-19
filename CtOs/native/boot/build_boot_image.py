# -*- coding: utf-8 -*-
"""A5: детерминированный сборщик legacy-BIOS образа CtOS (сырой диск).

Раскладка секторов (512 Б каждый):
  LBA 0      MBR: 16-битный код + сигнатура 55 AA
  LBA 1..4   stage2: 4 сектора, загружается в 0x1000:0000
  LBA 5..7   A5: 16-битный установщик, загружается в 0x5000:0000
  LBA 8..71  CTMD v1: 64 сектора, загружается в 0x2000:0000
  LBA 72..135 A4a: плоский 32-битный рантайм, загружается в 0x4000:0000
  LBA 136    зарезервировано под sentinel закрепления (в образ НЕ входит)

Установщик вызывается stage2 только при маркере CTOS-INST-A5 в LBA0+0x180;
без маркера он молча возвращается, и поведение совпадает с A4a.

BSS рантайма не занимает место в образе: pm_start.S обнуляет его по линкерным
символам `_bss_start`/`_bss_end` (BSS лежит по 0x01000000, вдали от стека
0x90000 и VGA 0xB8000).

Образ `*.img` и промежуточные `*.bin` не отслеживаются VCS: builder
воспроизводит их по требованию из исходников и CTMD.
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
INSTALL_LBA = 5
INSTALL_SECTORS = 3
CTMD_LBA = 8
CTMD_SECTORS = 64
CTMD_PHYS = 0x00020000
PM_LBA = 72
PM_SECTORS = 64
TOTAL_SECTORS = PM_LBA + PM_SECTORS

PM_BASE = 0x00040000
PM_BSS_BASE = 0x01000000
PM_CTMD_PHYS = CTMD_PHYS


def tool(name):
    p = shutil.which(name)
    if not p:
        raise SystemExit("A4a: не найден инструмент %s в PATH" % name)
    return p


def flat_binary(src, ldscript, base, obj, exe, out, defines=None):
    as_p, ld_p, cp_p = tool("as"), tool("ld"), tool("objcopy")
    as_cmd = [as_p, "--32"]
    for d in (defines or []):
        as_cmd += ["--defsym", d]   # GAS: .if NAME, не cpp-макрос
    subprocess.run(as_cmd + ["-o", obj, src], check=True)
    subprocess.run([ld_p, "-m", "i386pe", "--image-base=0x%X" % base,
                    "-T", ldscript, "-o", exe, obj], check=True)
    subprocess.run([cp_p, "-O", "binary", "--only-section=.text", exe, out],
                   check=True)
    return io.open(out, "rb").read()


def pm_flags(include_dir):
    return ["-m32", "-O2", "-std=c11", "-ffreestanding", "-fno-builtin",
            "-fno-stack-protector", "-fno-pic", "-fno-common", "-nostdinc",
            "-mno-mmx", "-mno-sse", "-mno-sse2", "-I", include_dir,
            "-DPM_CTMD_PHYS=0x%08Xu" % PM_CTMD_PHYS]


def pm_binary(tmp, name_mode=False, tag="a4a"):
    """Тот же native_rt.c без правок семантики + freestanding-shim.

    A14: name_mode=True включает аддитивный выбор модуля по имени через
    GAS --defsym / -D только в pm_start.S и shim.c. При False собирается
    байт-в-байт прежний PM (gate A4a/A12/A13 не должен измениться).
    """
    gcc_p, as_p, ld_p, cp_p = (tool("gcc"), tool("as"), tool("ld"),
                               tool("objcopy"))
    pm_dir = os.path.join(HERE, "pm")
    inc = os.path.join(pm_dir, "include")
    src = os.path.join(NATIVE, "native_rt.c")
    shim = os.path.join(pm_dir, "shim.c")
    start = os.path.join(pm_dir, "pm_start.S")
    lds = os.path.join(pm_dir, "pm.ld")
    flags = pm_flags(inc)

    obj_rt = os.path.join(tmp, tag + "_native_rt.o")
    obj_shim = os.path.join(tmp, tag + "_shim.o")
    obj_start = os.path.join(tmp, tag + "_start.o")
    exe = os.path.join(tmp, tag + "_pm.exe")
    out = os.path.join(tmp, tag + "_pm.bin")

    shim_flags = flags + ["-DA14_NAME=%d" % (1 if name_mode else 0)]
    start_defs = ["A14_NAME=%d" % (1 if name_mode else 0)]
    subprocess.run([gcc_p] + flags + ["-c", "-o", obj_rt, src], check=True)
    subprocess.run([gcc_p] + shim_flags + ["-c", "-o", obj_shim, shim],
                   check=True)
    subprocess.run([as_p, "--32"] +
                   sum([["--defsym", d] for d in start_defs], []) +
                   ["-o", obj_start, start], check=True)
    subprocess.run([ld_p, "-m", "i386pe", "--image-base=0",
                    "-e", "_start", "-T", lds, "-o", exe,
                    obj_start, obj_rt, obj_shim], check=True)
    subprocess.run([cp_p, "-O", "binary",
                    "--only-section=.text", "--only-section=.rdata",
                    "--only-section=.data", exe, out], check=True)

    undef = subprocess.run([tool("nm"), "-u", exe], check=True,
                           capture_output=True, text=True).stdout.strip()
    if undef:
        raise SystemExit("A4a: неразрешённые символы в PM-рантайме:\n%s" % undef)

    data = io.open(out, "rb").read()
    if len(data) > PM_SECTORS * SECTOR:
        raise SystemExit("A4a: PM-рантайм не помещается: %d Б" % len(data))
    for p in (obj_rt, obj_shim, obj_start, exe):
        if os.path.exists(p):
            os.remove(p)
    return data


def build(out_path, tmp=None, profile="default"):
    # Внешний верификатор передаёт свой TEMP-каталог; по умолчанию — рядом.
    if tmp is None:
        tmp = os.path.join(HERE, "_build_tmp")
    if profile not in ("default", "combined", "name", "name_sep"):
        raise SystemExit("A14: неизвестный профиль сборки %r" % profile)
    os.makedirs(tmp, exist_ok=True)
    base = "a14sep" if profile == "name_sep" else \
           ("a14" if profile == "name" else \
            ("a12" if profile == "combined" else "a3b"))

    mbr = flat_binary(os.path.join(HERE, "mbr.S"),
                      os.path.join(HERE, "mbr.ld"), 0x7C00,
                      os.path.join(tmp, base + "_mbr.o"),
                      os.path.join(tmp, base + "_mbr.exe"),
                      os.path.join(tmp, base + "_mbr.bin"))
    if len(mbr) > SECTOR - 2:
        raise SystemExit("A3b: MBR не помещается: %d Б" % len(mbr))
    # A12: combined-профиль меняет только stage2 (два DAP-смещения и режим
    # сканирования). A14 `name` использует тот же single-SD stage2 и дополнительно
    # включает name-ветку в PM; `name_sep` — name-ветка PM, но дефолтное
    # сканирование отдельного диска данных (как A7/A8). MBR/установщик/CTMD
    # собираются из тех же исходников.
    s2_defines = ["A12_COMBINED=%d" %
                  (1 if profile in ("combined", "name") else 0)]
    stage2 = flat_binary(os.path.join(HERE, "stage2.S"),
                         os.path.join(HERE, "stage2.ld"), 0,
                         os.path.join(tmp, base + "_s2.o"),
                         os.path.join(tmp, base + "_s2.exe"),
                         os.path.join(tmp, base + "_s2.bin"),
                         defines=s2_defines)
    if len(stage2) > STAGE2_SECTORS * SECTOR:
        raise SystemExit("A3b: stage2 не помещается: %d Б" % len(stage2))
    install = flat_binary(os.path.join(HERE, "install.S"),
                          os.path.join(HERE, "stage2.ld"), 0,
                          os.path.join(tmp, base + "_inst.o"),
                          os.path.join(tmp, base + "_inst.exe"),
                          os.path.join(tmp, base + "_inst.bin"))
    if len(install) > INSTALL_SECTORS * SECTOR:
        raise SystemExit("A5: установщик не помещается: %d Б" % len(install))

    ctmd_path = os.path.join(tmp, base + "_modules.ctmd")
    ctmd = ctmd_builder.build(ctmd_path)
    ctmd_builder.verify(ctmd)
    if len(ctmd) > CTMD_SECTORS * SECTOR:
        raise SystemExit("A3b: CTMD не помещается: %d Б" % len(ctmd))
    if PM_CTMD_PHYS != CTMD_PHYS:
        raise SystemExit("A4a: PM_CTMD_PHYS не совпадает с загрузкой CTMD")

    pm = pm_binary(tmp, name_mode=(profile in ("name", "name_sep")),
                   tag=base + "_pm")

    img = bytearray(TOTAL_SECTORS * SECTOR)
    img[:len(mbr)] = mbr
    struct.pack_into("<H", img, SECTOR - 2, 0xAA55)
    s2off = STAGE2_LBA * SECTOR
    img[s2off:s2off + len(stage2)] = stage2
    ioff = INSTALL_LBA * SECTOR
    img[ioff:ioff + len(install)] = install
    coff = CTMD_LBA * SECTOR
    img[coff:coff + len(ctmd)] = ctmd
    poff = PM_LBA * SECTOR
    img[poff:poff + len(pm)] = pm

    io.open(out_path, "wb").write(img)
    for p in (os.path.join(tmp, base + "_mbr.o"),
              os.path.join(tmp, base + "_mbr.exe"),
              os.path.join(tmp, base + "_s2.o"),
              os.path.join(tmp, base + "_s2.exe"),
              os.path.join(tmp, base + "_inst.o"),
              os.path.join(tmp, base + "_inst.exe")):
        if os.path.exists(p):
            os.remove(p)
    return {
        "image": bytes(img),
        "mbr": mbr,
        "stage2": stage2,
        "install": install,
        "ctmd": ctmd,
        "pm": pm,
        "path": out_path,
    }


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(HERE, "ctos_boot.img")
    tmp = sys.argv[2] if len(sys.argv) > 2 else None
    profile = sys.argv[3] if len(sys.argv) > 3 else "default"
    r = build(out, tmp, profile)
    print("A5 BOOT OK [%s]: %s — %d Б, md5 %s" %
          (profile, out, len(r["image"]),
           hashlib.md5(r["image"]).hexdigest()))
    print("  MBR=%d Б, stage2=%d Б, install=%d Б, CTMD=%d Б, PM=%d Б; "
          "LBA: 0/1..%d/%d..%d/8..%d/%d..%d" %
          (len(r["mbr"]), len(r["stage2"]), len(r["install"]),
           len(r["ctmd"]), len(r["pm"]),
           STAGE2_LBA + STAGE2_SECTORS - 1,
           INSTALL_LBA, INSTALL_LBA + INSTALL_SECTORS - 1,
           CTMD_LBA + CTMD_SECTORS - 1,
           PM_LBA, PM_LBA + PM_SECTORS - 1))
