# -*- coding: utf-8 -*-
# Регресс вехи-21а спринт 5 (regr25): base regr24 (HEAD = W-24 1ae9c12).
# Полка: том 'sp' (спринт 5): wc14v8sp_build.py -> pos_wc14v8sp.words,
# 487 токенов <= 510 (INIT полный, elide PA/PD из спринта ow не нужен);
# PB-конст 'sp' (28787 = 0x7073, 2-char LE); EMIT_SP = U8 83 (0x53)
# + слот BE32(F3+d) + хвост U16 1535 (0x05FF). Окно 'sp' 6 Б (probe28).
# Приёмка честная (probe29 sp): 10 целей 'wc d sp te' d=0..9 том
# байт-в-байт == эталонам stage1 (md5 70b4c02e .. 39737fa9, 51 Б);
# негативы pr/zz/as через sp-том - молчание; stage1-эталон негатива
# 'wc 0 sp zz' = 0xFE, Token 3, FC=1@3, md5 edaa4227.
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

AS_MD5 = ['306363fc', 'd6b7a312', '7c3d64fe', '66b771e8', '868fbc7e',
          '5eac3141', '7eaa340c', '0d7d6e40', '7b2ef9a2', '461ee233']
VA_MD5 = ['ad410305', '5d8b9888', '66b81c43', '463e3c26', 'e74e7a82',
          'c7b41073', '1018ce96', 'c66dd38c', '3cf06b93', '0e4696a8']
OW_MD5 = ['13f56e28', '7386b7f9', 'ca657671', 'f685f7da', '17db7fa1',
          '05bec7c0', 'd73fc3ec', '0c34165d', '32d82848', '48d85e74']
SP_MD5 = ['70b4c02e', 'c6558697', '2ed5dc36', 'c2dd58cb', '848b1a59',
          'd7210696', '2156a3ab', 'f7acb414', '17e3dfce', '39737fa9']

NEW = {
    # ---- веха-21а спринт 2 (regr22, W-22) ----
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
    # ---- веха-21а спринт 3 (regr23, W-23) ----
    'Python_compiler/pos_wc14v8va.words': (0xFF, '8f4ceb36'),
    'Python_compiler/target_va0.words': (0xFF, VA_MD5[0]),
    'Python_compiler/target_va1.words': (0xFF, VA_MD5[1]),
    'Python_compiler/target_va2.words': (0xFF, VA_MD5[2]),
    'Python_compiler/target_va3.words': (0xFF, VA_MD5[3]),
    'Python_compiler/target_va4.words': (0xFF, VA_MD5[4]),
    'Python_compiler/target_va5.words': (0xFF, VA_MD5[5]),
    'Python_compiler/target_va6.words': (0xFF, VA_MD5[6]),
    'Python_compiler/target_va7.words': (0xFF, VA_MD5[7]),
    'Python_compiler/target_va8.words': (0xFF, VA_MD5[8]),
    'Python_compiler/target_va9.words': (0xFF, VA_MD5[9]),
    'Python_compiler/neg_va2.words':    (0xFE, '5ed0477b'),  # 'wc 0 va zz' FC=1@3
    # ---- веха-21а спринт 4 (regr24, W-24) ----
    'Python_compiler/pos_wc14v8ow.words': (0xFF, '9a1ac095'),
    'Python_compiler/target_ow0.words': (0xFF, OW_MD5[0]),
    'Python_compiler/target_ow1.words': (0xFF, OW_MD5[1]),
    'Python_compiler/target_ow2.words': (0xFF, OW_MD5[2]),
    'Python_compiler/target_ow3.words': (0xFF, OW_MD5[3]),
    'Python_compiler/target_ow4.words': (0xFF, OW_MD5[4]),
    'Python_compiler/target_ow5.words': (0xFF, OW_MD5[5]),
    'Python_compiler/target_ow6.words': (0xFF, OW_MD5[6]),
    'Python_compiler/target_ow7.words': (0xFF, OW_MD5[7]),
    'Python_compiler/target_ow8.words': (0xFF, OW_MD5[8]),
    'Python_compiler/target_ow9.words': (0xFF, OW_MD5[9]),
    'Python_compiler/neg_ow2.words':    (0xFE, '30f2b201'),  # 'wc 0 ow zz' FC=1@3
    # ---- веха-21а спринт 5 (regr25, W-25) ----
    'Python_compiler/pos_wc14v8sp.words': (0xFF, '641f7f2c'),
    'Python_compiler/target_sp0.words': (0xFF, SP_MD5[0]),
    'Python_compiler/target_sp1.words': (0xFF, SP_MD5[1]),
    'Python_compiler/target_sp2.words': (0xFF, SP_MD5[2]),
    'Python_compiler/target_sp3.words': (0xFF, SP_MD5[3]),
    'Python_compiler/target_sp4.words': (0xFF, SP_MD5[4]),
    'Python_compiler/target_sp5.words': (0xFF, SP_MD5[5]),
    'Python_compiler/target_sp6.words': (0xFF, SP_MD5[6]),
    'Python_compiler/target_sp7.words': (0xFF, SP_MD5[7]),
    'Python_compiler/target_sp8.words': (0xFF, SP_MD5[8]),
    'Python_compiler/target_sp9.words': (0xFF, SP_MD5[9]),
    'Python_compiler/neg_sp2.words':    (0xFE, 'edaa4227'),  # 'wc 0 sp zz' FC=1@3
}

fails = []
tracked = subprocess.run(['git', '-C', REPO, 'ls-files', '*.words'],
                         capture_output=True, text=True).stdout.split()
tracked = [t for t in tracked if t not in NEW]
for rel in sorted(set(tracked) | set(NEW)):
    src = os.path.join(REPO, rel)
    if rel in NEW:
        exp_v, exp_md5 = NEW[rel]
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

# ---- честная ПОЛКА: тома-двоички ----
SHELF = [
    ('as', 'pos_wc14v8as.words', 'target_as'),
    ('va', 'pos_wc14v8va.words', 'target_va'),
    ('ow', 'pos_wc14v8ow.words', 'target_ow'),
    ('sp', 'pos_wc14v8sp.words', 'target_sp'),
]
shelf_ok = True
vol_paths = {}
for lex, pos_rel, _tbase in SHELF:
    art = jc(work_path, os.path.join(REPO, 'Python_compiler', pos_rel))
    if art is None:
        print('shelf: том %s не собрал бинарник' % lex); shelf_ok = False
        continue
    volp = os.path.join(TMP, 'regr25_vol_%s.ctos' % lex)
    io.open(volp, 'wb').write(art)
    vol_paths[lex] = volp
    print('shelf vol-%s: %d B md5 %s' % (lex, len(art),
                                         hashlib.md5(art).hexdigest()[:8]))
for lex, _pos_rel, tbase in SHELF:
    volp = vol_paths.get(lex)
    if volp is None:
        continue
    ok10 = True
    for d in range(10):
        src = os.path.join(REPO, 'Python_compiler', '%s%d.words' % (tbase, d))
        ref = jc(work_path, src)          # честный свежий эталон
        got = jc(volp, src)               # том на цели
        if ref is None or got is None:
            print('shelf %s%d: молчание тома/эталона' % (lex, d))
            ok10 = False
            continue
        if ref != got:
            print('shelf %s%d: MISMATCH' % (lex, d))
            ok10 = False
    print('shelf %s: %s' % (lex, '10/10 targets byte-ok' if ok10
                            else 'has mismatches above'))
    shelf_ok = shelf_ok and ok10
    # кросс-отказы: pr-цель и первые цели ЧУЖИХ томов - честное молчание
    for cross in ('target0.words',) + tuple(
            '%s0.words' % tb for _l, _p, tb in SHELF if tb != tbase):
        cx = os.path.join(REPO, 'Python_compiler', cross)
        g2 = jc(volp, cx)
        if g2 is None:
            print('shelf %s-vol on %s: молчание (честный отказ)' % (lex, cross))
        else:
            print('shelf %s-vol on %s: НЕ молчание (%d B)!!'
                  % (lex, cross, len(g2)))
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
print('REGRESS OK (tracked IDENTICAL + as/va/ow/sp-shelf byte-ok + cold)')
