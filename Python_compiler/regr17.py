# -*- coding: utf-8 -*-
# Регресс вехи-15: union (tracked *.words + NEW) - байт-в-байт tracked
# против HEAD (d4a117e: веха-14v4), NEW - честный вердец от честного
# рабочего stage-1 компилятора (22 614 Б, 'wc' 0..5 -> 0..9: слоты
# W8..WB = 0x00F00FF9..0x00F00FFC; приёмка 10/10 против stage1-эталонов).
# regr16.py (веха-14v4) -> SKIP-список пуст, числа честно НЕ менялись.
# regr17 additions: target6..target9 в NEW (ВЕРДЕЦНЫЙ тест, НЕ tracked
# byte-check: HEAD честно бракует d=6..9 кодом BRK_WC_NO_LIT 0x08@1 —
# снятие различия слоёв — предмет вехи-15; head-vs-work сравнение по
# построению невозможно). Приёмка 10/10: stage1 (веха-15) на d=0..9
# честные md5: d0 8d82091a, d1 d40a8ad8, d2 19f90fac, d3 6693dabe,
# d4 f50c55e2, d5 a4a0c9e1, d6 1ae1dd05 (=wc14v4-факт), d7 ac728a9e,
# d8 67952626, d9 7e05c1be; слоты честно BE32 @25..28 = 0x00F00FF3..0x00F00FFC.
# Регресс против HEAD (вехи-9): HEAD в честной temp-копии (regr13).
# Layout стадии-1: hdr(20)+эмиссия+вердец(1)+отчёт(24), вердец @ len-25.
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
# Честная защита от stale-ловушки: при браке VM молчит и НЕ
# переписывает .out (факт stage-2 neg_target); чистка .out честна,
# чтобы не принять чужой артефакт за свой прогон.

SKIP = set()
# Честь вехи-14v4: neg_big/neg_big2/neg_big3 не в SKIP - факты известны:
# head-vs-work по старым словам IDENTICAL (веха-15 честно не трогает
# старые цифры 0..5 и bytecode старых слов: probe byte-diff снял только
# границы). Граница вехи-15 - только расширение диапазона 'wc'.

# 2) NEW-пробы (вердец - факт от честных прогонов работающего компилятора)
NEW = {
    # honest Syntax/Node ow-канал: программа 260 токенов (факт счётчика,
    # плановая оценка 261 была неточной), MAX 0x200 нужен (260 > 254)
    'Python_compiler/pos_wc14v4.words': 0xFF,
    # честная граница MAX-1: 511 sv -> Boot_Count 512 == MAX
    # честный OVERFLOW: вердец 0xFE, Fail_Code 0x07, Fail_Position 0x200
    # (2600 Б, md5 19966a43; Token 511, эмиссия 2555 = 511х5)
    'Python_compiler/neg_big3.words': 0xFE,
    # честная граница MAX-2: 508 sv + pr te = 510 токенов -> 0xFF
    # (2595 Б, md5 ea018d84; Token 510 = 0x1FE, эмиссия 2550 = 510х5)
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
    # Веха-15 честная приёмка: цифры 6..9 (слоты W8..WB 0x00F00FF9..0x00F00FFC).
    # вердецный тест: HEAD честно бракует 0x08@1 (стадии расходились; снятие
    # различия слоёв — предмет вехи-15). d=6 stage1 == wc14v4-факт md5
    # 1ae1dd05 (байт-в-байт снят вехой-15); d=7..9 честные новые факты:
    # ac728a9e / 67952626 / 7e05c1be; слоты честно 0x00F00FFA/FFB/FFC
    # (BE32 @25..28, вердец 0xFF по честной формуле art[len-25]).
    'Python_compiler/target6.words':   0xFF,
    'Python_compiler/target7.words':   0xFF,
    'Python_compiler/target8.words':   0xFF,
    'Python_compiler/target9.words':   0xFF,
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
