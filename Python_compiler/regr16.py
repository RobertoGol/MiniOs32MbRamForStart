# -*- coding: utf-8 -*-
# Регресс вехи-14v4: union (tracked *.words ∪ NEW) — байт-в-байт tracked
# против HEAD (7a4c419: веха-14v3), NEW — честные вердецы рабочим
# компилятором (22 426 Б, MAX 0x200 + honest Syntax/Node ow-канал).
# regr15.py (вехи-14v3) − SKIP + три NEW-пробы v4. Протокол вехи-9:
# HEAD и рабочий в своих temp-копиях.
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
# честная защита от ловушки stale-выхода: при браке VM молчит и НЕ
# переписывает .out (факт stage-2 neg_target); старый .out чистим,
# чтобы не прочитать чужой артефакт чужого пути.

SKIP = set()
# Честный ре-SKIP: neg_big / neg_big2 больше НЕ SKIP — факт теста:
# head-vs-work IDENTICAL (360 Б / 680 Б), и тот же результат после
# подъёма MAX 0x200 (diff 76 Б = 4 метаданных образа + 72 inline-
# константы 0x01->0x02). Границы 511/510 теперь проверяют честные
# NEW-пробы neg_big3 / pos_edge3; старые пробы честно влезают в 0x200.

# 2) NEW probes вехи-14v4 (вердец — факт приёмки рабочего компилятора)
NEW = {
    # honest Syntax/Node ow-канал: программа 260 токенов (факт счётчика,
    # плановая оценка 261 была неточной), MAX 0x200 нужен (260 > 254)
    'Python_compiler/pos_wc14v4.words': 0xFF,
    # граница MAX-1: 511 sv -> Boot_Count 512 == MAX
    # честный OVERFLOW: вердец 0xFE, Fail_Code 0x07, Fail_Position 0x200
    # (2600 Б, md5 19966a43; Token 511, эмиссия 2555 = 511×5)
    'Python_compiler/neg_big3.words': 0xFE,
    # честная граница MAX-2: 508 sv + pr te = 510 токенов -> 0xFF
    # (2595 Б, md5 ea018d84; Token 510 = 0x1FE, эмиссия 2550 = 510×5)
    'Python_compiler/pos_edge3.words': 0xFF,
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
    'Python_compiler/neg_target.words': 0xFF,
}

fails = []
tracked = subprocess.run(['git', '-C', REPO, 'ls-files', '*.words'],
                         capture_output=True, text=True).stdout.split()
checked_new = 0
for rel in sorted(set(tracked) | set(NEW)):
    if rel in SKIP:
        print('%-42s SKIP' % rel)
        continue
    # честная защита от stale-.out (VM молчит при браке и не переписывает)
    if os.path.exists(work_path + '.out'):
        os.remove(work_path + '.out')
    if os.path.exists(head_path + '.out'):
        os.remove(head_path + '.out')
    src = os.path.join(REPO, rel)
    if rel in NEW:
        r = subprocess.run([sys.executable, VM, work_path, '--source', src, '--quiet'],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(work_path + '.out'):
            fails.append('%s: VM rc=%d (%s)' % (rel, r.returncode, r.stdout[-200:]))
            continue
        art = io.open(work_path + '.out', 'rb').read()
        v = art[len(art) - 25]
        if v == NEW[rel]:
            checked_new = checked_new + 1
            print('%-42s NEW ok: len=%d, вердец 0x%02X' % (rel, len(art), v))
        else:
            fails.append('%s: вердец 0x%02X, ожидался 0x%02X' % (rel, v, NEW[rel]))
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
