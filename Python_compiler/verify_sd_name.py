# -*- coding: utf-8 -*-
"""A14: выбор одного .ctos по ИМЕНИ с диска (только QEMU).

A13 выбирал модуль числовым индексом в MBR+0x1AC. Здесь селектор хранит
13-байтовый маркер `CTOS-NAME-A14`, 4 байта заглушки (MBR+0x1B0 = 0x7DB0
зарезервирован под номер диска в mbr.S) и 15-байтовое имя CAT-записи с
MBR+0x1B1. PM ищет это имя в уже прочитанной CAT-области и запускает ровно
один модуль через тот же синтетический CTMD, что и A8. `native_rt.c`, stage2,
MBR, установщик и дефолтный/combined boot-образы не меняются.

Покрыты два сценария: один SD после удаления флэшки (профиль `name`,
combined stage2, CAT на LBA 2056) и отдельный диск данных HDD/SSD (профиль
`name_sep`, дефолтное сканирование, CAT на LBA 8).

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
import verify_a5_install as a5  # noqa: E402
import build_boot_image as boot_builder  # noqa: E402

SECTOR = 512
SELECT_OFF = 0x1A0
A14_MARKER = b"CTOS-NAME-A14"
NAME_FIELD = 15
NAME_MD5 = "271516f0f2b659e1093af971059cd41c"
NAME_SEP_MD5 = "310376d2f37fe785189d93a5d6d71677"
COMBINED_MD5 = "88f86ea9d9c127106af11feec7e4c6f0"
DEFAULT_MD5 = "59285f03e4c60c512cbb9c7963f1748f"
A8_INDEX = 2
A14_NAME = "syscall.CTS"
SWITCH_NAME = "sched.CTS"
SWITCH_INDEX = 1
BAD_NAME = "missing.CTS"


def check(name, cond, fails):
    print("  %-32s %s" % (name, "OK" if cond else "FAIL"))
    if not cond:
        fails.append(name)


def cold_build_profile(profile, base, tag, tmp_root):
    d = os.path.join(tmp_root, "build_" + tag)
    os.makedirs(d, exist_ok=True)
    img = os.path.join(d, "ctos_boot.img")
    a4.clean(img)
    r = subprocess.run(
        [sys.executable, "-X", "utf8", boot_builder.__file__, img, d, profile],
        capture_output=True, encoding="utf-8", errors="replace", timeout=300)
    if r.returncode:
        raise RuntimeError("A14 build %s: %s %s" %
                           (tag, r.stdout[-500:], r.stderr[-500:]))
    return (io.open(img, "rb").read(),
            io.open(os.path.join(d, base + "_pm_pm.bin"), "rb").read(), d)


def cold_build_name(tag, tmp_root):
    return cold_build_profile("name", "a14", tag, tmp_root)


def cold_build_name_sep(tag, tmp_root):
    return cold_build_profile("name_sep", "a14sep", tag, tmp_root)


def selector(name):
    raw = name.encode("ascii")
    if len(raw) > NAME_FIELD:
        raise RuntimeError("A14: имя длиннее %d байт" % NAME_FIELD)
    # Маркер занимает MBR+0x1A0..0x1AC; MBR+0x1B0 = 0x7DB0 зарезервировано
    # под номер диска (mbr.S), поэтому имя начинается с +0x1B1: 4 байта
    # заглушки между маркером и полем имени.
    return A14_MARKER + b"\x00" * 4 + raw.ljust(NAME_FIELD, b"\x00")


def write_sel(img, blob, pin=True):
    d = bytearray(img)
    d[SELECT_OFF:SELECT_OFF + len(blob)] = blob
    return a13.repin(d) if pin else d


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


def expect_sep(host):
    return (list(a4.POS_PREAMBLE[:7]) + [a4.A7_LINE] +
            list(a4.POS_PREAMBLE[7:]) + host)


def run_sep_case(boot_img, data_path, tmp_root, tag, want, want_rc=39):
    rc, raw, err = a4.boot_log(boot_img, tmp_root, tag, data_path)
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

        sep1, sep_pm1, _ = cold_build_name_sep("a14_sep_1", tmp_root)
        sep2, sep_pm2, _ = cold_build_name_sep("a14_sep_2", tmp_root)
        sep_md5 = hashlib.md5(sep1).hexdigest()
        print("name_sep boot: %d Б, md5 %s, PM=%d Б" %
              (len(sep1), sep_md5, len(sep_pm1)))
        check("name_sep deterministic", sep1 == sep2 and sep_pm1 == sep_pm2 and
              hashlib.md5(sep2).hexdigest() == sep_md5, fails)
        check("name_sep golden", sep_md5 == NAME_SEP_MD5, fails)

        default_img, _, _ = cold_build_profile("default", "a3b", "a14_default", tmp_root)
        check("default unchanged",
              hashlib.md5(default_img).hexdigest() == DEFAULT_MD5, fails)
        combined, _, _ = a12.cold_build_combined("a14_combined", tmp_root)
        check("combined unchanged",
              hashlib.md5(combined).hexdigest() == COMBINED_MD5, fails)

        data, data_path = a4.build_data_image(tmp_root)
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
        check("SD selector preserved after install",
              sd_after[SELECT_OFF:SELECT_OFF + 13] == A14_MARKER, fails)

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

        # ---------- A14 на отдельном диске данных (HDD/SSD, дефолтный stage2) ----------
        sep_boot = write_sel(sep1, selector(A14_NAME), pin=False)
        ok, _, _ = run_sep_case(bytes(sep_boot), data_path, tmp_root,
                                "a14_sep_syscall", expect_sep(host))
        if not ok:
            fails.append("a14_sep_syscall")

        host_sw, name_sw = a13.host_for(data, SWITCH_INDEX, tmp_root,
                                        "a14_sep_sched_host")
        check("sep switch CAT name", name_sw == SWITCH_NAME, fails)
        sep_sw = write_sel(sep1, selector(SWITCH_NAME), pin=False)
        ok, _, _ = run_sep_case(bytes(sep_sw), data_path, tmp_root,
                                "a14_sep_switch", expect_sep(host_sw))
        if not ok:
            fails.append("a14_sep_switch")

        sep_unknown = write_sel(sep1, selector(BAD_NAME), pin=False)
        rc, raw, err = a4.boot_log(bytes(sep_unknown), tmp_root,
                                   "a14_sep_unknown", data_path)
        got = a4.lines_of(raw)
        ok = rc == 41 and "CTOS A14 NO NAME" in got and not err
        print("a14_sep_unknown rc=%s %s" % (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("a14_sep_unknown", rc, got, err)
            fails.append("a14_sep_unknown")

        # порча тела на отдельном диске данных
        cat0 = a4.a7data.CAT_LBA * SECTOR
        ent = data[cat0 + 24 + 64 * A8_INDEX:cat0 + 24 + 64 * (A8_INDEX + 1)]
        body_off = struct.unpack_from("<I", ent, 32)[0]
        bad_data = bytearray(data)
        bad_data[cat0 + body_off + 8] ^= 0x5A
        bad_data_path = os.path.join(tmp_root, "a14_sep_bad_body.img")
        io.open(bad_data_path, "wb").write(bytes(bad_data))
        rc, raw, err = a4.boot_log(bytes(sep_boot), tmp_root,
                                   "a14_sep_bad_body", bad_data_path)
        got = a4.lines_of(raw)
        ok = rc == 41 and any("FATAL: CTMD:" in s for s in got) and not err
        print("a14_sep_bad_body rc=%s %s" % (rc, "OK" if ok else "FAIL"))
        if not ok:
            show("a14_sep_bad_body", rc, got, err)
            fails.append("a14_sep_bad_body")

        # перестановка CAT на отдельном диске: имя устойчиво, индекс — нет
        reordered_data = bytearray(data)
        dcat = a4.a7data.CAT_LBA * SECTOR
        e1d = dcat + 24 + 64 * SWITCH_INDEX
        e2d = dcat + 24 + 64 * A8_INDEX
        reordered_data[e1d:e1d + 64], reordered_data[e2d:e2d + 64] = \
            bytes(reordered_data[e2d:e2d + 64]), bytes(reordered_data[e1d:e1d + 64])
        dcount = struct.unpack_from("<I", reordered_data, dcat + 12)[0]
        struct.pack_into("<I", reordered_data, dcat + 20, 0)
        dcrc = zlib.crc32(bytes(reordered_data[dcat:dcat + 24 + 64 * dcount])) & \
               0xFFFFFFFF
        struct.pack_into("<I", reordered_data, dcat + 20, dcrc)
        reordered_path = os.path.join(tmp_root, "a14_sep_reordered.img")
        io.open(reordered_path, "wb").write(bytes(reordered_data))
        sep_by_name = write_sel(sep1, selector(A14_NAME), pin=False)
        ok, _, _ = run_sep_case(bytes(sep_by_name), reordered_path, tmp_root,
                                "a14_sep_reordered_name", expect_sep(host))
        if not ok:
            fails.append("a14_sep_reordered_name")
        sep_by_index = bytearray(default_img)
        sep_by_index[SELECT_OFF:SELECT_OFF + 13] = a4.A8_MARKER + bytes([A8_INDEX])
        ok, _, _ = run_sep_case(bytes(sep_by_index), reordered_path, tmp_root,
                                "a14_sep_reordered_index", expect_sep(host_sw))
        if not ok:
            fails.append("a14_sep_reordered_index")

        # ---------- A5-установка name_sep: селектор сохраняется, цель загружается ----------
        src_inst = bytearray(write_sel(sep1, selector(A14_NAME), pin=False))
        src_inst[a5.MARKER_OFF:a5.MARKER_OFF + 16] = a5.SRC_MARKER
        tgt_blank = bytearray(a5.TARGET_SECTORS * SECTOR)
        tgt_blank[a5.MARKER_OFF:a5.MARKER_OFF + 16] = a5.TGT_MARKER
        rc, raw, err, disks = a5.boot([bytes(src_inst), bytes(tgt_blank), data],
                                      tmp_root, "a14_sep_a5_inst")
        got = a4.lines_of(raw)
        tgt_after_sep = disks[1]
        inst_ok = (rc == 39 and
                   "CTOS A5 INSTALL OK" in got and
                   "CTOS A5 AUTORUN ALL" in got and
                   tgt_after_sep[SELECT_OFF:SELECT_OFF + 13] == A14_MARKER and
                   not err)
        print("a14_sep_a5_install rc=%s sel=%s %s" %
              (rc, tgt_after_sep[SELECT_OFF:SELECT_OFF + 13] == A14_MARKER,
               "OK" if inst_ok else "FAIL"))
        if not inst_ok:
            show("a14_sep_a5_install", rc, got, err)
            fails.append("a14_sep_a5_install")
        # перезагрузка с установленной цели + отдельный диск данных
        ok, _, _ = run_sep_case(tgt_after_sep, data_path, tmp_root,
                                "a14_sep_a5_reboot", expect_sep(host))
        if not ok:
            fails.append("a14_sep_a5_reboot")

        # ---------- A5-установка name_sep без селектора: A9-автозапуск всех модулей + отдельный диск ----------
        ctmd_sep = sep1[a4.CTMD_OFF:a4.CTMD_OFF + a4.EXPECT_CTMD_LEN]
        host_all = []
        for mod in a4.EXPECT_MODULES:
            host_all += a4.host_event_lines(ctmd_sep, tmp_root,
                                            "a14_sep_auto_" + mod, mod)
        src_auto = bytearray(sep1)
        src_auto[a5.MARKER_OFF:a5.MARKER_OFF + 16] = a5.SRC_MARKER
        tgt_auto = bytearray(a5.TARGET_SECTORS * SECTOR)
        tgt_auto[a5.MARKER_OFF:a5.MARKER_OFF + 16] = a5.TGT_MARKER
        rc, raw, err, disks = a5.boot([bytes(src_auto), bytes(tgt_auto), data],
                                      tmp_root, "a14_sep_a5_auto_inst")
        got = a4.lines_of(raw)
        tgt_after_auto = disks[1]
        inst_auto_ok = (rc == 39 and
                        "CTOS A5 INSTALL OK" in got and
                        "CTOS A5 AUTORUN ALL" in got and
                        not err)
        print("a14_sep_a5_auto_install rc=%s %s" %
              (rc, "OK" if inst_auto_ok else "FAIL"))
        if not inst_auto_ok:
            show("a14_sep_a5_auto_install", rc, got, err)
            fails.append("a14_sep_a5_auto_install")
        ok, _, _ = run_sep_case(tgt_after_auto, data_path, tmp_root,
                                "a14_sep_a5_auto_reboot",
                                expect_sep(host_all))
        if not ok:
            fails.append("a14_sep_a5_auto_reboot")

        print("\nA14 SD NAME: FAILED=%d" % len(fails))
        if fails:
            print("  " + ", ".join(fails))
        return 1 if fails else 0
    finally:
        pass


if __name__ == "__main__":
    sys.exit(main())
