# -*- coding: utf-8 -*-
# Регресс вехи-14: union (tracked *.words ∪ NEW) — байт-в-байт tracked против
# HEAD, NEW — честные вердецы рабочим компилятором. regr13.py + пробы 'ow'
# (веха-14v2: аддитивный сайт 'ow' в stage1_compiler.kt — честный канал
# «значение слота → файл»: OP_OUTCELL_V(STREAM_EMIT_CELL, W_Current) +
# OP_SYSCALL(FILE_PUT)). Протокол вехи-9: HEAD и рабочий в своих temp-копиях.
# Layout стадии-1: hdr(20)+эмиссия+вердец(1)+отчёт(24), вердец на len-25.
import io, os, shutil, struct, subprocess, sys

REPO = r'H:\Project\MiniOS_CtOS'
WORK = os.path.join(REPO, 'Compiler', 'stage1_compiler.ctos')
VM   = os.path.join(REPO, 'CtOs-Emu', 'ctos_vm.py')
TMP  = os.path.join(r'G:\Windows\RJ\AppData\Local\Temp\opencode', 'regr13')
os.makedirs(TMP, exist_ok=True)

# 1) HEAD-компилятор -> temp-копия
head = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:Compiler/stage1_compiler.ctos'],
                      capture_output=True)
assert head.returncode == 0, head.stderr
head_path = os.path.join(TMP, 'compiler_head.ctos')
with io.open(head_path, 'wb') as f:
    f.write(head.stdout)
work_path = os.path.join(TMP, 'compiler_work.ctos')
shutil.copyfile(WORK, work_path)

SKIP = {
    'Python_compiler/neg_big.words',
    'Python_compiler/neg_big2.words',
}
# neg_big / neg_big2 — честная эволюция границы (вехи-9/12/13):
# 16→64→128→256; старые грани теперь честно ВЛЕЗАЮТ (вердец 0x07@N → 0xFF).

NEW = {
    'Python_compiler/pos_cp1.words':   0xFF,
    'Python_compiler/pos_cp2.words':   0xFF,
    'Python_compiler/neg_cp1.words':   0xFE,
    'Python_compiler/pos_scan3.words': 0xFF,
    'Python_compiler/pos_scan4.words': 0xFF,
    'Python_compiler/pos_scan5.words': 0xFF,
    'Python_compiler/pos_scan6.words': 0xFF,
    'Python_compiler/pos_scan7.words': 0xFF,
    'Python_compiler/neg_scan7.words': 0xFF,
    'Python_compiler/pos_wc14.words':  0xFF,
    # веха-14v2: 'ow' — 0xFF успех / 0xFE + 0x0C при открытом nb
    'Python_compiler/pos_ow1.words':   0xFF,
    'Python_compiler/pos_ow2.words':   0xFF,
    'Python_compiler/neg_ow1.words':   0xFE,
    'Python_compiler/pos_wc14v2.words': 0xFF,
}

fails = []
tracked = subprocess.run(['git', '-C', REPO, 'ls-files', '*.words'],
                         capture_output=True, text=True).stdout.split()
checked_new = 0
for rel in sorted(set(tracked) | set(NEW)):
    if rel in SKIP:
        print('%-42s SKIP (граница 0x40 -> 0x80, эволюция вехи-12г)' % rel)
        continue
    src = os.path.join(REPO, rel)
    if rel in NEW:
        r = subprocess.run([sys.executable, VM, work_path, '--source', src, '--quiet'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            fails.append('%s: VM rc=%d (%s)' % (rel, r.returncode, r.stdout[-200:]))
            continue
        art = io.open(work_path + '.out', 'rb').read()
        v = art[len(art) - 25]
        if v == NEW[rel]:
            checked_new = checked_new + 1
            print('%-42s NEW ok: len=%d, вердец 0x%02X' % (rel, len(art), v))
        else:
            fails.append('%s: вердец 0x%02X, ожидался 0x%02X' % (rel, v, NEW[rel]))
        os.remove(work_path + '.out')
        continue
    arts = {}
    for tag, binp in (('head', head_path), ('work', work_path)):
        r = subprocess.run([sys.executable, VM, binp, '--source', src, '--quiet'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            fails.append('%s %s: VM rc=%d %s' % (rel, tag, r.returncode, r.stdout[-200:]))
            continue
        out = binp + '.out'
        arts[tag] = io.open(out, 'rb').read()
    if ('head' in arts and 'work' in arts) and arts['head'] == arts['work']:
        print('%-42s IDENTICAL (%d B)' % (rel, len(arts['head'])))
    else:
        fails.append('%s DIFF (len head=%d work=%d)' % (
            rel, len(arts.get('head', b'')), len(arts.get('work', b''))))

# холодный ход (нет --source)
cold = {}
for tag, binp in (('head', head_path), ('work', work_path)):
    subprocess.run([sys.executable, VM, binp, '--quiet'], capture_output=True)
    cold[tag] = io.open(binp + '.out', 'rb').read()
print('cold: %s' % ('IDENTICAL' if cold['head'] == cold['work'] else 'DIFF'))
if cold['head'] != cold['work']:
    fails.append('cold DIFF')

print('')
if fails:
    print('FAILURES:')
    for f_ in fails:
        print(' ', f_)
    sys.exit(1)
if checked_new != len(NEW):
    print('HONEST CHECK FAIL: NEW проверено %d из %d (молчаливый пропуск?)'
          % (checked_new, len(NEW)))
    sys.exit(1)
print('REGRESS OK (tracked IDENTICAL + %d NEW-verdict + cold)' % checked_new)
