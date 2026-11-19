# -*- coding: utf-8 -*-
"""A5: честная приёмка самоадаптивной установки CtOS в QEMU (два raw-диска).

Проверяется ровно то, что реально исполняется:
  1. холодная детерминированная сборка дважды в разных TEMP;
  2. источник с CTOS-INST-A5 находит диск с CTOS-TGT-A5, копирует 136 секторов
     с перечиткой, ставит ACTIVE, снимает оба маркера, затирает LBA5..7 и
     пишет sentinel (магия/версия/размер/CRC32-сумма/флаги) в LBA136;
     A9: дополнительно пишет в MBR цели маркер CTOS-AUTORUN-A6, чтобы сразу
     после установки запускались ВСЕ написанные модули, а не только memmgr;
  3. перезагрузка с цели: rc=39, COM1 байт-в-байт = четырём host-запускам
     (A6-автозапуск) и НИ ОДНОЙ строки A5 — установщик самоудалился;
  4. негатив: маркер источника есть, цели нет -> AL=2 -> rc=37, «REFUSED»,
     без «CTMD ALL OK» и без «PM OK»;
  5. A5b: перезагрузка с закреплённой цели сама проверяет sentinel. Подмена
     любого из 136 секторов образа или любого поля sentinel (магия, версия,
     размер, флаги, контрольная сумма), а также стёртый sentinel — честный
     rc=35 с «CTOS A5 PIN FAIL», без «CTMD ALL OK» и без «PM OK».

QEMU — только локальная эмуляционная контрольная точка. На R3700 НЕ заявляется.
Запуск только: python -X utf8 Python_compiler/verify_a5_install.py
"""
import hashlib
import io
import os
import shutil
import struct
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(REPO, "Python_compiler")
if PY not in sys.path:
    sys.path.insert(0, PY)
import verify_boot_image as a4  # noqa: E402

SECTOR = 512
MARKER_OFF = 0x180
AUTORUN_OFF = 0x190
ACTIVE_OFF = 0x1BE
AUTORUN_MARKER = b"CTOS-AUTORUN-A6\x00"
SRC_MARKER = b"CTOS-INST-A5\x00\x00\x00\x00"
TGT_MARKER = b"CTOS-TGT-A5!\x00\x00\x00\x00"
LOCK_MARKER = b"CTOS-LOCK-A5\x00\x00\x00\x00"
IMAGE_SECTORS = 136
INSTALL_LBA = 5
INSTALL_SECTORS = 3
SENTINEL_LBA = 136
TARGET_SECTORS = IMAGE_SECTORS + 4

RC_OK = 39
RC_INSTALL_REFUSE = 37          # AX=0x12
RC_PIN_REFUSE = 35              # AX=0x11: честный отказ закреплённой системы

A5_LINES = [
    "CTOS A5 INSTALL: START",
    "CTOS A5 TARGET 0x81",
    "CTOS A5 WRITE OK",
    "CTOS A5 SELF-DELETE OK",
    "CTOS A5 PIN OK",
    "CTOS A5 INSTALL OK",
    "CTOS A5 AUTORUN ALL",
]


def boot(disks, tmp_root, tag):
    """Первый диск загружается (IDE index=0), остальные подключены как data."""
    d = os.path.join(tmp_root, "run_" + tag)
    os.makedirs(d, exist_ok=True)
    log = os.path.join(d, "serial.log")
    a4.clean(log)
    paths = []
    for i, data in enumerate(disks):
        p = os.path.join(d, "disk%d.img" % i)
        a4.clean(p)
        io.open(p, "wb").write(data)
        paths.append(p)
    cmd = [a4.qemu(), "-machine", "pc"]
    for i, p in enumerate(paths):
        cmd += ["-drive", "file=%s,format=raw,if=ide,index=%d,media=disk" %
                (p, i)]
    cmd += ["-boot", "order=c",
            "-display", "none",
            "-serial", "file:" + log,
            "-monitor", "none",
            "-no-reboot",
            "-device", "isa-debug-exit,iobase=0xf4,iosize=0x4",
            "-net", "none"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        err = ""
    except subprocess.TimeoutExpired:
        return None, b"", "QEMU TIMEOUT", [bytes(len(d)) for d in disks]
    raw = io.open(log, "rb").read() if os.path.exists(log) else b""
    after = [io.open(p, "rb").read() for p in paths]
    return r.returncode, raw, err, after


def check(name, cond, fails):
    print("  %-28s %s" % (name, "OK" if cond else "FAIL"))
    if not cond:
        fails.append(name)


def pin_negative(name, disk, tmp_root, tag):
    """A5b: закреплённая система обязана отказать до перехода в PM."""
    rc, raw, err, _ = boot([disk], tmp_root, tag)
    got = a4.lines_of(raw)
    ok = (rc == RC_PIN_REFUSE and
          "CTOS A5 PIN FAIL" in got and
          "CTMD ALL OK" not in got and "PM OK" not in got and
          "CTOS A5 INSTALL OK" not in got and
          not err)
    print("neg %-24s rc=%s  %s" % (name, rc, "OK" if ok else "FAIL"))
    if not ok:
        print("  LOG:", " | ".join(got))
        if err:
            print("  ERR:", err)
    return ok


def main():
    fails = []
    tmp_root = tempfile.mkdtemp(prefix="a5_install_verify_", dir=a4.TMP_BASE)
    try:
        # ---------- 1. холодная детерминированная сборка ----------
        a_img, _, _ = a4.cold_build("a5a", tmp_root)
        b_img, _, _ = a4.cold_build("a5b", tmp_root)
        md5 = hashlib.md5(a_img).hexdigest()
        print("cold x2: %d Б, md5 %s/%s  %s" %
              (len(a_img), md5, hashlib.md5(b_img).hexdigest(),
               "IDENTICAL" if a_img == b_img else "DIFF"))
        check("determinism", a_img == b_img, fails)
        check("image md5", md5 == a4.EXPECT_IMAGE_MD5, fails)
        check("clean image has no marker",
              a_img[MARKER_OFF:MARKER_OFF + 16] == b"\x00" * 16, fails)

        # ---------- 2. эталон host-запуска ----------
        ctmd = a_img[a4.CTMD_OFF:a4.CTMD_OFF + a4.EXPECT_CTMD_LEN]
        host = a4.host_event_lines(ctmd, tmp_root, "a5_etalon")
        check("host events", host == a4.EXPECT_HOST_EVENTS, fails)

        # ---------- 3. установка: источник + явно помеченная цель ----------
        source = bytearray(a_img)
        source[MARKER_OFF:MARKER_OFF + 16] = SRC_MARKER
        target = bytearray(TARGET_SECTORS * SECTOR)
        target[MARKER_OFF:MARKER_OFF + 16] = TGT_MARKER
        rc, raw, err, disks = boot([bytes(source), bytes(target)],
                                   tmp_root, "install")
        got = a4.lines_of(raw)
        expect = ([a4.POS_PREAMBLE[0]] + A5_LINES +
                  a4.POS_PREAMBLE[1:] + host)
        print("install: rc=%s lines=%d (ожидалось %d)  %s" %
              (rc, len(got), len(expect),
               "OK" if (rc == RC_OK and got == expect and not err)
               else "FAIL"))
        if rc != RC_OK or got != expect or err:
            print("  LOG:", " | ".join(got))
            if err:
                print("  ERR:", err)
            fails.append("install log")

        src_after, tgt_after = disks[0], disks[1]
        print("post-install disk state:")
        check("target marker cleared",
              tgt_after[MARKER_OFF:MARKER_OFF + 16] == b"\x00" * 16, fails)
        check("target autorun marker",
              tgt_after[AUTORUN_OFF:AUTORUN_OFF + 16] == AUTORUN_MARKER, fails)
        check("target ACTIVE=80",
              tgt_after[ACTIVE_OFF] == 0x80, fails)
        check("target LBA5..7 zeroed",
              tgt_after[INSTALL_LBA * SECTOR:
                        (INSTALL_LBA + INSTALL_SECTORS) * SECTOR] ==
              b"\x00" * (INSTALL_SECTORS * SECTOR), fails)
        sbase = SENTINEL_LBA * SECTOR
        check("sentinel magic",
              tgt_after[sbase:sbase + 16] == LOCK_MARKER, fails)
        ver, size, csum, flags = struct.unpack_from("<IIII", tgt_after,
                                                    sbase + 16)
        check("sentinel version=1", ver == 1, fails)
        check("sentinel size=136", size == IMAGE_SECTORS, fails)
        check("sentinel flags=0", flags == 0, fails)
        want = 0
        for off in range(0, IMAGE_SECTORS * SECTOR, 4):
            want = (want + struct.unpack_from("<I", tgt_after, off)[0]) & \
                   0xFFFFFFFF
        print("  checksum in sentinel=%08X, computed=%08X" % (csum, want))
        check("sentinel checksum", csum == want, fails)
        check("source marker cleared",
              src_after[MARKER_OFF:MARKER_OFF + 16] == b"\x00" * 16, fails)
        check("source LBA5..7 zeroed",
              src_after[INSTALL_LBA * SECTOR:
                        (INSTALL_LBA + INSTALL_SECTORS) * SECTOR] ==
              b"\x00" * (INSTALL_SECTORS * SECTOR), fails)

        # ---------- 4. перезагрузка с цели: A9-автозапуск, установщика нет ----------
        rc, raw, err, _ = boot([tgt_after], tmp_root, "reboot_target")
        got = a4.lines_of(raw)
        plain = list(a4.POS_PREAMBLE)
        for name in a4.EXPECT_MODULES:
            plain += a4.host_event_lines(ctmd, tmp_root, "a9_" + name, name)
        reboot_ok = (rc == RC_OK and got == plain and not err and
                     not any("A5" in s for s in got))
        print("reboot from target: rc=%s lines=%d (ожидалось %d)  %s" %
              (rc, len(got), len(plain), "OK" if reboot_ok else "FAIL"))
        if not reboot_ok:
            print("  LOG:", " | ".join(got))
            if err:
                print("  ERR:", err)
            fails.append("reboot from target")

        # ---------- 5. негатив: маркер источника есть, цели нет ----------
        src_nt = bytearray(a_img)
        src_nt[MARKER_OFF:MARKER_OFF + 16] = SRC_MARKER
        blank = bytearray(TARGET_SECTORS * SECTOR)
        rc, raw, err, _ = boot([bytes(src_nt), bytes(blank)],
                               tmp_root, "no_target")
        got = a4.lines_of(raw)
        nt_ok = (rc == RC_INSTALL_REFUSE and
                 "CTOS A5 NO TARGET" in got and
                 "CTOS A5 REFUSED" in got and
                 "CTMD ALL OK" not in got and "PM OK" not in got and
                 not err)
        print("neg no-target: rc=%s (ожидалось %d)  %s" %
              (rc, RC_INSTALL_REFUSE, "OK" if nt_ok else "FAIL"))
        if not nt_ok:
            print("  LOG:", " | ".join(got))
            if err:
                print("  ERR:", err)
            fails.append("neg no-target")

        # ---------- 6. A5b: честные отказы при повреждении закрепления ----------
        # tgt_after — уже закреплённый диск: ACTIVE=0x80 и валидный sentinel.
        # Каждая подмена обязана дать rc=35 и «CTOS A5 PIN FAIL» до PM.
        pin_cases = []

        d = bytearray(tgt_after)
        d[72 * SECTOR + 100] ^= 0x5A          # сектор PM внутри LBA0..135
        pin_cases.append(("image sector", bytes(d)))

        d = bytearray(tgt_after)
        d[AUTORUN_OFF + 3] ^= 0x01            # A9: маркер автозапуска в MBR
        pin_cases.append(("autorun marker", bytes(d)))

        d = bytearray(tgt_after)
        d[sbase + 0x18] ^= 0x01               # контрольная сумма
        pin_cases.append(("sentinel checksum", bytes(d)))

        d = bytearray(tgt_after)
        d[sbase + 0x00] = ord("X")            # магия
        pin_cases.append(("sentinel magic", bytes(d)))

        d = bytearray(tgt_after)
        struct.pack_into("<I", d, sbase + 0x10, 2)   # версия
        pin_cases.append(("sentinel version", bytes(d)))

        d = bytearray(tgt_after)
        struct.pack_into("<I", d, sbase + 0x14, IMAGE_SECTORS - 1)  # размер
        pin_cases.append(("sentinel size", bytes(d)))

        d = bytearray(tgt_after)
        struct.pack_into("<I", d, sbase + 0x1C, 1)   # флаги, смещение +0x1C
        pin_cases.append(("sentinel flags", bytes(d)))

        d = bytearray(tgt_after)
        d[sbase:sbase + SECTOR] = b"\x00" * SECTOR   # sentinel стёрт
        pin_cases.append(("sentinel zeroed", bytes(d)))

        for i, (name, data) in enumerate(pin_cases):
            if not pin_negative(name, data, tmp_root, "pin_%d" % i):
                fails.append("neg " + name)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("")
    if fails:
        print("A5 INSTALL FAIL:", ", ".join(fails))
        print("Эмуляционная контрольная точка НЕ пройдена; на железе не заявляется.")
        return 1
    print("A5 INSTALL OK: двухдисковая самоустановка, ACTIVE+sentinel, "
          "самоудаление, перезагрузка с цели rc=39 без A5-строк, честный "
          "отказ rc=37; A9: автозапуск всех модулей на цели (90 строк); "
          "A5b: 8 подмен дали rc=35 с PIN FAIL. "
          "QEMU — контрольная точка, R3700 не тронут.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
