# -*- coding: utf-8 -*-
"""A4a/A6/A7/A8: честная приёмка загрузчика и нативного рантайма CtOS в QEMU.

Проверяется ровно то, что реально исполняется:
  1. детерминированная сборка образа ДВАЖДЫ в разных TEMP-каталогах
     (свежий as/ld/gcc/objcopy каждый раз) — байты обязаны совпасть;
  2. positive: MBR -> EDD stage2 -> CTMD (CRC каталога) -> PM-рантайм,
     тот же native_rt.c что и на хосте, Event-линии COM1 байт-в-байт
     сверяются с хост-запуском `native_rt.exe --module memmgr`;
     isa-debug-exit даёт rc=39 (AX=0x13);
  3a. A6: маркер CTOS-AUTORUN-A6 в MBR+0x190 заставляет PM вызвать main()
      четырежды — по разу на каждый модуль CTMD; каждая event-последовательность
      байт-в-байт сверяется с хост-запуском;
  3b. A7: второй диск с маркером CTOS-DATA-A7! и каталогом в LBA8..71: stage2
      проверяет magic/version/count/CRC и печатает CTOS A7 DATA OK; порча
      каталога даёт честный rc=35, сбитый маркер — тихий старт без строки;
  3c. A8: маркер CTOS-DISK-A8 в MBR+0x1A0 и индекс записи каталога запускают
      один выбранный модуль из CAT-области; шим собирает синтетический CTMD,
      COM1 байт-в-байт сверяется с хост-запуском тех же байт; порча тела даёт
      честный rc=41, сбитый индекс — отказ без MODULE-строки;
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
DATA_BUILDER = os.path.join(REPO, "CtOs", "native", "build_data_image.py")
DATA_DIR = os.path.dirname(DATA_BUILDER)
if DATA_DIR not in sys.path:
    sys.path.insert(0, DATA_DIR)
import build_data_image as a7data  # noqa: E402
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
EXPECT_S2_LEN = 2040
EXPECT_INSTALL_LEN = 1223   # installer без хвостовых нулей (A9; файл .bin — 1224 Б)
EXPECT_CTMD_LEN = 28425
EXPECT_PM_LEN = 22292        # слот бинарника в образе
EXPECT_PM_TAIL_LEN = 22289   # последний ненулевой байт + 1
EXPECT_CTMD_MD5 = "110b54e786544c561b64132e7557812d"
EXPECT_IMAGE_MD5 = "59285f03e4c60c512cbb9c7963f1748f"
AUTORUN_MARKER_OFF = 0x190
AUTORUN_MARKER = b"CTOS-AUTORUN-A6\x00"
A7_MARKER_OFF = 0x180
A7_MARKER = b"CTOS-DATA-A7!"
A7_CAT_OFF = 8 * SECTOR
A7_LINE = "CTOS A7 DATA OK"
A8_SELECT_OFF = 0x1A0
A8_MARKER = b"CTOS-DISK-A8"
A8_INDEX_OFF = 0x1AC
A8_INDEX = 2                 # syscall.CTS — третий модуль CAT-каталога
A8_MODULES = ("memmgr.CTS", "sched.CTS", "syscall.CTS", "stage1.CTS")
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


def build_data_image(tmp_root):
    """Свежий диск данных A7 (32 МиБ) для двухдискового QEMU-гейта."""
    d = os.path.join(tmp_root, "data_disk")
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "data.img")
    clean(out)
    r = subprocess.run([sys.executable, "-X", "utf8", DATA_BUILDER, out],
                       capture_output=True, encoding="utf-8",
                       errors="replace", timeout=180)
    if r.returncode:
        raise RuntimeError("A7 data build: %s %s" % (r.stdout, r.stderr))
    return io.open(out, "rb").read(), out


def a8_ctmd(data_img, index):
    """Собрать тот же синтетический CTMD, что собирает PM-шим из CAT-области."""
    cat = data_img[a7data.CAT_LBA * SECTOR:
                   (a7data.CAT_LBA + a7data.CAT_SECTORS) * SECTOR]
    ent = cat[24 + 64 * index:24 + 64 * (index + 1)]
    if ent[0] != 1:
        raise RuntimeError("A8: запись %d не APPS" % index)
    name = ent[1:16].split(b"\x00", 1)[0].decode("ascii")
    size, crc, body_off = struct.unpack_from("<III", ent, 24)
    body = cat[body_off:body_off + size]
    rec = bytearray(48)
    rec[0:len(name)] = name.encode("ascii")
    struct.pack_into("<III", rec, 32, 60, size, crc)
    out = b"CTMD" + struct.pack("<II", 1, 1) + bytes(rec) + body
    return out, name


def boot_log(data, tmp_root, tag, data_disk=None):
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
           "-drive", "file=" + img + ",format=raw,if=ide,index=0,media=disk"]
    if data_disk:
        cmd += ["-drive", "file=" + data_disk +
                ",format=raw,if=ide,index=1,media=disk"]
    cmd += ["-boot", "order=c",
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


def host_event_lines(ctmd, tmp_root, tag, module="memmgr"):
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
    r = subprocess.run([host_exe(), "--module", module, ctmd_path, ev],
                       capture_output=True, encoding="utf-8",
                       errors="replace", timeout=60)
    if r.returncode:
        raise RuntimeError("host --module %s: %s %s" %
                           (module, r.stdout, r.stderr))
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

        # ---------- 3a. A6: маркер автозапуска -> все модули CTMD в PM ----------
        autorun = bytearray(a)
        autorun[AUTORUN_MARKER_OFF:
                AUTORUN_MARKER_OFF + len(AUTORUN_MARKER)] = AUTORUN_MARKER
        rc, raw, err = boot_log(bytes(autorun), tmp_root, "autorun")
        got = lines_of(raw)
        want = list(POS_PREAMBLE)
        counts = []
        for name in EXPECT_MODULES:
            lines = host_event_lines(ctmd, tmp_root, "a6_" + name, name)
            counts.append("%s=%d" % (name, len(lines)))
            want += lines
        auto_ok = (rc == RC_OK and got == want and not err)
        print("A6 autorun: rc=%s lines=%d (ожидалось %d), "
              "COM1==host(x%d): %s  %s" %
              (rc, len(got), len(want), len(EXPECT_MODULES),
               ",".join(counts), "OK" if auto_ok else "FAIL"))
        if not auto_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("A6 autorun")

        # ---------- 3b. A7: диск данных с папками и машинным каталогом ----------
        data_img, data_path = build_data_image(tmp_root)
        rc, raw, err = boot_log(a, tmp_root, "a7", data_path)
        got = lines_of(raw)
        # A7 печатается после CTMD ALL OK, но до перехода в PM.
        want = (list(POS_PREAMBLE[:7]) + [A7_LINE] +
                list(POS_PREAMBLE[7:]) + EXPECT_HOST_EVENTS)
        a7_ok = (rc == RC_OK and got == want and not err)
        print("A7 data disk: rc=%s lines=%d (ожидалось %d), CAT+events: %s  %s" %
              (rc, len(got), len(want), A7_LINE in got,
               "OK" if a7_ok else "FAIL"))
        if not a7_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("A7 data disk")

        # A7 негатив: порча записи каталога -> честный отказ до PM.
        bad_data = bytearray(data_img)
        bad_data[A7_CAT_OFF + 24 + 1] ^= 0x01
        bad_path = os.path.join(os.path.dirname(data_path), "data_bad.img")
        clean(bad_path)
        io.open(bad_path, "wb").write(bytes(bad_data))
        rc, raw, err = boot_log(a, tmp_root, "a7_bad", bad_path)
        got = lines_of(raw)
        a7_bad_ok = (rc == RC_REFUSE and "CTOS A7 DATA BAD" in got and
                     "PM OK" not in got and "CTOS A4a EXEC" not in got)
        print("neg A7 catalog: rc=%s diag=%s  %s" %
              (rc, "CTOS A7 DATA BAD" in got,
               "OK" if a7_bad_ok else "FAIL"))
        if not a7_bad_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("neg A7 catalog")

        # A7 негатив: сбитый маркер роли -> диск не считается диском данных.
        bad_role = bytearray(data_img)
        bad_role[A7_MARKER_OFF] ^= 0x20
        role_path = os.path.join(os.path.dirname(data_path), "data_role.img")
        clean(role_path)
        io.open(role_path, "wb").write(bytes(bad_role))
        rc, raw, err = boot_log(a, tmp_root, "a7_role", role_path)
        got = lines_of(raw)
        role_ok = (rc == RC_OK and got == POS_LINES and A7_LINE not in got)
        print("neg A7 role: rc=%s без A7-строки=%s  %s" %
              (rc, A7_LINE not in got, "OK" if role_ok else "FAIL"))
        if not role_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("neg A7 role")

        # ---------- 3c. A8: выбранный модуль с диска данных ----------
        a8_img = bytearray(a)
        sel = A8_MARKER + bytes([A8_INDEX])
        a8_img[A8_SELECT_OFF:A8_SELECT_OFF + len(sel)] = sel
        ctmd_a8, a8_name = a8_ctmd(data_img, A8_INDEX)
        host_a8 = host_event_lines(ctmd_a8, tmp_root, "a8_" + a8_name, a8_name)
        rc, raw, err = boot_log(bytes(a8_img), tmp_root, "a8", data_path)
        got = lines_of(raw)
        want = (list(POS_PREAMBLE[:7]) + [A7_LINE] +
                list(POS_PREAMBLE[7:]) + host_a8)
        a8_ok = (rc == RC_OK and got == want and not err)
        print("A8 module %s: rc=%s lines=%d (ожидалось %d), COM1==host  %s" %
              (a8_name, rc, len(got), len(want), "OK" if a8_ok else "FAIL"))
        if not a8_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("A8 disk module")

        # A8 негатив: порча тела выбранного модуля (CRC каталога не меняется)
        # обязана дать runtime-fatal до нормальных event'ов.
        ent_off = A7_CAT_OFF + 24 + 64 * A8_INDEX
        body_off = struct.unpack_from("<I", data_img, ent_off + 32)[0]
        bad_body = bytearray(data_img)
        bad_body[A7_CAT_OFF + body_off + 3] ^= 0x01
        body_path = os.path.join(os.path.dirname(data_path), "data_a8_bad.img")
        clean(body_path)
        io.open(body_path, "wb").write(bytes(bad_body))
        rc, raw, err = boot_log(bytes(a8_img), tmp_root, "a8_body", body_path)
        got = lines_of(raw)
        # lines_of() декодирует COM1 как ASCII: русский текст диагностики
        # превращается в replacement-символы, поэтому ищем ASCII-префикс.
        body_bad_ok = (rc == RC_FATAL and
                       any(s.startswith("FATAL: CTMD:") for s in got) and
                       not any(s.startswith("OPS ") for s in got))
        print("neg A8 body: rc=%s diag=%s  %s" %
              (rc, body_bad_ok, "OK" if body_bad_ok else "FAIL"))
        if not body_bad_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("neg A8 body")

        # A8 негатив: сбитый индекс -> не выполняем чужой модуль, честно
        # возвращаемся к A4a/A6-пути (диск данных при этом на месте).
        bad_idx = bytearray(a8_img)
        bad_idx[A8_INDEX_OFF] = 9
        rc, raw, err = boot_log(bytes(bad_idx), tmp_root, "a8_index", data_path)
        got = lines_of(raw)
        idx_ok = (rc == RC_OK and got == want[:len(want) - len(host_a8)] +
                  EXPECT_HOST_EVENTS)
        print("neg A8 index: rc=%s fallback=%s  %s" %
              (rc, idx_ok, "OK" if idx_ok else "FAIL"))
        if not idx_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("neg A8 index")

        # A8 негатив: маркер есть, а диска данных нет — шим обязан честно
        # отказать, а не взять модуль из загрузочного контейнера.
        rc, raw, err = boot_log(bytes(a8_img), tmp_root, "a8_nodata")
        got = lines_of(raw)
        nodata_ok = (rc == RC_FATAL and "CTOS A8 NO DATA" in got and
                     A7_LINE not in got)
        print("neg A8 no disk: rc=%s diag=%s  %s" %
              (rc, "CTOS A8 NO DATA" in got,
               "OK" if nodata_ok else "FAIL"))
        if not nodata_ok:
            print("  LOG:", show_lines(raw))
            if err:
                print("  ERR:", err)
            fails.append("neg A8 no disk")

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
    print("BOOT IMAGE OK A4a/A6/A7/A8 (+A9-установщик): детерминированный образ, QEMU rc=39, "
          "COM1 байт-в-байт совпадает с host native_rt (A4a: memmgr, A6: все 4 "
          "модуля CTMD, A7: диск данных с папками, A8: выбранный модуль с диска), "
          "отказы rc=35 и runtime-fatal rc=41. QEMU — контрольная точка, "
          "на R3700 НЕ принято.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
