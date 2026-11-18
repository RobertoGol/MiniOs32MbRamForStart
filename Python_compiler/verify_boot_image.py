# -*- coding: utf-8 -*-
"""A4a: честная приёмка загрузчика и нативного рантайма CtOS в QEMU.

Проверяется ровно то, что реально исполняется:
  1. детерминированная сборка образа ДВАЖДЫ в разных TEMP-каталогах
     (свежий as/ld/gcc/objcopy каждый раз) — байты обязаны совпасть;
  2. positive: MBR -> EDD stage2 -> CTMD (CRC каталога) -> PM-рантайм,
     тот же native_rt.c что и на хосте, Event-линии COM1 байт-в-байт
     сверяются с хост-запуском `native_rt.exe --module memmgr`;
     isa-debug-exit даёт rc=39 (AX=0x13);
  3. негативы загрузчика: подмена магии CTMD и порча тела модуля дают
     честный отказ rc=35 (AX=0x11) без «PM OK»;
  4. негатив рантайма: порча тела memmgr с пересчётом CRC каталога
     проходит stage2, но `verify_code()` ловит брак внутреннего CRC и даёт
     rc=41 (AX=0x14).

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
import zlib
from collections import deque

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# В этой среде удаление файлов разрешено только в одобренном TEMP-дереве.
_APPROVED_TMP = r"G:\Windows\RJ\AppData\Local\Temp\opencode"
TMP_BASE = (os.environ.get("OPENCODE_TMP") or
            (_APPROVED_TMP if os.path.isdir(_APPROVED_TMP)
             else tempfile.gettempdir()))
BUILDER = os.path.join(REPO, "CtOs", "native", "boot", "build_boot_image.py")
BOOT_DIR = os.path.dirname(BUILDER)
HOST_SRC = os.path.join(REPO, "CtOs", "native", "native_rt.c")
HOST_EXE = os.path.join(tempfile.gettempdir(), "ctos_native_rt",
                        "native_rt.exe")

SECTOR = 512
CTMD_LBA = 8
CTMD_OFF = CTMD_LBA * SECTOR
PM_LBA = 72
PM_OFF = PM_LBA * SECTOR
IMAGE_LEN = 136 * SECTOR

EXPECT_MBR_LEN = 188
EXPECT_S2_LEN = 1720
EXPECT_INSTALL_LEN = 1188   # длина installer-секции без хвостовых нулей
EXPECT_CTMD_LEN = 28425
EXPECT_PM_LEN = 21220        # слот бинарника в образе
EXPECT_PM_TAIL_LEN = 21217   # последний ненулевой байт + 1 (3 нуля в .data)
EXPECT_CTMD_MD5 = "110b54e786544c561b64132e7557812d"
EXPECT_IMAGE_MD5 = "dc90a080710efb03b3ccbfe640cebb9e"
EXPECT_MODULES = ("memmgr", "sched", "syscall_test", "stage1")

# isa-debug-exit: (AX << 1) | 1
RC_OK = 39       # AX=0x13 — успех A4a
RC_REFUSE = 35   # AX=0x11 — отказ stage2
RC_FATAL = 41    # AX=0x14 — runtime-fatal

POS_PREAMBLE = [
    "CTOS A3b STAGE2",
    "CTMD count=00000004",
    "memmgr CRC OK",
    "sched CRC OK",
    "syscall_test CRC OK",
    "stage1 CRC OK",
    "CTMD ALL OK",
    "CTOS A3b PM OK",
    "CTOS A4a EXEC",
]

# Эталон host-запуска: эта же последовательность обязана прийти по COM1.
EXPECT_HOST_EVENTS = [
    "MODULE memmgr 1834 6434AADB",
    "PORT 3F0050C0 0000A701",
    "PORT 3F0050C0 0000A710",
    "PORT 3F0050C0 0000A721",
    "PORT 3F0050C0 0000A722",
    "PORT 3F0050C0 00000002",
    "PORT 3F0050C0 0000A731",
    "PORT 3F0050C0 0000A732",
    "PORT 3F0050C0 0000A733",
    "PORT 3F0050C0 00000001",
    "PORT 3F0050C0 0000A740",
    "PORT 3F0050C0 0000A792",
    "PORT 3F0050C0 0000A741",
    "PORT 3F0050C0 0000A7FF",
    "OPS 1395 CELLS 73",
]
POS_LINES = POS_PREAMBLE + EXPECT_HOST_EVENTS


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
    raise RuntimeError("A4a: qemu-system-i386 не найден (эмуляционная "
                       "контрольная точка недоступна)")


def host_exe():
    """Тот же host-интерпретатор, что и в verify_native_rt.py."""
    if (not os.path.exists(HOST_EXE) or
            os.path.getmtime(HOST_EXE) < os.path.getmtime(HOST_SRC)):
        os.makedirs(os.path.dirname(HOST_EXE), exist_ok=True)
        r = subprocess.run(
            ["gcc", "-O2", "-std=c11", "-Wall", "-Wextra",
             "-o", HOST_EXE, HOST_SRC],
            capture_output=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise RuntimeError("gcc host: %s %s" % (r.stdout, r.stderr))
    return HOST_EXE


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
        raise RuntimeError("A4a build %s: %s %s" %
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


def host_event_lines(ctmd, tmp_root, tag):
    """Event-лог хоста для того же CTMD; артефакт *.out чистим перед запуском."""
    d = os.path.join(tmp_root, "host_" + tag)
    os.makedirs(d, exist_ok=True)
    ctmd_path = os.path.join(d, "modules.ctmd")
    ev = os.path.join(d, "events.txt")
    clean(ctmd_path)
    clean(ev)
    for name in os.listdir(d):
        if name.endswith(".out"):
            clean(os.path.join(d, name))
    io.open(ctmd_path, "wb").write(ctmd)
    r = subprocess.run([host_exe(), "--module", "memmgr", ctmd_path, ev],
                       capture_output=True, encoding="utf-8",
                       errors="replace", timeout=60)
    if r.returncode:
        raise RuntimeError("host --module memmgr: %s %s" %
                           (r.stdout, r.stderr))
    text = io.open(ev, encoding="ascii").read()
    return [s.strip() for s in text.splitlines() if s.strip()]


def lines_of(raw):
    # QEMU пишет в начало COM1-файла мусорный байт 0x03 при сбросе UART.
    text = raw.decode("ascii", errors="replace").lstrip("\x03")
    return [s.strip() for s in text.replace("\r\n", "\n").split("\n") if s]


def show_lines(raw):
    return " | ".join(lines_of(raw))


def main():
    fails = []
    tmp_root = tempfile.mkdtemp(prefix="a4a_boot_verify_", dir=TMP_BASE)
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
        s2 = a[SECTOR:SECTOR + 4 * SECTOR]
        s2_len = len(s2.rstrip(b"\x00"))
        inst = a[5 * SECTOR:8 * SECTOR]
        inst_len = len(inst.rstrip(b"\x00"))
        ctmd = a[CTMD_OFF:CTMD_OFF + EXPECT_CTMD_LEN]
        pm = a[PM_OFF:PM_OFF + EXPECT_PM_LEN]
        pm_len = len(pm.rstrip(b"\x00"))
        print("layout: MBR<=%d(%d), stage2=%d(ожидалось %d), "
              "install=%d(ожидалось %d), "
              "CTMD=%d(ожидалось %d), PM=%d/%d(ожидалось %d/%d), CTMD md5 %s" %
              (SECTOR - 2, len(mbr.rstrip(b"\x00")),
               s2_len, EXPECT_S2_LEN, inst_len, EXPECT_INSTALL_LEN,
               len(ctmd), EXPECT_CTMD_LEN,
               pm_len, EXPECT_PM_LEN, EXPECT_PM_TAIL_LEN, EXPECT_PM_LEN,
               hashlib.md5(ctmd).hexdigest()))
        if s2_len != EXPECT_S2_LEN:
            fails.append("stage2 length %d" % s2_len)
        if inst_len != EXPECT_INSTALL_LEN:
            fails.append("install length %d" % inst_len)
        if a[0x180:0x18C] != b"\x00" * 12:
            fails.append("install marker in clean image")
        if pm_len != EXPECT_PM_TAIL_LEN:
            fails.append("PM length %d" % pm_len)
        if len(ctmd) != EXPECT_CTMD_LEN or \
                hashlib.md5(ctmd).hexdigest() != EXPECT_CTMD_MD5:
            fails.append("CTMD md5")
        if ctmd[:4] != b"CTMD" or struct.unpack_from("<I", ctmd, 8)[0] != 4:
            fails.append("CTMD header")
        names = [ctmd[12 + i * 48:12 + i * 48 + 32].split(b"\0", 1)[0].decode("ascii")
                 for i in range(4)]
        if tuple(names) != EXPECT_MODULES:
            fails.append("CTMD catalog %s" % names)

        # ---------- 2. эталон хоста ----------
        host = host_event_lines(ctmd, tmp_root, "etalon")
        host_ok = (host == EXPECT_HOST_EVENTS)
        print("host events: %d линий, %s" %
              (len(host), "OK" if host_ok else "FAIL"))
        if not host_ok:
            print("  HOST:", " | ".join(host))
            fails.append("host events")

        # ---------- 3. positive: QEMU -> rc=39 + COM1 == host ----------
        rc, raw, err = boot_log(a, tmp_root, "pos")
        got = lines_of(raw)
        tail = got[len(POS_PREAMBLE):] if got[:len(POS_PREAMBLE)] == POS_PREAMBLE else got
        pos_ok = (rc == RC_OK and got == POS_LINES and
                  tail == host and not err)
        print("positive: rc=%s ожидалось=%d lines=%d, COM1==host=%s  %s" %
              (rc, RC_OK, len(got), tail == host, "OK" if pos_ok else "FAIL"))
        if not pos_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("positive")

        # ---------- 4. negative: подмена магии CTMD -> rc=35 ----------
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

        # ---------- 5. negative: порча тела модуля -> rc=35 ----------
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

        # ---------- 6. negative: CRC каталога исправлен, брак внутри .ctos ----------
        # stage2 видит корректный CTMD CRC и пускает PM, но verify_code()
        # ловит несовпадение внутреннего CRC v1.1 -> exit(1) -> AX=0x14.
        off0, len0 = struct.unpack_from("<II", ctmd, 12 + 32)
        bad_fatal = bytearray(a)
        bad_fatal[CTMD_OFF + off0 + 40] ^= 0x5A
        body = bytes(bad_fatal[CTMD_OFF + off0:CTMD_OFF + off0 + len0])
        newcrc = zlib.crc32(body) & 0xFFFFFFFF
        struct.pack_into("<I", bad_fatal, CTMD_OFF + 12 + 40, newcrc)
        rc, raw, err = boot_log(bytes(bad_fatal), tmp_root, "fatal")
        got = lines_of(raw)
        fatal_ok = (rc == RC_FATAL and
                    b"FATAL: [TKT-040]" in raw and
                    "CTMD ALL OK" in got and "CTOS A4a EXEC" in got and
                    not any(s.startswith("OPS ") for s in got))
        print("neg runtime-fatal: rc=%s diag=%s  %s" %
              (rc, b"FATAL: [TKT-040]" in raw,
               "OK" if fatal_ok else "FAIL"))
        if not fatal_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("neg runtime-fatal")
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("")
    if fails:
        print("BOOT IMAGE FAIL:", ", ".join(fails))
        print("Эмуляционная контрольная точка НЕ пройдена; на железе не заявляется.")
        return 1
    print("BOOT IMAGE OK A4a: детерминированный образ, QEMU rc=39, COM1 "
          "байт-в-байт совпадает с host native_rt, два отказа rc=35 и "
          "runtime-fatal rc=41. QEMU — контрольная точка, на R3700 НЕ принято.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
