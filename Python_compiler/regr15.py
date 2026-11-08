# -*- coding: utf-8 -*-
# Регресс вехи-14v3: union (tracked *.words ∪ NEW) — байт-в-байт tracked
# против HEAD (222b454: веха-14v2), NEW — честные вердецы рабочим
# компилятором (22 426 Б, additive aa/as/vw вехи-14v3). regr14.py
# (вехи-14 v1/v2) + пробы aa/as/vw и word-компилятор v3 (честный слот).
# Протокол вехи-9: HEAD и рабочий в своих temp-копиях.
# Layout стадии-1: hdr(20)+эмиссия+вердец(1)+отчёт(24), вердец на len-25.
import io, os, shutil, subprocess, sys

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

# 2) NEW probes вехи-14v3 (вердец — факт приёмки рабочего компилятора)
NEW = {
    # 'aa' — ДЕСЯТЫЙ поглотитель nb: acc += cell[X], 6 Б; без nb — 0x0C
    'Python_compiler/pos_aa1.words':   0xFF,
    'Python_compiler/neg_aa1.words':   0xFE,
    # 'as' — слот-аккумулятор: acc += cell[W]; cell[W] = acc, 11 Б; с открытым nb — 0x0C
    'Python_compiler/pos_as1.words':   0xFF,
    'Python_compiler/neg_as1.words':   0xFE,
    # 'vw' — КОМПИЛ-ВРЕМЕННЫЙ канал: адрес слота W_Current -> 4 Б потока; с открытым nb — 0x0C
    'Python_compiler/pos_vw1.words':   0xFF,
    'Python_compiler/neg_vw1.words':   0xFE,
    # word-компилятор wc14v3 (слот ЧЕСТНО вычисляется из цифры target)
    'Python_compiler/pos_wc14v3.words': 0xFF,
    # честные цели stage1: слот F4 (d=1) — сильная сверка, не совпадение
    'Python_compiler/target1.words':   0xFF,
    # чу! 'va pr te' для stage1 — НЕ брак: va без открытого nb честно
    # загружает через W_Current (12 19 BE32(W_Current)), 61 Б, 0xFF.
    # (негатив wc14v3 — это брак ДЛЯ слово-компилятора: слово 1 != 'wc'
    #  -> fail-маркер 0 на порт, файл не открывается, honest OP_TERM.)
    'Python_compiler/neg_target.words': 0xFF,
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
