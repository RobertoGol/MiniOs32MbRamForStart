# -*- coding: utf-8 -*-
"""Проверка фиксепоинта самосборки T(S_T) == T (веха-24д).

T     = кольцевой word-компилятор ( Compiler/stage1_compiler.ctos.out,
        собранный из S_T свежим stage1 ).
S_T   = Python_compiler/pos_wc14v3ring.words — исходник кольца на words.

Проверка честная: гоняем T на S_T и сравниваем байты с T. Если T молчит,
бисектом находим первый токен, на котором кольцо перестаёт печатать (это
указание на неподдерживаемое исходное слово, а не на панику).
"""
import hashlib
import io
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VM = os.path.join(REPO, 'CtOs-Emu', 'ctos_vm.py')
STAGE1 = os.path.join(REPO, 'Compiler', 'stage1_compiler.ctos')
T = os.path.join(REPO, 'Compiler', 'stage1_compiler.ctos.out')
S_T = os.path.join(REPO, 'Python_compiler', 'pos_wc14v3ring.words')
TMP = os.environ.get('TEMP') or os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(TMP):
    TMP = os.path.dirname(os.path.abspath(__file__))


def run(binp, src):
    outp = binp + '.out'
    if os.path.exists(outp):
        os.remove(outp)
    r = subprocess.run([sys.executable, VM, binp, '--source', src, '--quiet'],
                       capture_output=True, encoding='cp1251')
    art = io.open(outp, 'rb').read() if os.path.exists(outp) else None
    return art, r.returncode, r.stdout.strip()[:120]


def main():
    # 1) T := S(S_T) свежим stage1
    art, rc, msg = run(STAGE1, S_T)
    if art is None:
        print('SELFHOST FAIL: stage1 не собрал S_T (rc=%d %s)' % (rc, msg))
        return 1
    io.open(T, 'wb').write(art)
    print('T   = %d Б md5 %s' % (len(art), hashlib.md5(art).hexdigest()))

    # 2) T(S_T)
    got, grc, gmsg = run(T, S_T)
    if got is None:
        print('T(S_T): кольцо молчит (rc=%d %s) — фиксепоинт НЕ достигнут' %
              (grc, gmsg))
        words = io.open(S_T, encoding='ascii').read().split()
        probe = os.path.join(TMP, '_selfhost_prefix.words')
        def works(n):
            with io.open(probe, 'w', encoding='ascii', newline='') as f:
                f.write(' '.join(words[:n]) + '\n')
            o, _, _ = run(T, probe)
            return o is not None
        lo, hi = 1, len(words)
        if works(hi):
            hi = len(words)  # should not happen
        while lo < hi:
            mid = (lo + hi) // 2
            if works(mid):
                lo = mid + 1
            else:
                hi = mid
        print('первый неподдерживаемый префикс: %d токенов' % lo)
        print('контекст: ... %s ...' % ' '.join(words[max(0, lo - 8):lo + 4]))
        return 1
    print('T(S_T) = %d Б md5 %s' % (len(got), hashlib.md5(got).hexdigest()))
    if got == art:
        print('SELFHOST IDENTICAL: T(S_T) == T')
        return 0
    print('SELFHOST DIFF: T(S_T) != T')
    return 1


if __name__ == '__main__':
    sys.exit(main())
