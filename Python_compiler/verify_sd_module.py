# -*- coding: utf-8 -*-
"""A13: выбранный .ctos с ЕДИНОГО SD после удаления флэшки (только QEMU).

A12 показал, что SD один грузится с boot+data и запускает все модули A6.
 Здесь закрывается последний пробел сценария: тот же SD запускает ровно
 один выбранный модуль из CAT-области своего же диска (A8 через LBA 2056),
 плюс таймерный профиль A11 на одном SD.

 1. combined- boot + data с LBA 2048 + CTOS-INST-A5 + CTOS-DISK-A8/индекс;
    migrate_sd.py переносит всё на SD, A5 закрепляет boot.
 2. загрузка с флэшки и перезагрузка с одного SD: COM1 байт-в-байт хосту
    `native_rt --module <имя из CAT>`; data stays byte-exact.
 3. негативы: порча тела в CAT SD ⇒ rc=41; сбитый индекс ⇒ fallback на A6;
    стёртый маркер данных ⇒ `CTOS A8 NO DATA` + rc=41.
 4. профиль timer_ret (schedTR) на одном SD: 10 тиков, 10 TIMER_RET,
    `OPS 753 CELLS 60`, COM1 == host; порча тела ⇒ rc=41.

QEMU — локальная эмуляционная контрольная точка. На R3700 НЕ заявляется:
моноблок физически не подключён (нет диска/SD/питания), он на складе
выключен; SD-загрузка его BIOS не проверялась.

Запуск только: python -X utf8 Python_compiler/verify_sd_module.py
"""
import hashlib
import io
import os
import struct
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(REPO, "Python_compiler")
if PY not in sys.path:
    sys.path.insert(0, PY)
import verify_boot_image as a4  # noqa: E402
import verify_sd_migration as a12  # noqa: E402

SECTOR = 512
CAT_LBA = 2056
COMBINED_MD5 = "88f86ea9d9c127106af11feec7e4c6f0"
A8_INDEX = 2            # syscall.CTS в дефолтном CAT
A11_INDEX = 3           # schedTR в профиле timer_ret
BAD_INDEX = 9           # > A8_MAX_INDEX (8) — честный fallback


def check(name, cond, fails):
    print("  %-32s %s" % (name, "OK" if cond else "FAIL"))
    if not cond:
        fails.append(name)


def make_flash_a8(boot, data, tmp_root, tag, index, with_src=True):
    """Тот же flash A12, но с маркером A8 в boot-MBR (переживает pin)."""
    flash, path = a12.make_flash(boot, data, tmp_root, tag, with_src)
    f = bytearray(flash)
    sel = a4.A8_MARKER + bytes([index])
    f[a4.A8_SELECT_OFF:a4.A8_SELECT_OFF + len(sel)] = sel
    io.open(path, "wb").write(bytes(f))
    return bytes(f), path


def cat_body_offset(data_img, index):
    """Смещение тела записи CAT в SD-образе: LBA 2048+8 = 2056."""
    cat = data_img[a4.a7data.CAT_LBA * SECTOR:
                   (a4.a7data.CAT_LBA + a4.a7data.CAT_SECTORS) * SECTOR]
    ent = cat[24 + 64 * index:24 + 64 * (index + 1)]
    size, crc, body_off = struct.unpack_from("<III", ent, 24)
    return a12.CAT_LBA * SECTOR + body_off, size


def repin(sd):
    """Пересчитать A5b-checksum LBA0..135 после правки MBR и записать в LBA136+24."""
    d = bytearray(sd)
    csum = 0
    for off in range(0, a12.IMAGE_SECTORS * SECTOR, 4):
        csum = (csum + struct.unpack_from("<I", d, off)[0]) & 0xFFFFFFFF
    struct.pack_into("<I", d, a12.SENTINEL_LBA * SECTOR + 0x18, csum)
    return d


def host_for(data_img, index, tmp_root, tag):
    ctmd, name = a4.a8_ctmd(data_img, index)
    return a4.host_event_lines(ctmd, tmp_root, tag, name), name


def show(tag, rc, got, err):
    if err:
        print("  %s ERR: %s" % (tag, err))
    print("  %s rc=%s LOG: %s" % (tag, rc, " | ".join(got[:40])))


def main():
    fails = []
    tmp_root = tempfile.mkdtemp(prefix="a13_sd_module_", dir=a4.TMP_BASE)
    try:
        boot_img, _, _ = a12.cold_build_combined("a13_boot", tmp_root)
        md5 = hashlib.md5(boot_img).hexdigest()
        print("combined boot: %d Б, md5 %s" % (len(boot_img), md5))
        check("combined golden", md5 == COMBINED_MD5, fails)

        # ---------- 1. дефолтный CAT: syscall.CTS с одного SD ----------
        data, _ = a4.build_data_image(tmp_root)
        host, name = host_for(data, A8_INDEX, tmp_root, "a8_default")
        check("CAT name", name == "syscall.CTS", fails)
        print("host %s: %d строк" % (name, len(host)))

        flash, flash_path = make_flash_a8(boot_img, data, tmp_root,
                                          "a8_flash", A8_INDEX)
        sd, _ = a12.run_migrate(flash_path, tmp_root, "a8_sd")
        rc, raw, err, disks = a12.boot([flash, sd], tmp_root, "a8_install")
        got = a4.lines_of(raw)
        want = a12.expect_install(host)
        print("install boot: rc=%s lines=%d/%d %s" %
              (rc, len(got), len(want),
               "OK" if (rc == 39 and got == want and not err) else "FAIL"))
        if rc != 39 or got != want or err:
            show("a8_install", rc, got, err)
            fails.append("a8_install log")
        sd_after = disks[1]

        rc, raw, err, _ = a12.boot([sd_after], tmp_root, "a8_sd_alone")
        got = a4.lines_of(raw)
        want = a12.expect_sd(host)
        print("sd alone: rc=%s lines=%d/%d %s" %
              (rc, len(got), len(want),
               "OK" if (rc == 39 and got == want and not err) else "FAIL"))
        if rc != 39 or got != want or err:
            show("a8_sd_alone", rc, got, err)
            fails.append("a8_sd_alone log")
        check("SD data intact", sd_after[2048 * SECTOR:
              2048 * SECTOR + len(data)] == data, fails)

        # ---------- 2. негативы на одном SD ----------
        off, size = cat_body_offset(data, A8_INDEX)
        bad = bytearray(sd_after)
        bad[off + 8] ^= 0x5A
        rc, raw, err, _ = a12.boot([bytes(bad)], tmp_root, "a8_bad_body")
        got = a4.lines_of(raw)
        ok = (rc == 41 and any("FATAL: CTMD:" in s for s in got) and not err)
        print("neg a8_bad_body   rc=%s  %s" %
              (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("a8_bad_body", rc, got, err)
            fails.append("a8_bad_body")

        bad_idx = bytearray(sd_after)
        bad_idx[a4.A8_INDEX_OFF] = BAD_INDEX
        bad_idx = repin(bad_idx)
        rc, raw, err, _ = a12.boot([bytes(bad_idx)], tmp_root, "a8_bad_index")
        got = a4.lines_of(raw)
        host_all = []
        ctmd = boot_img[a4.CTMD_OFF:a4.CTMD_OFF + a4.EXPECT_CTMD_LEN]
        for nm in a4.EXPECT_MODULES:
            host_all += a4.host_event_lines(ctmd, tmp_root,
                                            "a13_fb_" + nm, nm)
        want_fb = a12.expect_sd(host_all)
        ok = (rc == 39 and got == want_fb and not err)
        print("neg a8_bad_index  rc=%s  %s" %
              (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("a8_bad_index", rc, got, err)
            fails.append("a8_bad_index")

        nodata = bytearray(sd_after)
        nodata[2048 * SECTOR + a4.A7_MARKER_OFF:
               2048 * SECTOR + a4.A7_MARKER_OFF + 13] = b"\x00" * 13
        rc, raw, err, _ = a12.boot([bytes(nodata)], tmp_root, "a8_no_data")
        got = a4.lines_of(raw)
        ok = (rc == 41 and "CTOS A8 NO DATA" in got and not err)
        print("neg a8_no_data    rc=%s  %s" %
              (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("a8_no_data", rc, got, err)
            fails.append("a8_no_data")

        # ---------- 3. timer_ret (schedTR) на одном SD ----------
        tr_ctmd, tr_data, _ = a4.build_timer_ret_artifacts(tmp_root)
        host_tr, name_tr = host_for(tr_data, A11_INDEX, tmp_root, "a11_sd")
        check("timer_ret name", name_tr == "schedTR", fails)
        flash_tr, path_tr = make_flash_a8(boot_img, tr_data, tmp_root,
                                          "tr_flash", A11_INDEX)
        sd_tr, _ = a12.run_migrate(path_tr, tmp_root, "tr_sd")
        rc, raw, err, disks = a12.boot([flash_tr, sd_tr], tmp_root,
                                       "tr_install")
        got = a4.lines_of(raw)
        want = a12.expect_install(host_tr)
        ok = rc == 39 and got == want and not err
        print("timer_ret install: rc=%s lines=%d/%d %s" %
              (rc, len(got), len(want), "OK" if ok else "FAIL"))
        if not ok:
            show("tr_install", rc, got, err)
            fails.append("tr_install log")
        sd_tr_after = disks[1]

        rc, raw, err, _ = a12.boot([sd_tr_after], tmp_root, "tr_sd_alone")
        got = a4.lines_of(raw)
        want = a12.expect_sd(host_tr)
        ok = rc == 39 and got == want and not err
        print("timer_ret sd alone: rc=%s lines=%d/%d %s" %
              (rc, len(got), len(want), "OK" if ok else "FAIL"))
        if not ok:
            show("tr_sd_alone", rc, got, err)
            fails.append("tr_sd_alone log")
        check("A11 MODULE line", a4.A11_MODULE_LINE in got, fails)
        check("A11 counts", a4.A11_COUNTS in got, fails)
        check("A11 ticks",
              sum(1 for s in got if s.startswith("TICK ")) == 10, fails)
        check("A11 IRETs",
              sum(1 for s in got if "SYSCALL 154" in s) == 10, fails)
        seen11 = sum(1 for m in a4.A11_MARKERS if any(m in s for s in got))
        bad11 = [b for b in a4.A11_BAD_MARKERS if any(b in s for s in got)]
        check("A11 markers",
              seen11 == len(a4.A11_MARKERS) and not bad11, fails)

        off_tr, _ = cat_body_offset(tr_data, A11_INDEX)
        bad_tr = bytearray(sd_tr_after)
        bad_tr[off_tr + 8] ^= 0x5A
        rc, raw, err, _ = a12.boot([bytes(bad_tr)], tmp_root, "tr_bad_body")
        got = a4.lines_of(raw)
        ok = (rc == 41 and any("FATAL: CTMD:" in s for s in got) and not err)
        print("neg tr_bad_body   rc=%s  %s" %
              (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("tr_bad_body", rc, got, err)
            fails.append("tr_bad_body")

        print("\nA13 SD MODULE: FAILED=%d" % len(fails))
        if fails:
            print("  " + ", ".join(fails))
        return 1 if fails else 0
    finally:
        pass


if __name__ == "__main__":
    sys.exit(main())
