# -*- coding: utf-8 -*-
"""A1 (bring-up Ф2): честная сверка нативного интерпретатора с ctos_vm.py.

Сравниваются:
  1) последовательность портовых выводов (OP_OUTCELL / OP_OUTCELL_V);
  2) счётчик исполненных опкодов;
  3) число живых ячеек;
  4) честный отказ обоих исполнителей на испорченном CRC-32 тела.

Запуск:
    python -X utf8 Python_compiler/verify_native_rt.py
"""
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
CASES = [
    os.path.join(REPO, "CtOs", "memmgr.ctos"),
    os.path.join(REPO, "CtOs", "kernel_sched.ctos"),
]

PORT_RE = re.compile(
    r"OP_OUTCELL(?:_V)?: порт 0x([0-9A-Fa-f]+) <- "
    r"(?:cell\[0x[0-9A-Fa-f]+\] = )?0x([0-9A-Fa-f]+)")
OPS_RE = re.compile(r"(\d+) опкод")
CELLS_RE = re.compile(r"ячеек: (\d+)")


def run_vm(binary, trace):
    outp = binary + ".out"
    if os.path.exists(outp):
        os.remove(outp)
    r = subprocess.run([sys.executable, "-X", "utf8", VM, binary,
                        "--trace", trace],
                       capture_output=True, encoding="utf-8")
    return r


def vm_expect(binary, trace):
    r = run_vm(binary, trace)
    if r.returncode != 0:
        raise RuntimeError("VM rc=%d: %s" % (r.returncode, r.stderr.strip()))
    ports = []
    with open(trace, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = PORT_RE.search(line)
            if m:
                ports.append("PORT %s %s" % (m.group(1).upper(), m.group(2).upper()))
    mo, mc = OPS_RE.search(r.stdout), CELLS_RE.search(r.stdout)
    if not mo or not mc:
        raise RuntimeError("не найден итог VM в stdout: %r" % r.stdout[-200:])
    counts = "OPS %s CELLS %s" % (mo.group(1), mc.group(1))
    return ports, counts


def run_native(binary, events):
    if os.path.exists(events):
        os.remove(events)
    r = subprocess.run([EXE, binary, events], capture_output=True,
                       encoding="utf-8")
    lines = []
    if os.path.exists(events):
        with open(events, encoding="ascii") as f:
            lines = [s.rstrip("\r\n") for s in f if s.strip()]
    return r, lines


def ensure_exe():
    os.makedirs(os.path.dirname(EXE), exist_ok=True)
    if (os.path.exists(EXE) and
            os.path.getmtime(EXE) >= os.path.getmtime(SRC)):
        return
    print("build: gcc -O2 -std=c11 ...")
    r = subprocess.run(["gcc", "-O2", "-std=c11", "-Wall", "-Wextra",
                        "-o", EXE, SRC], capture_output=True,
                       encoding="utf-8")
    if r.returncode:
        raise RuntimeError("gcc: %s %s" % (r.stdout, r.stderr))


def main():
    ensure_exe()
    tmp = tempfile.mkdtemp(prefix="native_verify_")
    fails = []
    try:
        for binary in CASES:
            name = os.path.basename(binary)
            trace = os.path.join(tmp, name + ".vm.trace")
            events = os.path.join(tmp, name + ".native.events")
            vp, vc = vm_expect(binary, trace)
            r, nl = run_native(binary, events)
            np = [s for s in nl if s.startswith("PORT ")]
            nc = [s for s in nl if s.startswith("OPS ")]

            ok_ports = (np == vp)
            ok_counts = (nc == [vc])
            print("%-20s ports %d/%d %s; counts %s %s (native rc=%d)" %
                  (name, len(np), len(vp), "OK" if ok_ports else "DIFF",
                   "OK" if ok_counts else "DIFF",
                   nc[0] if nc else "-", r.returncode))
            if not ok_ports:
                for i, (a, b) in enumerate(zip(vp, np)):
                    if a != b:
                        print("  first port diff @%d: vm=%s native=%s" % (i, a, b))
                        break
                print("  vm  =", vp[:4], "...", vp[-2:])
                print("  nat =", np[:4], "...", np[-2:])
            if not ok_counts:
                print("  vm counts=%s native counts=%s" % (vc, nc))
            if r.returncode or not ok_ports or not ok_counts:
                fails.append(name)

        # честный негатив: порча тела => оба исполнителя отказываются
        good = CASES[0]
        body = open(good, "rb").read()
        bad = bytearray(body)
        bad[20 + len(bad[20:]) // 2] ^= 0x5A
        badp = os.path.join(tmp, "corrupt.ctos")
        with open(badp, "wb") as f:
            f.write(bad)
        vr = run_vm(badp, os.path.join(tmp, "corrupt.vm.trace"))
        nr, _ = run_native(badp, os.path.join(tmp, "corrupt.native.events"))
        # VM пишет KERNEL PANIC в stdout, нативный рантайм — в stderr;
        # проверяем оба потока, не предполагая конкретный канал.
        neg_ok = (vr.returncode != 0 and nr.returncode != 0 and
                  "целостности" in (vr.stdout + vr.stderr) and
                  "целостности" in (nr.stdout + nr.stderr))
        print("corrupt CRC: VM rc=%d native rc=%d %s" %
              (vr.returncode, nr.returncode, "OK" if neg_ok else "FAIL"))
        if not neg_ok:
            fails.append("corrupt CRC")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    if fails:
        print("NATIVE RT FAIL:", ", ".join(fails))
        return 1
    print("NATIVE RT OK A1: порты/опкоды/ячейки совпадают с ctos_vm.py; "
          "CRC-негатив честный")
    return 0


if __name__ == "__main__":
    sys.exit(main())
