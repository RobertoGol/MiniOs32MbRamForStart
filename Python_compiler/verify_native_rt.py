# -*- coding: utf-8 -*-
"""A1/A2 (bring-up Ф2): честная сверка нативного интерпретатора с ctos_vm.py.

A1 — подмножество опкодов ядра: PORT/опкоды/ячейки + CRC-негатив.
A2 — NID-слой (файл 0x130..0x137, контекст 0x150..0x152, таймер 0x153/0x154):
     сверка последовательностей SYSCALL/TICK/NET/PORT, счётчиков и байт
     артефакта, плюс честные негативы (брак порядка syscall / пустой аргумент).
     Полная самосборка S(S_T) нативом обязана дать тот же T, что и VM.

Запуск:
    python -X utf8 Python_compiler/verify_native_rt.py
"""
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VM = os.path.join(REPO, "CtOs-Emu", "ctos_vm.py")
NATIVE_DIR = os.path.join(REPO, "CtOs", "native")
SRC = os.path.join(NATIVE_DIR, "native_rt.c")
# билд уходит во временный каталог, чтобы не засорять tracked-дерево .exe
EXE = os.path.join(tempfile.gettempdir(), "ctos_native_rt", "native_rt.exe")

# NID -> метка в трассе VM (строка OP_SYSCALL[<метка>]: ...)
NIDMAP = {
    "FILE_BEGIN":"130", "FILE_PUT":"131", "FILE_U16":"132", "FILE_END":"133",
    "FILE_U8":"134", "FILE_SEAL":"135", "FILE_SEEK":"136", "FILE_GET":"137",
    "WORK_CTX_SAVE":"150", "WORK_CTX_RESTORE":"151", "WORK_CTX_YIELD":"152",
    "TIMER_ARM":"153", "TIMER_RET":"154",
}
# сетевые маркеры VM (1-байтные no-op) -> код опкода в events натива
NETMAP = {
    "net_all":"20", "net_up":"21", "net_down":"22", "net_flush":"23",
    "net_arp":"24", "go":"25", "trace":"26",
}

PORT_RE = re.compile(
    r"OP_OUTCELL(?:_V)?: порт 0x([0-9A-Fa-f]+) <- "
    r"(?:cell\[0x[0-9A-Fa-f]+\] = )?0x([0-9A-Fa-f]+)")
NID_RE = re.compile(r"OP_SYSCALL\[([A-Z_0-9]+)\]:")
TICK_RE = re.compile(r"SCHED-TICK:.*?\bpc=0x([0-9A-Fa-f]+)")
NET_RE = re.compile(r"сеть:\s*([a-z_]+)")
OPS_RE = re.compile(r"(\d+) опкод")
CELLS_RE = re.compile(r"ячеек: (\d+)")

# (имя, относительный путь, исходник, сверять events, ждать артефакт)
CORE = [
    ("memmgr",       "CtOs/memmgr.ctos",               None, True,  False),
    ("kernel_sched", "CtOs/kernel_sched.ctos",         None, True,  False),
    ("syscall_test", "Python_compiler/syscall_test.ctos", None, True, True),
    ("schedF",       "Python_compiler/schedF_test.ctos",  None, True, False),
    ("schedT",       "Python_compiler/schedT_test.ctos",  None, True, False),
]
SELFHOST = (
    "stage1_selfhost",
    "Compiler/stage1_compiler.ctos",
    "Python_compiler/pos_wc14v3ring.words",
)
# честные негативы: оба исполнителя obligatory отказываются
NEGATIVES = [
    ("probe_seek",           "Python_compiler/probe_seek.ctos",
     None, "FILE_SEEK до FILE_BEGIN"),
    ("neg_ctx1",             "Python_compiler/neg_ctx1.ctos",
     None, "WORK_CTX_YIELD"),
    ("syscall_endfail",      "Python_compiler/syscall_test_endfail.ctos",
     None, "FILE_END"),
    ("syscall_orderfail",    "Python_compiler/syscall_test_orderfail.ctos",
     None, "FILE_PUT до FILE_BEGIN"),
]
# ожидаемые итоги самосборки (TKT-052 / W-122)
EXPECT_T_LEN = 13084
EXPECT_T_MD5 = "30a90f3ff440ec249a132f58ee5a040a"


def clean(p):
    if os.path.exists(p):
        os.remove(p)


def vm_events(trace):
    ev = []
    with io.open(trace, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = PORT_RE.search(line)
            if m:
                ev.append("PORT %s %s" % (m.group(1).upper(), m.group(2).upper()))
                continue
            m = NID_RE.search(line)
            if m:
                ev.append("SYSCALL " + NIDMAP[m.group(1)])
                continue
            m = TICK_RE.search(line)
            if m:
                ev.append("TICK " + m.group(1).upper())
                continue
            m = NET_RE.search(line)
            if m:
                ev.append("NET " + NETMAP[m.group(1)])
    return ev


def native_events(path):
    ev, counts = [], []
    if not os.path.exists(path):
        return ev, counts
    with io.open(path, encoding="ascii") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("OPS "):
                counts.append(s)
            else:
                ev.append(s)
    return ev, counts


def vm_counts(stdout):
    mo, mc = OPS_RE.search(stdout), CELLS_RE.search(stdout)
    if not mo or not mc:
        return None
    return "OPS %s CELLS %s" % (mo.group(1), mc.group(1))


def run_vm(binp, src, trace, steps=None):
    outp = binp + ".out"
    clean(outp)
    cmd = [sys.executable, "-X", "utf8", VM, binp, "--trace", trace]
    if src:
        cmd += ["--source", src]
    if steps:
        cmd += ["--steps", str(steps)]
    return subprocess.run(cmd, capture_output=True, encoding="utf-8",
                          errors="replace", timeout=1200)


def run_native(binp, src, events):
    outp = binp + ".out"
    clean(outp)
    cmd = [EXE, binp, events]
    if src:
        cmd += [src]
    return subprocess.run(cmd, capture_output=True, encoding="utf-8",
                          errors="replace", timeout=1200)


def stage_pair(tmp, name, rel, src, tag):
    """Копия бинаря в отдельные каталоги VM/native: .out не пересекаются."""
    vdir = os.path.join(tmp, tag + "_vm")
    ndir = os.path.join(tmp, tag + "_nat")
    os.makedirs(vdir, exist_ok=True)
    os.makedirs(ndir, exist_ok=True)
    vb = os.path.join(vdir, name)
    nb = os.path.join(ndir, name)
    shutil.copy2(os.path.join(REPO, rel), vb)
    shutil.copy2(os.path.join(REPO, rel), nb)
    return vb, nb


def first_diff(a, b, label):
    if a == b:
        return
    print("  %s: первое расхождение" % label)
    for i in range(max(len(a), len(b))):
        x = a[i] if i < len(a) else "<нет>"
        y = b[i] if i < len(b) else "<нет>"
        if x != y:
            print("    @%d: VM=%s NAT=%s" % (i, x, y))
            print("    VM ctx : %s" % a[max(0, i-2):i+3])
            print("    NAT ctx: %s" % b[max(0, i-2):i+3])
            break


def ensure_exe():
    os.makedirs(os.path.dirname(EXE), exist_ok=True)
    if (os.path.exists(EXE) and
            os.path.getmtime(EXE) >= os.path.getmtime(SRC)):
        return
    print("build: gcc -O2 -std=c11 ...")
    r = subprocess.run(["gcc", "-O2", "-std=c11", "-Wall", "-Wextra",
                        "-o", EXE, SRC], capture_output=True, encoding="utf-8")
    if r.returncode:
        raise RuntimeError("gcc: %s %s" % (r.stdout, r.stderr))


def main():
    ensure_exe()
    fails = []
    tmp = tempfile.mkdtemp(prefix="native_verify_")
    try:
        # ---------- A1 + A2 ядро/сервисы ----------
        for tag, rel, src, want_events, want_art in CORE:
            name = os.path.basename(rel)
            vb, nb = stage_pair(tmp, name, rel, src, tag)
            vt = os.path.join(tmp, tag + ".vm.trace")
            ne = os.path.join(tmp, tag + ".nat.events")
            rv = run_vm(vb, src, vt)
            rn = run_native(nb, src, ne)
            vc = vm_counts(rv.stdout)
            vv = vm_events(vt) if want_events else []
            nv, nc = native_events(ne)

            ok = (rv.returncode == 0 and rn.returncode == 0 and
                  vc is not None and nc == [vc])
            if want_events:
                ok = ok and (nv == vv)
            art_ok = True
            if want_art:
                a = io.open(vb + ".out", "rb").read() if os.path.exists(vb + ".out") else None
                b = io.open(nb + ".out", "rb").read() if os.path.exists(nb + ".out") else None
                art_ok = (a is not None and a == b)
                ok = ok and art_ok

            print("%-16s rc=%d/%d events=%d/%d counts=%s art=%s  %s" % (
                tag, rv.returncode, rn.returncode, len(nv), len(vv),
                nc[0] if nc else "-", "OK" if art_ok else "DIFF",
                "OK" if ok else "FAIL"))
            if want_events and nv != vv:
                first_diff(vv, nv, "events")
            if nc and vc and nc != [vc]:
                print("  counts VM=%s NAT=%s" % (vc, nc))
            if rn.returncode:
                print("  NATIVE ERR:", rn.stderr.strip()[:300])
            if not ok:
                fails.append(tag)

        # ---------- A2 полная самосборка S(S_T) ----------
        tag, rel, src = SELFHOST
        name = os.path.basename(rel)
        vb, nb = stage_pair(tmp, name, rel, src, tag)
        vt = os.path.join(tmp, tag + ".vm.trace")
        ne = os.path.join(tmp, tag + ".nat.events")
        rv = run_vm(vb, src, vt, steps=50000000)
        rn = run_native(nb, src, ne)
        a = io.open(vb + ".out", "rb").read() if os.path.exists(vb + ".out") else None
        b = io.open(nb + ".out", "rb").read() if os.path.exists(nb + ".out") else None
        vc, nc = vm_counts(rv.stdout), native_events(ne)[1]
        vv, nv = vm_events(vt), native_events(ne)[0]
        md5 = hashlib.md5(b).hexdigest() if b else "-"
        ok = (rv.returncode == 0 and rn.returncode == 0 and
              a is not None and a == b and
              a is not None and len(a) == EXPECT_T_LEN and
              md5 == EXPECT_T_MD5 and
              vc is not None and nc == [vc] and nv == vv)
        print("%-16s rc=%d/%d T=%sБ md5=%s events=%d/%d counts=%s art=%s  %s" % (
            tag, rv.returncode, rn.returncode,
            len(b) if b else "-", md5, len(nv), len(vv),
            nc[0] if nc else "-", "OK" if (a is not None and a == b) else "DIFF",
            "OK" if ok else "FAIL"))
        if nv != vv:
            first_diff(vv, nv, "events")
        if rn.returncode:
            print("  NATIVE ERR:", rn.stderr.strip()[:300])
        if not ok:
            fails.append(tag)

        # ---------- честные негативы ----------
        for tag, rel, src, needle in NEGATIVES:
            name = os.path.basename(rel)
            vb, nb = stage_pair(tmp, name, rel, src, "neg_" + tag)
            rv = run_vm(vb, src, os.path.join(tmp, "neg_" + tag + ".vm.trace"))
            rn = run_native(nb, src, os.path.join(tmp, "neg_" + tag + ".nat.events"))
            vtext = rv.stdout + rv.stderr
            ntext = rn.stdout + rn.stderr
            ok = (rv.returncode != 0 and rn.returncode != 0 and
                  needle in vtext and needle in ntext)
            print("neg %-12s VM rc=%d NAT rc=%d diag=%s  %s" % (
                tag, rv.returncode, rn.returncode, needle,
                "OK" if ok else "FAIL"))
            if not ok:
                print("  VM :", vtext.strip()[:250])
                print("  NAT:", ntext.strip()[:250])
                fails.append("neg:" + tag)

        # ---------- CRC-негатив (A1) ----------
        good = os.path.join(REPO, "CtOs", "memmgr.ctos")
        body = bytearray(io.open(good, "rb").read())
        body[20 + len(body[20:]) // 2] ^= 0x5A
        bad = os.path.join(tmp, "corrupt.ctos")
        io.open(bad, "wb").write(body)
        rv = run_vm(bad, None, os.path.join(tmp, "corrupt.vm.trace"))
        rn = run_native(bad, None, os.path.join(tmp, "corrupt.nat.events"))
        ok = (rv.returncode != 0 and rn.returncode != 0 and
              "целостности" in (rv.stdout + rv.stderr) and
              "целостности" in (rn.stdout + rn.stderr))
        print("corrupt CRC: VM rc=%d NAT rc=%d %s" %
              (rv.returncode, rn.returncode, "OK" if ok else "FAIL"))
        if not ok:
            fails.append("corrupt CRC")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    if fails:
        print("NATIVE RT FAIL:", ", ".join(fails))
        return 1
    print("NATIVE RT OK A1/A2: ядро/NID/NID-негативы/полная самосборка "
          "совпадают с ctos_vm.py; T(S_T) байт-в-байт")
    return 0


if __name__ == "__main__":
    sys.exit(main())
