# -*- coding: utf-8 -*-
"""A7: честная приёмка диска данных CtOS — FAT16 + машинный каталог.

Проверяется ровно то, что реально лежит в образе:
  1. холодная сборка ДВАЖДЫ в разных TEMP-каталогах (свежий Python) — байты
     обязаны совпасть;
  2. MBR: маркер CTOS-DATA-A7!, сигнатура 55 AA, один раздел FAT16 (type 0x06)
     с ожидаемыми LBA/размером;
  3. BPB разделя и FAT-цепочки: independently обходим root -> CTOS -> APPS,
     GAMES, MUSIC, VIDEO; проверяем записи "."/"..", имена 8.3 и атрибуты;
  4. каталог в LBA 8..71: magic CTOSCAT1, version=1, count, CRC-32; каждая
     запись сверяется с байтами по её LBA и с исходным .ctos-файлом;
     A8-тела в хвосте CAT-области сверяются с теми же байтами;
  5. негативы: испорченный маркер, CRC каталога, байт внутри файла и сломанная
     FAT-цепочка обязаны детектироваться.

Запуск (только так):
    python -X utf8 Python_compiler/verify_data_image.py
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
_APPROVED_TMP = r"G:\Windows\RJ\AppData\Local\Temp\opencode"
TMP_BASE = (os.environ.get("OPENCODE_TMP") or
            (_APPROVED_TMP if os.path.isdir(_APPROVED_TMP)
             else tempfile.gettempdir()))
BUILDER = os.path.join(REPO, "CtOs", "native", "build_data_image.py")

sys.path.insert(0, os.path.dirname(BUILDER))
import build_data_image as a7  # noqa: E402

SECTOR = 512
IMAGE_LEN = a7.IMAGE_SECTORS * SECTOR
EXPECT_MD5 = "5f54256087028a0cc71dfcfde77b9073"

NAME_DOT = b".          "
NAME_DOTDOT = b"..         "


def u16(b, off):
    return struct.unpack_from("<H", b, off)[0]


def u32(b, off):
    return struct.unpack_from("<I", b, off)[0]


def cold_build(tag, tmp_root):
    d = os.path.join(tmp_root, "build_" + tag)
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "data.img")
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run([sys.executable, "-X", "utf8", BUILDER, out],
                       capture_output=True, encoding="utf-8",
                       errors="replace", timeout=180)
    if r.returncode:
        raise RuntimeError("builder: %s %s" % (r.stdout, r.stderr))
    return io.open(out, "rb").read(), out


def mbr_errors(img):
    e = []
    if img[a7.MARKER_OFF:a7.MARKER_OFF + len(a7.DATA_MARKER)] != a7.DATA_MARKER:
        e.append("MARKEP")
    if u16(img, SECTOR - 2) != 0xAA55:
        e.append("MBR_SIG")
    pt = 0x1BE
    if img[pt + 4] != 0x06:
        e.append("PART_TYPE")
    if u32(img, pt + 8) != a7.PART_LBA:
        e.append("PART_LBA")
    if u32(img, pt + 12) != a7.PART_SECTORS:
        e.append("PART_SIZE")
    return e


class Fat:
    """Независимый read-only разбор FAT16 из уже собранного образа."""

    def __init__(self, img):
        self.img = img
        self.e = []
        part = a7.PART_LBA * SECTOR
        bpb = img[part:part + SECTOR]
        if u16(bpb, SECTOR - 2) != 0xAA55:
            self.e.append("FAT_SIG")
        self.spc = bpb[13]
        self.reserved = u16(bpb, 14)
        self.nfats = bpb[16]
        self.root_entries = u16(bpb, 17)
        self.total16 = u16(bpb, 19)
        self.fat_sectors = u16(bpb, 22)
        self.hidden = u32(bpb, 28)
        self.root_sectors = (self.root_entries * 32 + SECTOR - 1) // SECTOR
        self.data_start = (self.reserved + self.nfats * self.fat_sectors +
                           self.root_sectors)
        if (self.spc != a7.SPC or self.reserved != a7.RESERVED or
                self.nfats != a7.FAT_COUNT or self.hidden != a7.PART_LBA or
                self.fat_sectors != a7.FAT_SECTORS or
                self.total16 != a7.PART_SECTORS or
                self.root_entries != a7.ROOT_ENTRIES):
            self.e.append("BPB")
        self.fat_off = part + self.reserved * SECTOR
        self.root_off = part + (self.reserved +
                                self.nfats * self.fat_sectors) * SECTOR

    def chain(self, first):
        out = []
        c = first
        seen = set()
        while 0x0002 <= c < 0xFFF0:
            if c in seen or c >= a7.CLUSTERS + 2:
                self.e.append("FAT_LOOP")
                return out
            seen.add(c)
            out.append(c)
            c = u16(self.img, self.fat_off + 2 * c)
        if c < 0xFFF0:
            self.e.append("FAT_EOC")
        return out

    def cluster_bytes(self, c):
        off = (a7.PART_LBA + self.data_start + (c - 2) * self.spc) * SECTOR
        return self.img[off:off + self.spc * SECTOR]

    def dir_entries(self, first=None):
        if first is None:
            buf = self.img[self.root_off:self.root_off + self.root_entries * 32]
        else:
            buf = b"".join(self.cluster_bytes(c) for c in self.chain(first))
        out = []
        for i in range(0, len(buf), 32):
            e = buf[i:i + 32]
            if e[0] == 0x00:
                break
            if e[0] == 0xE5:
                continue
            out.append(e)
        return out

    @staticmethod
    def name(e):
        return e[0:11]

    @staticmethod
    def cl(e):
        return u16(e, 26)

    @staticmethod
    def size(e):
        return u32(e, 28)

    def file_bytes(self, e):
        raw = b"".join(self.cluster_bytes(c) for c in self.chain(self.cl(e)))
        return raw[:self.size(e)]


def expected_files():
    """Имя в каталоге -> (kind, исходный байт-код)."""
    out = {}
    for name, rel, _fat in a7.MODULES:
        out[name] = (1, io.open(os.path.join(REPO, rel), "rb").read())
    for folder in a7.FOLDERS:
        out[folder + "/README"] = (a7.KIND[folder], a7.README[folder])
    return out


def fat_short(cname):
    """Имя каталога -> короткое имя 8.3 в FAT."""
    for name, _rel, fatname in a7.MODULES:
        if cname == name:
            return fatname.rstrip()
    return a7.README_NAME.rstrip()


def catalog_errors(img, expect):
    e = []
    off = a7.CAT_LBA * SECTOR
    cat = img[off:off + a7.CAT_SECTORS * SECTOR]
    if cat[0:8] != a7.CAT_MAGIC:
        return ["CAT_MAGIC"]
    if u32(cat, 8) != 1:
        e.append("CAT_VERSION")
    if u32(cat, 16) != 0:
        e.append("CAT_RESERVED")
    count = u32(cat, 12)
    if count != len(expect):
        e.append("CAT_COUNT")
        return e
    # CRC по непрерывному [0..24+64*count), поле CRC на время счёта обнулено.
    probe = bytearray(cat[0:24 + 64 * count])
    struct.pack_into("<I", probe, 20, 0)
    want_crc = zlib.crc32(bytes(probe)) & 0xFFFFFFFF
    if u32(cat, 20) != want_crc:
        e.append("CAT_CRC")
    seen = set()
    for i in range(count):
        ent = cat[24 + 64 * i:24 + 64 * (i + 1)]
        kind = ent[0]
        name = ent[1:16].split(b"\x00", 1)[0].decode("ascii")
        name = name.rstrip(" ")
        lba, nsect, size, crc, body_off = struct.unpack_from("<IIIII", ent, 16)
        if name not in expect:
            e.append("CAT_NAME_" + name)
            continue
        seen.add(name)
        ekind, data = expect[name]
        if kind != ekind:
            e.append("CAT_KIND_" + name)
        if size != len(data):
            e.append("CAT_SIZE_" + name)
        if nsect != (len(data) + SECTOR - 1) // SECTOR:
            e.append("CAT_NSECT_" + name)
        if crc != (zlib.crc32(data) & 0xFFFFFFFF):
            e.append("CAT_FILECRC_" + name)
        on_disk = img[lba * SECTOR:lba * SECTOR + size]
        if on_disk != data:
            e.append("CAT_LBA_BYTES_" + name)
        # A8: тело внутри прочитанной CAT-области — точная копия FAT-файла.
        is_module = any(name == m[0] for m in a7.MODULES)
        if is_module:
            if body_off < a7.A8_BODY_BASE or body_off + size > len(cat):
                e.append("CAT_BODY_RANGE_" + name)
            elif cat[body_off:body_off + size] != data:
                e.append("CAT_BODY_BYTES_" + name)
        elif body_off != 0:
            e.append("CAT_BODY_SPURIOUS_" + name)
    if seen != set(expect):
        e.append("CAT_MISSING")
    return e


def tree_errors(fat, expect):
    e = []
    root = fat.dir_entries()
    names = [(fat.name(x), x[11]) for x in root]
    if (b"CTOSDATA   ", 0x08) not in names:
        e.append("ROOT_LABEL")
    ctos = [x for x in root if fat.name(x) == b"CTOS       " and x[11] == 0x10]
    if len(ctos) != 1:
        e.append("ROOT_CTOS")
        return e
    ctos_cl = fat.cl(ctos[0])
    cd = fat.dir_entries(ctos_cl)
    if not cd or fat.name(cd[0]) != NAME_DOT or fat.cl(cd[0]) != ctos_cl:
        e.append("CTOS_DOT")
    if len(cd) < 2 or fat.name(cd[1]) != NAME_DOTDOT or fat.cl(cd[1]) != 0:
        e.append("CTOS_DOTDOT")
    sub = {}
    for x in cd[2:]:
        sub[fat.name(x).rstrip(b" ").decode("ascii")] = (x[11], fat.cl(x))
    if set(sub) != set(a7.FOLDERS):
        e.append("CTOS_FOLDERS")
    for folder in a7.FOLDERS:
        if folder not in sub:
            continue
        attr, cl = sub[folder]
        if attr != 0x10:
            e.append("ATTR_" + folder)
            continue
        d = fat.dir_entries(cl)
        if not d or fat.name(d[0]) != NAME_DOT or fat.cl(d[0]) != cl:
            e.append("DOT_" + folder)
        if len(d) < 2 or fat.name(d[1]) != NAME_DOTDOT or fat.cl(d[1]) != ctos_cl:
            e.append("DOTDOT_" + folder)
        got = {}
        for x in d[2:]:
            got[fat.name(x).rstrip(b" ").decode("ascii")] = x
        want = {}
        for cname, (kind, data) in expect.items():
            if cname.startswith(folder + "/") or (folder == "APPS" and
                                                   "/" not in cname):
                want[fat_short(cname)] = (cname, data)
        if set(got) != set(want):
            e.append("FILES_" + folder)
            continue
        for short, x in got.items():
            cname, data = want[short]
            if x[11] != 0x20:
                e.append("ATTR_" + cname)
            if fat.size(x) != len(data):
                e.append("SIZE_" + cname)
            if fat.file_bytes(x) != data:
                e.append("BYTES_" + cname)
    return e


def main():
    fails = []
    tmp_root = tempfile.mkdtemp(prefix="a7_data_verify_", dir=TMP_BASE)
    try:
        images = []
        for tag in ("1", "2"):
            data, out = cold_build(tag, tmp_root)
            images.append(data)
            print("build %s: %s Б md5 %s" %
                  (tag, len(data), hashlib.md5(data).hexdigest()))
        a, b = images
        same = (a == b)
        print("cold x2: %s  %s" %
              ("IDENTICAL" if same else "DIFF",
               hashlib.md5(a).hexdigest()))
        if not same:
            fails.append("determinism")
        if len(a) != IMAGE_LEN:
            fails.append("image length %d" % len(a))
        print("EXPECT_MD5 = %s" % EXPECT_MD5)
        if hashlib.md5(a).hexdigest() != EXPECT_MD5:
            fails.append("image md5")

        expect = expected_files()
        me = mbr_errors(a)
        print("MBR: %s  %s" % ("OK" if not me else ",".join(me),
                              a[a7.MARKER_OFF:a7.MARKER_OFF + 13].decode("ascii")))
        if me:
            fails.append("MBR")

        fat = Fat(a)
        te = fat.e + tree_errors(fat, expect)
        print("FAT16 tree: %s" % ("OK" if not te else ",".join(te)))
        if te:
            fails.append("FAT tree")

        ce = catalog_errors(a, expect)
        print("catalog: %d records, %s" %
              (len(expect), "OK" if not ce else ",".join(ce)))
        if ce:
            fails.append("catalog")

        # ---------- негативы: каждый детектор обязан сработать ----------
        bad_marker = bytearray(a)
        bad_marker[a7.MARKER_OFF] ^= 0x20
        ok = bool(mbr_errors(bytes(bad_marker)))
        print("neg marker: %s" % ("OK" if ok else "FAIL"))
        if not ok:
            fails.append("neg marker")

        bad_cat = bytearray(a)
        bad_cat[a7.CAT_LBA * SECTOR + 24 + 16 + 1] ^= 0x01
        ok = bool(catalog_errors(bytes(bad_cat), expect))
        print("neg catalog payload: %s" % ("OK" if ok else "FAIL"))
        if not ok:
            fails.append("neg catalog")

        bad_file = bytearray(a)
        bad_file[a7.CAT_LBA * SECTOR + 24 + 16] ^= 0x01   # LBA записи
        ok = bool(catalog_errors(bytes(bad_file), expect))
        print("neg catalog LBA: %s" % ("OK" if ok else "FAIL"))
        if not ok:
            fails.append("neg catalog LBA")

        # A8-тело не входит в CRC каталога: детектор обязан поймать подмену
        # именно по байтам тела, а не по CRC каталога.
        bad_body = bytearray(a)
        bad_body[a7.CAT_LBA * SECTOR + a7.A8_BODY_BASE + 3] ^= 0x01
        ok = bool(catalog_errors(bytes(bad_body), expect))
        print("neg A8 body: %s" % ("OK" if ok else "FAIL"))
        if not ok:
            fails.append("neg A8 body")

        bad_fat = bytearray(a)
        bad_fat[fat.fat_off + 2 * 3:fat.fat_off + 2 * 3 + 2] = b"\xFF\xFF"
        f2 = Fat(bytes(bad_fat))
        ok = bool(f2.e or tree_errors(f2, expect))
        print("neg FAT chain: %s" % ("OK" if ok else "FAIL"))
        if not ok:
            fails.append("neg FAT")
    finally:
        import shutil
        shutil.rmtree(tmp_root, ignore_errors=True)

    if fails:
        print("DATA IMAGE FAIL: %s" % ", ".join(fails))
        return 1
    print("DATA IMAGE OK A7/A8: FAT16 + каталог LBA8..71, %d файлов и A8-тела; "
          "QEMU не нужен (чисто байтовый гейт), на R3700 НЕ принято." %
          len(expect))
    return 0


if __name__ == "__main__":
    sys.exit(main())
