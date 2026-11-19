# -*- coding: utf-8 -*-
"""A14: выбор одного .ctos по ИМЕНИ с одного SD после удаления флэшки (только QEMU).

A13 выбирал модуль числовым индексом в MBR+0x1AC. Здесь селектор хранит
13-байтовый маркер `CTOS-NAME-A14`, байт-заглушку на MBR+0x1B0 (там mbr.S
пишет номер диска) и 15-байтовое имя CAT-записи с MBR+0x1B1; PM-profile
`name` ищет это имя в CAT (LBA 2056) и запускает ровно один модуль через
тот же синтетический CTMD, что и A8. `native_rt.c`, stage2, MBR, установщик
и дефолтный/combined boot-образы не меняются.

Позитивы: имя syscall.CTS и переключение на sched.CTS; Name-селектор
переживает перестановку CAT-записей (индексный A8 при той же перестановке
честно запускает другой модуль). Негативы: неизвестное имя, порча тела,
нет CAT-маркера. QEMU — локальная эмуляционная контрольная точка; на R3700
не заявляется (моноблок физически не подключён, SD-загрузка BIOS не проверялась).

Запуск только: python -X utf8 Python_compiler/verify_sd_name.py
"""
import hashlib
import io
import os
import struct
import subprocess
import sys
import tempfile
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(REPO, "Python_compiler")
BOOT = os.path.join(REPO, "CtOs", "native", "boot")
if PY not in sys.path:
    sys.path.insert(0, PY)
if BOOT not in sys.path:
    sys.path.insert(0, BOOT)
import verify_boot_image as a4  # noqa: E402
import verify_sd_migration as a12  # noqa: E402
import verify_sd_module as a13  # noqa: E402
import build_boot_image as boot_builder  # noqa: E402

SECTOR = 512
SELECT_OFF = 0x1A0
A14_MARKER = b"CTOS-NAME-A14"
NAME_FIELD = 15
NAME_MD5 = "271516f0f2b659e1093af971059cd41c"
COMBINED_MD5 = "88f86ea9d9c127106af11feec7e4c6f0"
A8_INDEX = 2
A14_NAME = "syscall.CTS"
SWITCH_NAME = "sched.CTS"
SWITCH_INDEX = 1
BAD_NAME = "missing.CTS"


def check(name, cond, fails):
    print("  %-32s %s" % (name, "OK" if cond else "FAIL"))
    if not cond:
        fails.append(name)


def cold_build_name(tag, tmp_root):
    d = os.path.join(tmp_root, "build_" + tag)
    os.makedirs(d, exist_ok=True)
    img = os.path.join(d, "ctos_boot.img")
    a4.clean(img)
    r = subprocess.run(
        [sys.executable, "-X", "utf8", boot_builder.__file__, img, d, "name"],
        capture_output=True, encoding="utf-8", errors="replace", timeout=300)
    if r.returncode:
        raise RuntimeError("A14 build %s: %s %s" %
                           (tag, r.stdout[-500:], r.stderr[-500:]))
    return (io.open(img, "rb").read(),
            io.open(os.path.join(d, "a14_pm_pm.bin"), "rb").read(), d)


def selector(name):
    raw = name.encode("ascii")
    if len(raw) > NAME_FIELD:
        raise RuntimeError("A14: имя длиннее %d байт" % NAME_FIELD)
    # Маркер занимает MBR+0x1A0..0x1AC; MBR+0x1B0 = 0x7DB0 зарезервировано
    # под номер диска (mbr.S), поэтому имя начинается с +0x1B1: 4 байта
    # заглушки между маркером и полем имени.
    return A14_MARKER + b"\x00" * 4 + raw.ljust(NAME_FIELD, b"\x00")


def write_sel(img, blob):
    d = bytearray(img)
    d[SELECT_OFF:SELECT_OFF + len(blob)] = blob
    return a13.repin(d)


def show(tag, rc, got, err):
    if err:
        print("  %s ERR: %s" % (tag, err))
    print("  %s rc=%s LOG: %s" % (tag, rc, " | ".join(got[:40])))


def expect_boot(host):
    return a12.expect_sd(host)


def run_case(sd, tmp_root, tag, want, want_rc=39):
    rc, raw, err, _ = a12.boot([sd], tmp_root, tag)
    got = a4.lines_of(raw)
    ok = rc == want_rc and got == want and not err
    print("%-22s rc=%s lines=%d/%d %s" %
          (tag, rc, len(got), len(want), "OK" if ok else "FAIL"))
    if not ok:
        show(tag, rc, got, err)
    return ok, got, rc


def main():
    fails = []
    tmp_root = tempfile.mkdtemp(prefix="a14_sd_name_", dir=a4.TMP_BASE)
    try:
        img1, pm1, _ = cold_build_name("a14_boot_1", tmp_root)
        img2, pm2, _ = cold_build_name("a14_boot_2", tmp_root)
        md5 = hashlib.md5(img1).hexdigest()
        print("name boot: %d Б, md5 %s, PM=%d Б" % (len(img1), md5, len(pm1)))
        check("name deterministic", img1 == img2 and pm1 == pm2 and
              hashlib.md5(img2).hexdigest() == md5, fails)
        check("name golden", md5 == NAME_MD5, fails)
        combined, _, _ = a12.cold_build_combined("a14_combined", tmp_root)
        check("combined unchanged",
              hashlib.md5(combined).hexdigest() == COMBINED_MD5, fails)

        data, _ = a4.build_data_image(tmp_root)
        host, name = a13.host_for(data, A8_INDEX, tmp_root, "a14_syscall")
        check("CAT name", name == A14_NAME, fails)
        print("host %s: %d строк" % (name, len(host)))

        flash_path = a12.make_flash(img1, data, tmp_root, "a14_flash")[1]
        flash = write_sel(io.open(flash_path, "rb").read(),
                          selector(A14_NAME))
        io.open(flash_path, "wb").write(bytes(flash))
        sd, _ = a12.run_migrate(flash_path, tmp_root, "a14_sd")
        rc, raw, err, disks = a12.boot([flash, sd], tmp_root, "a14_install")
        got = a4.lines_of(raw)
        want = a12.expect_install(host)
        ok = rc == 39 and got == want and not err
        print("a14_install rc=%s lines=%d/%d %s" %
              (rc, len(got), len(want), "OK" if ok else "FAIL"))
        if not ok:
            show("a14_install", rc, got, err)
            fails.append("a14_install")
        sd_after = disks[1]

        ok, _, _ = run_case(sd_after, tmp_root, "a14_sd_alone",
                            expect_boot(host))
        if not ok:
            fails.append("a14_sd_alone")
        check("SD data intact", sd_after[2048 * SECTOR:
              2048 * SECTOR + len(data)] == data, fails)

        # имя из MBR переключает модуль без пересборки образа
        host_sw, name_sw = a13.host_for(data, SWITCH_INDEX, tmp_root,
                                        "a14_sched")
        check("switch CAT name", name_sw == SWITCH_NAME, fails)
        switched = write_sel(sd_after, selector(SWITCH_NAME))
        ok, _, _ = run_case(switched, tmp_root, "a14_switch_name",
                            expect_boot(host_sw))
        if not ok:
            fails.append("a14_switch_name")

        # неизвестное имя — честный отказ
        unknown = write_sel(sd_after, selector(BAD_NAME))
        rc, raw, err, _ = a12.boot([unknown], tmp_root, "a14_unknown")
        got = a4.lines_of(raw)
        ok = rc == 41 and "CTOS A14 NO NAME" in got and not err
        print("a14_unknown rc=%s %s" % (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("a14_unknown", rc, got, err)
            fails.append("a14_unknown")

        # порча тела выбранной CAT-записи
        off, _ = a13.cat_body_offset(data, A8_INDEX)
        bad = bytearray(sd_after)
        bad[off + 8] ^= 0x5A
        rc, raw, err, _ = a12.boot([bytes(bad)], tmp_root, "a14_bad_body")
        got = a4.lines_of(raw)
        ok = rc == 41 and any("FATAL: CTMD:" in s for s in got) and not err
        print("a14_bad_body rc=%s %s" % (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("a14_bad_body", rc, got, err)
            fails.append("a14_bad_body")

        # нет CAT-маркера данных — shim честно отказывает
        nodata = bytearray(sd_after)
        m = 2048 * SECTOR + a4.A7_MARKER_OFF
        nodata[m:m + 13] = b"\x00" * 13
        rc, raw, err, _ = a12.boot([bytes(nodata)], tmp_root, "a14_no_data")
        got = a4.lines_of(raw)
        ok = rc == 41 and "CTOS A8 NO DATA" in got and not err
        print("a14_no_data rc=%s %s" % (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("a14_no_data", rc, got, err)
            fails.append("a14_no_data")

        # перестановка CAT-записей: имя находит ту же запись, индекс — уже другую
        cat = 2056 * SECTOR
        reordered = bytearray(sd_after)
        e1 = cat + 24 + 64 * SWITCH_INDEX
        e2 = cat + 24 + 64 * A8_INDEX
        reordered[e1:e1 + 64], reordered[e2:e2 + 64] = \
            bytes(reordered[e2:e2 + 64]), bytes(reordered[e1:e1 + 64])
        count = struct.unpack_from("<I", reordered, cat + 12)[0]
        struct.pack_into("<I", reordered, cat + 20, 0)
        crc = zlib.crc32(bytes(reordered[cat:cat + 24 + 64 * count])) & \
              0xFFFFFFFF
        struct.pack_into("<I", reordered, cat + 20, crc)
        by_name = write_sel(reordered, selector(A14_NAME))
        ok, _, _ = run_case(bytes(by_name), tmp_root, "a14_reordered_name",
                            expect_boot(host))
        if not ok:
            fails.append("a14_reordered_name")
        by_index = bytearray(reordered)
        by_index[SELECT_OFF:SELECT_OFF + 13] = a4.A8_MARKER + bytes([A8_INDEX])
        by_index = a13.repin(by_index)
        ok, _, _ = run_case(bytes(by_index), tmp_root, "a14_reordered_index",
                            expect_boot(host_sw))
        if not ok:
            fails.append("a14_reordered_index")

        print("\nA14 SD NAME: FAILED=%d" % len(fails))
        if fails:
            print("  " + ", ".join(fails))
        return 1 if fails else 0
    finally:
        pass


if __name__ == "__main__":
    sys.exit(main())
