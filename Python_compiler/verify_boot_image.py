# -*- coding: utf-8 -*-
"""A3b: честная приёмка legacy-BIOS загрузчика CtOS в эмуляции QEMU.

Проверяется ровно то, что реально исполняется:
  1. детерминированная сборка образа ДВАЖДЫ в разных TEMP-каталогах
     (свежий as/ld/objcopy каждый раз) — байты обязаны совпасть;
  2. positive: QEMU грузит MBR -> stage2 -> CTMD -> защищённый режим,
     isa-debug-exit даёт rc=33 (AX=0x10), COM1-лог полный;
  3. negative: подмена магии CTMD и порча тела модуля дают честный
     отказ rc=35 (AX=0x11) с диагностикой в логе, без «PM OK».

Это ЭМУЛЯЦИОННАЯ контрольная точка. «Заработало на железе» НЕ заявляется:
доступа к Acer Aspire Revo R3700 нет, QEMU — не замена приёмки на моноблоке.

Запуск (только так):
    python -X utf8 Python_compiler/verify_boot_image.py
"""
import hashlib
import io
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from collections import deque

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# В этой среде удаление файлов разрешено только в одобренном TEMP-дереве.
_APPROVED_TMP = r"G:\Windows\RJ\AppData\Local\Temp\opencode"
TMP_BASE = (os.environ.get("OPENCODE_TMP") or
            (_APPROVED_TMP if os.path.isdir(_APPROVED_TMP)
             else tempfile.gettempdir()))
BUILDER = os.path.join(REPO, "CtOs", "native", "boot", "build_boot_image.py")
BOOT_DIR = os.path.dirname(BUILDER)

SECTOR = 512
CTMD_LBA = 8
CTMD_OFF = CTMD_LBA * SECTOR
IMAGE_LEN = 64 * 1024

EXPECT_MBR_LEN = 188
EXPECT_S2_LEN = 1056
EXPECT_CTMD_LEN = 28425
EXPECT_CTMD_MD5 = "110b54e786544c561b64132e7557812d"
EXPECT_IMAGE_MD5 = "2b8847fc192c3c7595e9240d9091730a"
EXPECT_MODULES = ("memmgr", "sched", "syscall_test", "stage1")

RC_OK = 33       # isa-debug-exit: (AX=0x10 << 1) | 1
RC_REFUSE = 35   # isa-debug-exit: (AX=0x11 << 1) | 1

POS_LINES = [
    "CTOS A3b STAGE2",
    "CTMD count=00000004",
    "memmgr CRC OK",
    "sched CRC OK",
    "syscall_test CRC OK",
    "stage1 CRC OK",
    "CTMD ALL OK",
    "CTOS A3b PM OK",
]


def clean(p):
    if os.path.exists(p):
        os.remove(p)


def qemu():
    p = shutil.which("qemu-system-i386")
    if p:
        return p
    for c in (r"C:\Program Files\qemu\qemu-system-i386.exe",
              r"C:\Program Files (x86)\qemu\qemu-system-i386.exe"):
        if os.path.exists(c):
            return c
    raise RuntimeError("A3b: qemu-system-i386 не найден (эмуляционная "
                       "контрольная точка недоступна)")


def cold_build(tag, tmp_root):
    """Свежая сборка из исходников в отдельном TEMP; .img не переживает запуск."""
    d = os.path.join(tmp_root, "build_" + tag)
    os.makedirs(d, exist_ok=True)
    img = os.path.join(d, "ctos_boot.img")
    clean(img)
    r = subprocess.run(
        [sys.executable, "-X", "utf8", BUILDER, img, d],
        capture_output=True, encoding="utf-8", errors="replace", timeout=300)
    if r.returncode:
        raise RuntimeError("A3b build %s: %s %s" %
                           (tag, r.stdout[-500:], r.stderr[-500:]))
    data = io.open(img, "rb").read()
    return data, r.stdout, d


def boot_log(data, tmp_root, tag):
    """Один прогон QEMU; лог удаляется перед каждым запуском (cold)."""
    d = os.path.join(tmp_root, "run_" + tag)
    os.makedirs(d, exist_ok=True)
    img = os.path.join(d, "ctos_boot.img")
    # ВАЖНО: «com1.log» на Windows — зарезервированное имя устройства COM1.
    log = os.path.join(d, "serial.log")
    clean(img)
    clean(log)
    io.open(img, "wb").write(data)
    cmd = [qemu(),
           "-machine", "pc",
           "-drive", "file=" + img + ",format=raw,if=ide,index=0,media=disk",
           "-boot", "order=c",
           "-display", "none",
           "-serial", "file:" + log,
           "-monitor", "none",
           "-no-reboot",
           "-device", "isa-debug-exit,iobase=0xf4,iosize=0x4",
           "-net", "none"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None, b"", "QEMU TIMEOUT"
    raw = io.open(log, "rb").read() if os.path.exists(log) else b""
    return r.returncode, raw, ""


def lines_of(raw):
    # QEMU пишет в начало COM1-файла мусорный байт 0x03 при сбросе UART.
    text = raw.decode("ascii", errors="replace").lstrip("\x03")
    return [s.strip() for s in text.replace("\r\n", "\n").split("\n") if s]


def show_lines(raw):
    return " | ".join(lines_of(raw))


def main():
    fails = []
    tmp_root = tempfile.mkdtemp(prefix="a3b_boot_verify_", dir=TMP_BASE)
    try:
        # ---------- 1. холодная детерминированная сборка ----------
        images = deque(maxlen=2)
        builds = []
        for tag in ("1", "2"):
            data, out, d = cold_build(tag, tmp_root)
            images.append(data)
            builds.append(out)
            print("build %s: %s" % (tag, out.strip().splitlines()[-1]))
        a, b = images[0], images[1]
        same = (a == b)
        print("deque cold x2: %s, md5 %s/%s  %s" %
              (len(a), hashlib.md5(a).hexdigest(),
               hashlib.md5(b).hexdigest(), "IDENTICAL" if same else "DIFF"))
        if not same:
            fails.append("determinism")
        if len(a) != IMAGE_LEN:
            fails.append("image length %d" % len(a))
        if hashlib.md5(a).hexdigest() != EXPECT_IMAGE_MD5:
            fails.append("image md5")
        if struct.unpack_from("<H", a, SECTOR - 2)[0] != 0xAA55:
            fails.append("MBR signature")
        mbr = a[0:SECTOR]
        s2 = a[SECTOR:CTMD_OFF]
        s2_len = len(s2.rstrip(b"\x00"))
        ctmd = a[CTMD_OFF:CTMD_OFF + EXPECT_CTMD_LEN]
        print("layout: MBR<=510, stage2=%d(ожидалось %d), CTMD=%d(ожидалось %d), md5 %s" %
              (s2_len, EXPECT_S2_LEN, len(ctmd), EXPECT_CTMD_LEN,
               hashlib.md5(ctmd).hexdigest()))
        if s2_len != EXPECT_S2_LEN:
            fails.append("stage2 length %d" % s2_len)
        if len(ctmd) != EXPECT_CTMD_LEN or \
                hashlib.md5(ctmd).hexdigest() != EXPECT_CTMD_MD5:
            fails.append("CTMD md5")
        if ctmd[:4] != b"CTMD" or struct.unpack_from("<I", ctmd, 8)[0] != 4:
            fails.append("CTMD header")
        names = [ctmd[12 + i * 48:12 + i * 48 + 32].split(b"\0", 1)[0].decode("ascii")
                 for i in range(4)]
        if tuple(names) != EXPECT_MODULES:
            fails.append("CTMD catalog %s" % names)

        # ---------- 2. positive: QEMU -> rc=33 + PM OK ----------
        rc, raw, err = boot_log(a, tmp_root, "pos")
        got = lines_of(raw)
        pos_ok = (rc == RC_OK and got == POS_LINES and not err)
        print("positive: rc=%s ожидалось=%d lines=%d  %s" %
              (rc, RC_OK, len(got), "OK" if pos_ok else "FAIL"))
        if not pos_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("positive")

        # ---------- 3. negative: подмена магии CTMD -> rc=35 ----------
        bad_magic = bytearray(a)
        bad_magic[CTMD_OFF:CTMD_OFF + 4] = b"XXXX"
        rc, raw, err = boot_log(bytes(bad_magic), tmp_root, "magic")
        got = lines_of(raw)
        magic_ok = (rc == RC_REFUSE and "CTMD magic FAIL" in got and
                    "CTMD ALL OK" not in got and "PM OK" not in got)
        print("neg magic: rc=%s diag=%s  %s" %
              (rc, "CTMD magic FAIL" in got, "OK" if magic_ok else "FAIL"))
        if not magic_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("neg magic")

        # ---------- 4. negative: порча тела модуля -> rc=35 ----------
        bad_crc = bytearray(a)
        off0 = struct.unpack_from("<I", ctmd, 12 + 32)[0]  # запись memmgr
        bad_crc[CTMD_OFF + off0 + 10] ^= 0x5A
        rc, raw, err = boot_log(bytes(bad_crc), tmp_root, "crc")
        got = lines_of(raw)
        crc_ok = (rc == RC_REFUSE and any("CRC FAIL" in s for s in got) and
                  "CTMD FAIL" in got and "CTMD ALL OK" not in got and
                  "PM OK" not in got)
        print("neg CRC: rc=%s diag=%s  %s" %
              (rc, any("CRC FAIL" in s for s in got),
               "OK" if crc_ok else "FAIL"))
        if not crc_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("neg CRC")
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("")
    if fails:
        print("BOOT IMAGE FAIL:", ", ".join(fails))
        print("Эмуляционная контрольная точка НЕ пройдена; на железе не заявляется.")
        return 1
    print("BOOT IMAGE OK A3b: детерминированный образ, QEMU rc=33 c "
          "CTOS A3b PM OK, два честных отказа rc=35. "
          "QEMU — контрольная точка, на R3700 НЕ принято.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
