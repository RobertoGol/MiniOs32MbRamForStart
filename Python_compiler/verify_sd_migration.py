# -*- coding: utf-8 -*-
"""A12: «флэшка -> наш скрипт -> SD -> убрать флэшку» в QEMU (только эмуляция).

Проверяется ровно то, что исполняется:
  1. дефолтный boot-образ остался байт-в-байт прежним (md5 A5/A9), а новый
     профиль `combined` собирается дважды в разных TEMP -> IDENTICAL;
  2. флэшка = boot (LBA 0..135) + data (целиком с LBA 2048) + CTOS-INST-A5;
     скрипт migrate_sd.py копирует ВСЁ на SD и ставит CTOS-TGT-A5!;
  3. загрузка с флэшки: штатный A5-установщик копирует и закрепляет boot на
     SD, самоудаляется, area данных на SD остаётся байт-в-байт прежней;
  4. перезагрузка с одного SD (флэшки нет): combined-stage2 видит данные на
     том же диске по LBA 2048/2056, COM1 байт-в-байт эталону host + A7;
  5. негативы: бит Catalan CAT -> rc=35; стёртый маркер данных -> честное
     отсутствие A7; сбитый sentinel -> rc=35; нет маркера источника -> A5
     не запускается и SD остаётся незакреплённой.

QEMU — локальная эмуляционная контрольная точка. На R3700 НЕ заявляется:
моноблок физически не подключён, диска/SD/питания нет, он на складе
выключенный; SD-загрузка его BIOS не проверялась.

Запуск только: python -X utf8 Python_compiler/verify_sd_migration.py
"""
import hashlib
import io
import os
import struct
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(REPO, "Python_compiler")
if PY not in sys.path:
    sys.path.insert(0, PY)
import verify_boot_image as a4  # noqa: E402

BUILDER = a4.BUILDER
MIGRATE = os.path.join(REPO, "CtOs", "native", "migrate_sd.py")

SECTOR = 512
DATA_LBA = 2048
CAT_LBA = DATA_LBA + 8
MARKER_OFF = 0x180
AUTORUN_OFF = 0x190
ACTIVE_OFF = 0x1BE
IMAGE_SECTORS = 136
INSTALL_LBA = 5
INSTALL_SECTORS = 3
SENTINEL_LBA = 136
SRC_MARKER = b"CTOS-INST-A5\x00\x00\x00\x00"
TGT_MARKER = b"CTOS-TGT-A5!\x00\x00\x00\x00"
AUTORUN_MARKER = b"CTOS-AUTORUN-A6\x00"
LOCK_MARKER = b"CTOS-LOCK-A5\x00\x00\x00\x00"

RC_OK = 39
RC_REFUSE = 35

A5_LINES = [
    "CTOS A5 INSTALL: START",
    "CTOS A5 TARGET 0x81",
    "CTOS A5 WRITE OK",
    "CTOS A5 SELF-DELETE OK",
    "CTOS A5 PIN OK",
    "CTOS A5 INSTALL OK",
    "CTOS A5 AUTORUN ALL",
]


def check(name, cond, fails):
    print("  %-30s %s" % (name, "OK" if cond else "FAIL"))
    if not cond:
        fails.append(name)


def clean(p):
    a4.clean(p)


def cold_build_combined(tag, tmp_root):
    d = os.path.join(tmp_root, "build_" + tag)
    os.makedirs(d, exist_ok=True)
    img = os.path.join(d, "ctos_boot.img")
    clean(img)
    r = subprocess.run(
        [sys.executable, "-X", "utf8", BUILDER, img, d, "combined"],
        capture_output=True, encoding="utf-8", errors="replace", timeout=300)
    if r.returncode:
        raise RuntimeError("A12 build %s: %s %s" %
                           (tag, r.stdout[-500:], r.stderr[-500:]))
    stage2 = io.open(os.path.join(d, "a12_s2.bin"), "rb").read()
    return io.open(img, "rb").read(), stage2, d


def make_flash(boot, data, tmp_root, tag, with_src=True):
    d = os.path.join(tmp_root, "flash_" + tag)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "flash.img")
    clean(p)
    f = bytearray((DATA_LBA + len(data) // SECTOR) * SECTOR)
    f[:len(boot)] = boot
    f[DATA_LBA * SECTOR:DATA_LBA * SECTOR + len(data)] = data
    if with_src:
        f[MARKER_OFF:MARKER_OFF + 16] = SRC_MARKER
    io.open(p, "wb").write(bytes(f))
    return bytes(f), p


def run_migrate(flash_path, tmp_root, tag):
    d = os.path.join(tmp_root, "sd_" + tag)
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "sd.img")
    clean(out)
    r = subprocess.run([sys.executable, "-X", "utf8", MIGRATE,
                        flash_path, out],
                       capture_output=True, encoding="utf-8",
                       errors="replace", timeout=120)
    if r.returncode:
        raise RuntimeError("A12 migrate: %s %s" % (r.stdout, r.stderr))
    return io.open(out, "rb").read(), out


def boot(disks, tmp_root, tag):
    d = os.path.join(tmp_root, "run_" + tag)
    os.makedirs(d, exist_ok=True)
    log = os.path.join(d, "serial.log")
    clean(log)
    paths = []
    for i, data in enumerate(disks):
        p = os.path.join(d, "disk%d.img" % i)
        clean(p)
        io.open(p, "wb").write(data)
        paths.append(p)
    cmd = [a4.qemu(), "-machine", "pc"]
    for i, p in enumerate(paths):
        cmd += ["-drive",
                "file=%s,format=raw,if=ide,index=%d,media=disk" % (p, i)]
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
        return None, b"", "QEMU TIMEOUT", [bytes(len(x)) for x in disks]
    raw = io.open(log, "rb").read() if os.path.exists(log) else b""
    return r.returncode, raw, err, [io.open(p, "rb").read() for p in paths]


def expect_install(host):
    return (list(a4.POS_PREAMBLE[:1]) + A5_LINES +
            list(a4.POS_PREAMBLE[1:7]) + [a4.A7_LINE] +
            list(a4.POS_PREAMBLE[7:]) + list(host))


def expect_sd(host):
    return (list(a4.POS_PREAMBLE[:7]) + [a4.A7_LINE] +
            list(a4.POS_PREAMBLE[7:]) + list(host))


def show(tag, rc, got, err):
    if rc != RC_OK and rc is not None:
        print("  %s rc=%s LOG: %s" % (tag, rc, " | ".join(got)))
    if err:
        print("  %s ERR: %s" % (tag, err))


def main():
    fails = []
    tmp_root = tempfile.mkdtemp(prefix="a12_sd_verify_", dir=a4.TMP_BASE)
    try:
        # ---------- 1. две холодные сборки ----------
        d_img, _, _ = a4.cold_build("a12_default", tmp_root)
        c_img, c_s2, _ = cold_build_combined("a12_combined", tmp_root)
        c_img2, c_s2_2, _ = cold_build_combined("a12_combined2", tmp_root)
        d_md5 = hashlib.md5(d_img).hexdigest()
        c_md5 = hashlib.md5(c_img).hexdigest()
        print("cold default: %d Б, md5 %s" % (len(d_img), d_md5))
        print("cold combined x2: %d Б, md5 %s/%s  %s" %
              (len(c_img), c_md5, hashlib.md5(c_img2).hexdigest(),
               "IDENTICAL" if c_img == c_img2 else "DIFF"))
        check("default golden unchanged", d_md5 == a4.EXPECT_IMAGE_MD5, fails)
        check("combined deterministic", c_img == c_img2, fails)
        check("combined stage2 deterministic", c_s2 == c_s2_2, fails)
        check("combined size", len(c_img) == a4.IMAGE_LEN, fails)
        check("combined stage2 size",
              len(c_s2) <= 4 * SECTOR and len(c_s2) != a4.EXPECT_S2_LEN,
              fails)
        print("  combined stage2=%d Б, md5 %s" %
              (len(c_s2), hashlib.md5(c_s2).hexdigest()))

        ctmd = c_img[a4.CTMD_OFF:a4.CTMD_OFF + a4.EXPECT_CTMD_LEN]
        host = a4.host_event_lines(ctmd, tmp_root, "a12_etalon")
        check("host events", host == a4.EXPECT_HOST_EVENTS, fails)
        # A9 на закреплённом SD включает ВСЕ модули — как в A6-гейте.
        host_all = []
        for name in a4.EXPECT_MODULES:
            host_all += a4.host_event_lines(ctmd, tmp_root,
                                            "a12_auto_" + name, name)

        # ---------- 2. данные + флэшка + скрипт переноса ----------
        data, _ = a4.build_data_image(tmp_root)
        flash, flash_path = make_flash(c_img, data, tmp_root, "install")
        sd_migrated, _ = run_migrate(flash_path, tmp_root, "install")
        dbase = DATA_LBA * SECTOR
        cbase = CAT_LBA * SECTOR
        want_boot = bytearray(c_img)
        want_boot[MARKER_OFF:MARKER_OFF + 16] = TGT_MARKER
        check("script copied boot", sd_migrated[:IMAGE_SECTORS * SECTOR] ==
              bytes(want_boot), fails)
        check("script copied data", sd_migrated[dbase:dbase + len(data)] ==
              data, fails)
        check("script set target marker",
              sd_migrated[MARKER_OFF:MARKER_OFF + 16] == TGT_MARKER, fails)

        # ---------- 3. загрузка с флэшки: A5 закрепляет SD ----------
        rc, raw, err, disks = boot([flash, sd_migrated], tmp_root, "install")
        got = a4.lines_of(raw)
        want = expect_install(host)
        print("install boot: rc=%s lines=%d (ожидалось %d)  %s" %
              (rc, len(got), len(want),
               "OK" if (rc == RC_OK and got == want and not err) else "FAIL"))
        if rc != RC_OK or got != want or err:
            show("install", rc, got, err)
            fails.append("install log")
        flash_after, sd = disks

        check("flash source marker cleared",
              flash_after[MARKER_OFF:MARKER_OFF + 16] == b"\x00" * 16, fails)
        check("flash installer zeroed",
              flash_after[INSTALL_LBA * SECTOR:
                          (INSTALL_LBA + INSTALL_SECTORS) * SECTOR] ==
              b"\x00" * (INSTALL_SECTORS * SECTOR), fails)
        check("SD target marker cleared",
              sd[MARKER_OFF:MARKER_OFF + 16] == b"\x00" * 16, fails)
        check("SD autorun marker",
              sd[AUTORUN_OFF:AUTORUN_OFF + 16] == AUTORUN_MARKER, fails)
        check("SD ACTIVE=80", sd[ACTIVE_OFF] == 0x80, fails)
        check("SD installer zeroed",
              sd[INSTALL_LBA * SECTOR:
                 (INSTALL_LBA + INSTALL_SECTORS) * SECTOR] ==
              b"\x00" * (INSTALL_SECTORS * SECTOR), fails)
        sbase = SENTINEL_LBA * SECTOR
        ver, size, csum, flags = struct.unpack_from("<IIII", sd, sbase + 16)
        check("SD sentinel magic",
              sd[sbase:sbase + 16] == LOCK_MARKER, fails)
        check("SD sentinel fields",
              (ver, size, flags) == (1, IMAGE_SECTORS, 0), fails)
        check("SD data intact after install",
              sd[dbase:dbase + len(data)] == data, fails)
        data_cat_off = a4.a7data.CAT_LBA * SECTOR
        check("SD CAT intact after install",
              sd[cbase:cbase + 64 * SECTOR] ==
              data[data_cat_off:data_cat_off + 64 * SECTOR], fails)

        # ---------- 4. флэшки нет: загрузка одного SD ----------
        rc, raw, err, _ = boot([sd], tmp_root, "sd_alone")
        got = a4.lines_of(raw)
        want = expect_sd(host_all)
        print("sd alone: rc=%s lines=%d (ожидалось %d)  %s" %
              (rc, len(got), len(want),
               "OK" if (rc == RC_OK and got == want and not err) else "FAIL"))
        if rc != RC_OK or got != want or err:
            show("sd_alone", rc, got, err)
            fails.append("sd alone log")

        # ---------- 5. негативы ----------
        bad = bytearray(sd)
        bad[cbase:cbase + 4] = b"XXXX"
        rc, raw, err, _ = boot([bytes(bad)], tmp_root, "sd_bad_cat")
        got = a4.lines_of(raw)
        ok = (rc == RC_REFUSE and "CTOS A7 DATA BAD" in got and
              "CTOS A3b PM OK" not in got and not err)
        print("neg sd_bad_cat     rc=%s  %s" % (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("sd_bad_cat", rc, got, err)
            fails.append("sd_bad_cat")

        nodata = bytearray(sd)
        nodata[dbase + MARKER_OFF:dbase + MARKER_OFF + 13] = b"\x00" * 13
        rc, raw, err, _ = boot([bytes(nodata)], tmp_root, "sd_nodata")
        got = a4.lines_of(raw)
        want_nd = (list(a4.POS_PREAMBLE[:7]) + list(a4.POS_PREAMBLE[7:]) +
                   list(host_all))
        ok = (rc == RC_OK and got == want_nd and a4.A7_LINE not in got and
              not err)
        print("neg sd_nodata      rc=%s  %s" % (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("sd_nodata", rc, got, err)
            fails.append("sd_nodata")

        badpin = bytearray(sd)
        badpin[sbase:sbase + 4] = b"XXXX"
        rc, raw, err, _ = boot([bytes(badpin)], tmp_root, "sd_bad_pin")
        got = a4.lines_of(raw)
        ok = (rc == RC_REFUSE and "CTOS A5 PIN FAIL" in got and
              "CTOS A3b PM OK" not in got and not err)
        print("neg sd_bad_pin     rc=%s  %s" % (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("sd_bad_pin", rc, got, err)
            fails.append("sd_bad_pin")

        # маркера источника нет: установщик не запускается, SD не закреплён
        f_nosrc, f_nosrc_path = make_flash(c_img, data, tmp_root, "nosrc",
                                           with_src=False)
        # скрипт честно откажет без CTOS-INST-A5 — проверяем отказ отдельно
        r = subprocess.run([sys.executable, "-X", "utf8", MIGRATE,
                            f_nosrc_path,
                            os.path.join(tmp_root, "nosrc_out.img")],
                           capture_output=True, encoding="utf-8",
                           errors="replace", timeout=120)
        ok = r.returncode == 1 and "CTOS-INST-A5" in (r.stdout + r.stderr)
        print("neg migrate_nosrc  rc=%s  %s" %
              (r.returncode, "OK" if ok else "FAIL"))
        if not ok:
            fails.append("migrate_nosrc")

        rc, raw, err, disks = boot([f_nosrc, sd_migrated], tmp_root, "noinstall")
        got = a4.lines_of(raw)
        sd_noinst = disks[1]
        ok = (rc == RC_OK and not any(s.startswith("CTOS A5 ")
                                      for s in got) and
              sd_noinst[MARKER_OFF:MARKER_OFF + 16] == TGT_MARKER and
              sd_noinst[sbase:sbase + 16] != LOCK_MARKER and not err)
        print("neg no_install     rc=%s  %s" % (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("noinstall", rc, got, err)
            fails.append("no_install")

        print("\nA12 SD MIGRATION: FAILED=%d" % len(fails))
        if fails:
            print("  " + ", ".join(fails))
        return 1 if fails else 0
    finally:
        pass


if __name__ == "__main__":
    sys.exit(main())
