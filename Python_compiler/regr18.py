# -*- coding: utf-8 -*-
# Регресс вехи-16: union (tracked *.words + NEW) - байт-в-байт tracked
# против HEAD (3be2b33: веха-15), NEW - честный вердец (и, где задан,
# честный md5) от честного рабочего stage-1 компилятора (22 614 Б).
# regr17.py (веха-15) - база; многослотовая честная приёмка stage1
# веха-16: значения в слоты кладутся 'nb X ne sv' (ne закрывает число,
# sv пишет acc в W_Current), W_Current честно ведётся между 'wc d'.
# Честные runtime-факты stage1-артефактов (VM): m4 SUCCESS, порт <- 5
# (cell[F5]=5, cell[F8]=7), многолотовая семантика честна.
# Честная граница v4 (word-компилятор wc14v4, 474 Б): хвост целевой
# конструкции честно НЕ сверяется - при word0='wc' и цифре в word1
# любая цель честно сворачивается в template 'wc d pr te' (55 Б) с
# честным Token-счётом реального числа слов (факт: t_bad2 == эталон
# target0 8d82091a, Token 4 = 4 слова + '.'; t_dupe md5 другой =
# Token 5; t_3w Token 3; t_2w Token 2; m4 Token 13). Граница честно
# задокументирована вехой-14v1 ('проверка pr/te - v2') и честно не
# закрыта в v2..v4 (в v2 место проверки занял счётчик токенов).
# Layout стадии-1: hdr(20)+эмиссия+вердец(1)+отчёт(24), вердец @ len-25.
import io, os, hashlib, shutil, subprocess, sys

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

# 2) NEW-пробы (вердец (+ md5, где задан) - факт от честных прогонов
#    работающего компилятора). Формат значения: 0xFF (только вердец)
#    или (вердец, 'md5-префикс') - честный байт-контроль.
NEW = {
    # honest Syntax/Node ow-канал: программа 260 токенов, MAX 0x200
    'Python_compiler/pos_wc14v4.words': 0xFF,
    # честная граница MAX-1: 511 sv -> честный OVERFLOW 0x07@0x200
    'Python_compiler/neg_big3.words': 0xFE,
    # честная граница MAX-2: 510 токенов -> 0xFF
    'Python_compiler/pos_edge3.words': 0xFF,
    # 'aa' — ДЕСЯТЫЙ поглотитель nb: acc += cell[X], 6 Б; без nb — 0x0C
    'Python_compiler/pos_aa1.words':   0xFF,
    'Python_compiler/neg_aa1.words':   0xFE,
    # 'as' — слот-аккумулятор: 11 Б; с открытым nb — 0x0C
    'Python_compiler/pos_as1.words':   0xFF,
    'Python_compiler/neg_as1.words':   0xFE,
    # 'vw' — КОМПИЛ-ВРЕМЕННЫЙ канал: 4 Б потока; с открытым nb — 0x0C
    'Python_compiler/pos_vw1.words':   0xFF,
    'Python_compiler/neg_vw1.words':   0xFE,
    # word-компилятор wc14v3 (слот ЧЕСТНО вычисляется из цифры target)
    'Python_compiler/pos_wc14v3.words': 0xFF,
    # честные цели stage1: слот F4 (d=1) - сильная сверка
    'Python_compiler/target1.words':   0xFF,
    # 'va pr te' для stage1 — НЕ брак: va грузит через W_Current
    'Python_compiler/neg_target.words': 0xFF,
    # Веха-15: цифры 6..9 (слоты W8..WB); md5-факты честны
    'Python_compiler/target6.words':   (0xFF, '1ae1dd05'),
    'Python_compiler/target7.words':   (0xFF, 'ac728a9e'),
    'Python_compiler/target8.words':   (0xFF, '67952626'),
    'Python_compiler/target9.words':   (0xFF, '7e05c1be'),
    # ---- Веха-16: многослотовая честная приёмка stage1 ----
    # m1..m3: 'nb X sv' = честное ПОГЛОЩЕНИЕ как АДРЕС (веха-8):
    # cell[X] = acc; W_Current честно ведётся между 'wc d'
    # (probe_multi: 71 Б каждый, вердец 0xFF)
    'Python_compiler/target_m1.words': (0xFF, '2e554db2'),
    'Python_compiler/target_m2.words': (0xFF, '35069f16'),
    'Python_compiler/target_m3.words': (0xFF, '3949f9f2'),
    # m4: честный синтаксис значения 'nb X ne sv' -> cell[W_Current] = X;
    # runtime VM: OP_CONST 5; STORE_AT F5; CONST 7; STORE_AT F8;
    # LOAD[0x19] F5; OUTCELL_V порт <- 5; TERM; SUCCESS. 81 Б.
    'Python_compiler/target_m4.words': (0xFF, '17705440'),
    # Честная граница хвоста stage1-семантики (доки вехи-16):
    'Python_compiler/target_t2w.words': (0xFF, 'a154e85f'),  # 45 Б, эмиссия пуста ('wc d' без байтов)
    'Python_compiler/target_t3w.words': (0xFF, '4c30de2d'),  # 54 Б: pr без te в эмиссии
    'Python_compiler/target_td.words':  (0xFF, '1ceeb644'),  # 64 Б: двойной pr честен
    'Python_compiler/target_tb.words':  (0xFE, 'ad2ffb25'),  # честный брак: 'ne' без открытого nb
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
        exp = NEW[rel]
        exp_v, exp_md5 = (exp if isinstance(exp, tuple) else (exp, None))
        r = subprocess.run([sys.executable, VM, work_path, '--source', src, '--quiet'],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(work_path + '.out'):
            fails.append('%s: VM rc=%d (%s)' % (rel, r.returncode, r.stdout[-200:]))
            continue
        art = io.open(work_path + '.out', 'rb').read()
        v = art[len(art) - 25]
        md5 = hashlib.md5(art).hexdigest()
        if v != exp_v:
            fails.append('%s: вердец 0x%02X, ожидался 0x%02X' % (rel, v, exp_v))
            continue
        if exp_md5 and not md5.startswith(exp_md5):
            fails.append('%s: md5 %s, ожидался %s...' % (rel, md5, exp_md5))
            continue
        checked_new = checked_new + 1
        print('%-42s NEW ok: len=%d, вердец 0x%02X%s'
              % (rel, len(art), v, ', md5 ок' if exp_md5 else ''))
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
print('REGRESS OK (tracked IDENTICAL + %d NEW-verdict(+md5) + cold)' % checked_new)
