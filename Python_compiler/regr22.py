# -*- coding: utf-8 -*-
# Регресс вехи-21а спринт 2 (regr22): base regr21 (HEAD-e416897-W-21).
# Словарная полка: словарь разбит на честные Тома (решение пользователя).
#   Том v7  = 'pr'-ветка (веха-19, tracked, пробы вехи-18/19 честны).
#   Том v8as = 'as'-ветка (спринт 2): wc14v8as_build.py -> pos_wc14v8as.words,
#   499 токенов <= 510; CHECK v7-структура с конст-нетом 'as' (29537 = 0x7361,
#   2-char LE как 'pr' 29296 = 0x7270); EMIT_AS = честный шаблон 57 Б:
#   U16 4629 (=0x1215 '12 15') + слот BE32(F3+d) (канал nb(SRC_WORD2) va;
#   wc 0 as; wc 0 ow) + U8 85 (=0x55) + повтор 'ow' + _TAIL (U16 1535 = 0x05FF).
#   БЕЗ правок stage1 (22 861 Б, md5 abd93961 = слот №3 вехи-21а).
# Приёмка честная (probe23/27): 10 as-целей 'wc d as te' d=0..9
#   том байт-в-байт == эталонам stage1 (md5 306363fc .. 461ee233, Token 4);
#   негативы pr/zz/обрыв хвоста - честное молчание.
# Факт канал 'em'/'wo': ЦИФРЫ nb-train пишут ДЕСЯТИЧНОЕ значение байта
#   (1215 -> 0x04BF; hex 0x1215 = 4629). Ловушка снята честно.
# Факт пробы: явная '.' в source ДВОИТ терминатор (VM добразывает свою),
#   только у честных target-файлов БЕЗ явной '.' Token = 4.
import io, os, hashlib, shutil, subprocess, sys, struct

REPO = r'H:\Project\MiniOS_CtOS'
WORK = os.path.join(REPO, 'Compiler', 'stage1_compiler.ctos')
VM   = os.path.join(REPO, 'CtOs-Emu', 'ctos_vm.py')
TMP  = os.path.join(r'G:\Windows\RJ\AppData\Local\Temp\opencode', 'regr13')
os.makedirs(TMP, exist_ok=True)

head = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:Compiler/stage1_compiler.ctos'],
                      capture_output=True)
assert head.returncode == 0, head.stderr
head_path = os.path.join(TMP, 'compiler_head.ctos')
with io.open(head_path, 'wb') as f:
    f.write(head.stdout)
work_path = os.path.join(TMP, 'compiler_work.ctos')
shutil.copyfile(WORK, work_path)

def jc(binp, src):
    outp = binp + '.out'
    if os.path.exists(outp):
        os.remove(outp)
    r = subprocess.run([sys.executable, VM, binp, '--source', src, '--quiet'],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(outp):
        return None
    return io.open(outp, 'rb').read()

# Честная приёмка as-целей: md5 эталонов stage1 (probe27, источники без '.')
AS_MD5 = ['306363fc', 'd6b7a312', '7c3d64fe', '66b771e8', '868fbc7e',
          '5eac3141', '7eaa340c', '0d7d6e40', '7b2ef9a2', '461ee233']

NEW = {
    'Python_compiler/pos_wc14v8as.words': (0xFF, '8b504543'),
    'Python_compiler/target_as0.words': (0xFF, AS_MD5[0]),
    'Python_compiler/target_as1.words': (0xFF, AS_MD5[1]),
    'Python_compiler/target_as2.words': (0xFF, AS_MD5[2]),
    'Python_compiler/target_as3.words': (0xFF, AS_MD5[3]),
    'Python_compiler/target_as4.words': (0xFF, AS_MD5[4]),
    'Python_compiler/target_as5.words': (0xFF, AS_MD5[5]),
    'Python_compiler/target_as6.words': (0xFF, AS_MD5[6]),
    'Python_compiler/target_as7.words': (0xFF, AS_MD5[7]),
    'Python_compiler/target_as8.words': (0xFF, AS_MD5[8]),
    'Python_compiler/target_as9.words': (0xFF, AS_MD5[9]),
    'Python_compiler/neg_as2.words':    (0xFE, '5eae9fa0'),  # 'wc 0 as zz' FC=1@3
}

fails = []
tracked = subprocess.run(['git', '-C', REPO, 'ls-files', '*.words'],
                         capture_output=True, text=True).stdout.split()
tracked = [t for t in tracked if t not in NEW]
for rel in sorted(set(tracked) | set(NEW)):
    if os.path.exists(work_path + '.out'):
        os.remove(work_path + '.out')
    if os.path.exists(head_path + '.out'):
        os.remove(head_path + '.out')
    src = os.path.join(REPO, rel)
    if rel in NEW:
        exp = NEW[rel]
        exp_v, exp_md5 = (exp if isinstance(exp, tuple) else (exp, None))
        art = jc(work_path, src)
        if art is None:
            fails.append('%s: VM молчание (ожидался вердец 0x%02X)' % (rel, exp_v))
            continue
        v = art[len(art) - 25]
        md5 = hashlib.md5(art).hexdigest()
        if v != exp_v:
            fails.append('%s: вердец 0x%02X, ожидался 0x%02X' % (rel, v, exp_v))
            continue
        if exp_md5 and not md5.startswith(exp_md5):
            fails.append('%s: md5 %s, ожидался %s...' % (rel, md5, exp_md5))
            continue
        print('%-42s NEW ok: len=%d, вердец 0x%02X%s'
              % (rel, len(art), v, ', md5 ок' if exp_md5 else ''))
        continue
    arts = {}
    for tag, binp in (('head', head_path), ('work', work_path)):
        a = jc(binp, src)
        if a is not None:
            arts[tag] = a
    if ('head' in arts and 'work' in arts) and arts['head'] == arts['work']:
        print('%-42s IDENTICAL (%d B)' % (rel, len(arts['head'])))
    else:
        fails.append('%s DIFF (len head=%d work=%d)' % (
            rel, len(arts.get('head', b'')), len(arts.get('work', b''))))

# ---- честная ПОЛКА: том-двоички ----
# том v8as RUNTIME vs эталон stage1: recompile pos_wc14v8as -> vol bin -> targets
shelf_ok = True
art = jc(work_path, os.path.join(REPO, 'Python_compiler', 'pos_wc14v8as.words'))
if art is None:
    print('shelf: том компиляции не собрала бинарник'); shelf_ok = False
else:
    volp = os.path.join(TMP, 'regr22_vol_v8as.ctos')
    io.open(volp, 'wb').write(art)
    for d in range(10):
        src = os.path.join(REPO, 'Python_compiler', 'target_as%d.words' % d)
        ref = jc(work_path, src)          # честный свежий эталон
        got = jc(volp, src)               # том на цели
        if ref is None or got is None:
            print('shelf as%d: %s' % (d, 'молчание тома/эталона')); shelf_ok = False
            continue
        if ref == got:
            print('shelf as%d: IDENTICAL (%d B, md5 %s)'
                  % (d, len(got), hashlib.md5(got).hexdigest()[:8]))
        else:
            print('shelf as%d: MISMATCH' % d); shelf_ok = False
    # негатив: 'wc 0 pr te' через as-том - честное молчание
    neg = os.path.join(REPO, 'Python_compiler', 'target0.words')
    negg = jc(volp, neg)
    if negg is None:
        print('shelf as-vol on pr-цель: молчание (честный отказ)')
    else:
        print('shelf as-vol on pr-цель: НЕ молчание (%d B)!!' % len(negg))
        shelf_ok = False
if not shelf_ok:
    fails.append('shelf FAIL')

# холодный ход (нет --source)
cold = {}
for tag, binp in (('head', head_path), ('work', work_path)):
    outp = binp + '.out'
    if os.path.exists(outp):
        os.remove(outp)
    subprocess.run([sys.executable, VM, binp, '--quiet'], capture_output=True)
    cold[tag] = io.open(outp, 'rb').read()
print('cold: %s' % ('IDENTICAL' if cold['head'] == cold['work'] else 'DIFF'))
if cold['head'] != cold['work']:
    fails.append('cold DIFF')

print('')
if fails:
    print('FAILURES:')
    for f_ in fails:
        print(' ', f_)
    sys.exit(1)
print('REGRESS OK (tracked IDENTICAL + as-shelf byte-ok + cold)')
