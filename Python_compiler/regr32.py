# -*- coding: utf-8 -*-
# Регресс вехи-21а хвост (regr32): base regr31 (HEAD = W-31 6d5aec9).
# Полка Token-3 пополнилась томом 'as' (спринт 3 хвоста):
# wc14v9as_build.py -> pos_wc14v9as.words, 443 токенов <= 510;
# PB-конст 'as' (29537 = 0x7361, 2-char LE); PC = 46 (конст word4 '.');
# EMIT_AS3 = U16 4629 (0x1215) + слот BE32(F3+d) (канал
# nb(SRC_WORD2) va; wc 0 as; wc 0 ow) + U8 85 (0x55)
# + повтор BE32(F3+d) + вердец U8 FF (каркас probe33).
# Окно 'as' Token-3 11 Б = окно 4-словного as БЕЗ страддл-хвоста
# (честный факт probe30).
# Приёмка честная (probe31 as): 10 целей 'wc d as' d=0..9 том
# байт-в-байт == эталонам stage1 (md5 23942602..aeea23e3, 56 Б):
# негативы 'wc 0 as as' (4-словный), 'wc 0 pr te', 'wc 0 as zz'
# через as-том - МОЛЧАНИЕ; stage1-эталон негатива 'wc 0 as zz'
# = 0xFE, Token 3, FC=1@3, md5 5eae9fa0 = tracked neg_as2.words
# (тот же литерал - отдельный neg-файл НЕ дублируем, честно).
# Как и W-30: stage1 НЕ правился (22 861 Б md5 abd93961).
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
IF_MD5 = ['bb0a0c7d'] * 10   # d-независим
TE_MD5 = ['6b6227af'] * 10   # d-независим
SV_MD5 = ['e719b5ad', 'a49a7f62', 'f0c3d6b6', '5779e4d3', 'a76a0988',
          '9c9276e8', '19351977', 'fb9b8d2c', '4dbad71e', '1854ca43']
VW_MD5 = ['c7168aac', 'a58fa363', '1f34ddd9', 'd0900bbe', 'fc441b60',
          'c83d7381', '8f933e8a', 'ffdf2b20', '8691d719', '3ea4addb']
T3TE_MD5 = ['bac85372'] * 10   # Token-3 'te': d-независим (probe30/31)
T3PR_MD5 = ['4c30de2d', 'bda003b8', 'e4aa85e9', 'a2f1ace4', '9f202fec',
            '61957c4c', 'b7787771', '3ee88a48', '588cba79', '1be8f7ac']
T3AS_MD5 = ['23942602', '0b12e9a2', '33595acb', '42c6555b', '236385ee',
            '1176c0df', '8ceb9c6e', 'c3110b6b', '2a90c095', 'aeea23e3']

NEW = {
    # ---- веха-21а полка 4-словных (regr22..regr29, W-22..W-29) ----
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
    'Python_compiler/neg_as2.words':    (0xFE, '5eae9fa0'),
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
    'Python_compiler/neg_va2.words':    (0xFE, '5ed0477b'),
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
    'Python_compiler/neg_ow2.words':    (0xFE, '30f2b201'),
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
    'Python_compiler/neg_sp2.words':    (0xFE, 'edaa4227'),
    'Python_compiler/pos_wc14v8if.words': (0xFF, '50fac32b'),
    'Python_compiler/target_if0.words': (0xFF, IF_MD5[0]),
    'Python_compiler/target_if1.words': (0xFF, IF_MD5[1]),
    'Python_compiler/target_if2.words': (0xFF, IF_MD5[2]),
    'Python_compiler/target_if3.words': (0xFF, IF_MD5[3]),
    'Python_compiler/target_if4.words': (0xFF, IF_MD5[4]),
    'Python_compiler/target_if5.words': (0xFF, IF_MD5[5]),
    'Python_compiler/target_if6.words': (0xFF, IF_MD5[6]),
    'Python_compiler/target_if7.words': (0xFF, IF_MD5[7]),
    'Python_compiler/target_if8.words': (0xFF, IF_MD5[8]),
    'Python_compiler/target_if9.words': (0xFF, IF_MD5[9]),
    'Python_compiler/neg_if2.words':    (0xFE, '04a1e74f'),
    'Python_compiler/pos_wc14v8te.words': (0xFF, '5f27f5f1'),
    'Python_compiler/target_te0.words': (0xFF, TE_MD5[0]),
    'Python_compiler/target_te1.words': (0xFF, TE_MD5[1]),
    'Python_compiler/target_te2.words': (0xFF, TE_MD5[2]),
    'Python_compiler/target_te3.words': (0xFF, TE_MD5[3]),
    'Python_compiler/target_te4.words': (0xFF, TE_MD5[4]),
    'Python_compiler/target_te5.words': (0xFF, TE_MD5[5]),
    'Python_compiler/target_te6.words': (0xFF, TE_MD5[6]),
    'Python_compiler/target_te7.words': (0xFF, TE_MD5[7]),
    'Python_compiler/target_te8.words': (0xFF, TE_MD5[8]),
    'Python_compiler/target_te9.words': (0xFF, TE_MD5[9]),
    'Python_compiler/neg_te2.words':    (0xFE, '86f32377'),
    'Python_compiler/pos_wc14v8sv.words': (0xFF, '8cf43f2b'),
    'Python_compiler/target_sv0.words': (0xFF, SV_MD5[0]),
    'Python_compiler/target_sv1.words': (0xFF, SV_MD5[1]),
    'Python_compiler/target_sv2.words': (0xFF, SV_MD5[2]),
    'Python_compiler/target_sv3.words': (0xFF, SV_MD5[3]),
    'Python_compiler/target_sv4.words': (0xFF, SV_MD5[4]),
    'Python_compiler/target_sv5.words': (0xFF, SV_MD5[5]),
    'Python_compiler/target_sv6.words': (0xFF, SV_MD5[6]),
    'Python_compiler/target_sv7.words': (0xFF, SV_MD5[7]),
    'Python_compiler/target_sv8.words': (0xFF, SV_MD5[8]),
    'Python_compiler/target_sv9.words': (0xFF, SV_MD5[9]),
    'Python_compiler/neg_sv2.words':    (0xFE, 'bbdb0170'),
    'Python_compiler/pos_wc14v8vw.words': (0xFF, 'be2c8bb8'),
    'Python_compiler/target_vw0.words': (0xFF, VW_MD5[0]),
    'Python_compiler/target_vw1.words': (0xFF, VW_MD5[1]),
    'Python_compiler/target_vw2.words': (0xFF, VW_MD5[2]),
    'Python_compiler/target_vw3.words': (0xFF, VW_MD5[3]),
    'Python_compiler/target_vw4.words': (0xFF, VW_MD5[4]),
    'Python_compiler/target_vw5.words': (0xFF, VW_MD5[5]),
    'Python_compiler/target_vw6.words': (0xFF, VW_MD5[6]),
    'Python_compiler/target_vw7.words': (0xFF, VW_MD5[7]),
    'Python_compiler/target_vw8.words': (0xFF, VW_MD5[8]),
    'Python_compiler/target_vw9.words': (0xFF, VW_MD5[9]),
    'Python_compiler/neg_vw2.words':    (0xFE, '9c9a7be6'),
    # ---- веха-21а хвост: Token-3 полка, спринт 1 (regr30, W-30) ----
    'Python_compiler/pos_wc14v9te.words': (0xFF, '2b52b636'),
    'Python_compiler/target_t3te0.words': (0xFF, T3TE_MD5[0]),
    'Python_compiler/target_t3te1.words': (0xFF, T3TE_MD5[1]),
    'Python_compiler/target_t3te2.words': (0xFF, T3TE_MD5[2]),
    'Python_compiler/target_t3te3.words': (0xFF, T3TE_MD5[3]),
    'Python_compiler/target_t3te4.words': (0xFF, T3TE_MD5[4]),
    'Python_compiler/target_t3te5.words': (0xFF, T3TE_MD5[5]),
    'Python_compiler/target_t3te6.words': (0xFF, T3TE_MD5[6]),
    'Python_compiler/target_t3te7.words': (0xFF, T3TE_MD5[7]),
    'Python_compiler/target_t3te8.words': (0xFF, T3TE_MD5[8]),
    'Python_compiler/target_t3te9.words': (0xFF, T3TE_MD5[9]),
    # neg Token-3 te = tracked neg_te2.words ('wc 0 te zz', один литерал,
    # md5 86f32377 - тот же) - отдельный файл НЕ дублируем (честность).
    # ---- веха-21а хвост, Token-3 спринт 2 (regr31, W-31) ----
    'Python_compiler/pos_wc14v9pr.words': (0xFF, '757d418c'),
    'Python_compiler/target_t3pr0.words': (0xFF, T3PR_MD5[0]),
    'Python_compiler/target_t3pr1.words': (0xFF, T3PR_MD5[1]),
    'Python_compiler/target_t3pr2.words': (0xFF, T3PR_MD5[2]),
    'Python_compiler/target_t3pr3.words': (0xFF, T3PR_MD5[3]),
    'Python_compiler/target_t3pr4.words': (0xFF, T3PR_MD5[4]),
    'Python_compiler/target_t3pr5.words': (0xFF, T3PR_MD5[5]),
    'Python_compiler/target_t3pr6.words': (0xFF, T3PR_MD5[6]),
    'Python_compiler/target_t3pr7.words': (0xFF, T3PR_MD5[7]),
    'Python_compiler/target_t3pr8.words': (0xFF, T3PR_MD5[8]),
    'Python_compiler/target_t3pr9.words': (0xFF, T3PR_MD5[9]),
    'Python_compiler/neg_t3pr.words':    (0xFE, '23c4d31d'),  # 'wc 0 pr zz' FC=1@3
    # ---- веха-21а хвост, Token-3 спринт 3 (regr32, W-32) ----
    'Python_compiler/pos_wc14v9as.words': (0xFF, '0f8467c0'),
    'Python_compiler/target_t3as0.words': (0xFF, T3AS_MD5[0]),
    'Python_compiler/target_t3as1.words': (0xFF, T3AS_MD5[1]),
    'Python_compiler/target_t3as2.words': (0xFF, T3AS_MD5[2]),
    'Python_compiler/target_t3as3.words': (0xFF, T3AS_MD5[3]),
    'Python_compiler/target_t3as4.words': (0xFF, T3AS_MD5[4]),
    'Python_compiler/target_t3as5.words': (0xFF, T3AS_MD5[5]),
    'Python_compiler/target_t3as6.words': (0xFF, T3AS_MD5[6]),
    'Python_compiler/target_t3as7.words': (0xFF, T3AS_MD5[7]),
    'Python_compiler/target_t3as8.words': (0xFF, T3AS_MD5[8]),
    'Python_compiler/target_t3as9.words': (0xFF, T3AS_MD5[9]),
    # neg Token-3 as = tracked neg_as2.words ('wc 0 as zz', один литерал,
    # md5 5eae9fa0 - тот же) - отдельный файл НЕ дублируем.
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

# ---- честная ПОЛКА 4-словных томов (8 томов, как regr29) ----
SHELF = [
    ('as', 'pos_wc14v8as.words', 'target_as'),
    ('va', 'pos_wc14v8va.words', 'target_va'),
    ('ow', 'pos_wc14v8ow.words', 'target_ow'),
    ('sp', 'pos_wc14v8sp.words', 'target_sp'),
    ('if', 'pos_wc14v8if.words', 'target_if'),
    ('te', 'pos_wc14v8te.words', 'target_te'),
    ('sv', 'pos_wc14v8sv.words', 'target_sv'),
    ('vw', 'pos_wc14v8vw.words', 'target_vw'),
]
shelf_ok = True
vol_paths = {}
for lex, pos_rel, _tbase in SHELF:
    art = jc(work_path, os.path.join(REPO, 'Python_compiler', pos_rel))
    if art is None:
        print('shelf: том %s не собрал бинарник' % lex); shelf_ok = False
        continue
    volp = os.path.join(TMP, 'regr30_vol_%s.ctos' % lex)
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
        ref = jc(work_path, src)
        got = jc(volp, src)
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
    # кросс-отказы: pr + первые цели чужих томов + Token-3-цель =
    # честное молчание (4-словный том требует p5, у Token-3 SRC5 за
    # терминатором == 0/EOF)
    for cross in ('target0.words', 'target_t3te0.words') + tuple(
            '%s0.words' % tb for _l, _p, tb in SHELF if tb != tbase):
        cx = os.path.join(REPO, 'Python_compiler', cross)
        g2 = jc(volp, cx)
        if g2 is None:
            print('shelf %s-vol on %s: молчание (честный отказ)' % (lex, cross))
        else:
            print('shelf %s-vol on %s: НЕ молчание (%d B)!!'
                  % (lex, cross, len(g2)))
            shelf_ok = False

# ---- ДОБАВЛЕНО: честная ПОЛКА Token-3 томов ----
# том te-T3: 10 / 10 на 'wc d te'; кросс-отказы на 4-словные цели и neg.
T3SHELF = [
    ('te', 'pos_wc14v9te.words', 'target_t3te'),
    ('pr', 'pos_wc14v9pr.words', 'target_t3pr'),
    ('as', 'pos_wc14v9as.words', 'target_t3as'),
]
for lex, pos_rel, tbase in T3SHELF:
    art = jc(work_path, os.path.join(REPO, 'Python_compiler', pos_rel))
    if art is None:
        print('t3: том %s не собрал бинарник' % lex); shelf_ok = False
        continue
    volp = os.path.join(TMP, 'regr30_t3_%s.ctos' % lex)
    io.open(volp, 'wb').write(art)
    print('t3 vol-%s: %d B md5 %s' % (lex, len(art),
                                      hashlib.md5(art).hexdigest()[:8]))
    ok10 = True
    for d in range(10):
        src = os.path.join(REPO, 'Python_compiler', '%s%d.words' % (tbase, d))
        ref = jc(work_path, src)   # свежий честный эталон stage1
        got = jc(volp, src)
        if ref is None or got is None:
            print('t3 %s%d: молчание тома/эталона' % (lex, d))
            ok10 = False
            continue
        if ref != got:
            print('t3 %s%d: MISMATCH' % (lex, d))
            ok10 = False
    print('t3 %s: %s' % (lex, '10/10 targets byte-ok' if ok10
                         else 'has mismatches above'))
    shelf_ok = shelf_ok and ok10
    for cs in ('wc 0 %s %s' % (lex, lex), 'wc 0 pr te', 'wc 0 %s zz' % lex):
        cx = os.path.join(REPO, 'Python_compiler', 'neg_as2.words')
        # кросс-исходники Token-3: инлайн-случаи через temp-файл
        tmpsrc = os.path.join(TMP, 'regr30_t3_cx.words')
        with io.open(tmpsrc, 'w', encoding='ascii') as f:
            f.write(cs + '\n')
        g2 = jc(volp, tmpsrc)
        if g2 is None:
            print('t3 %s-vol on %r: молчание (честный отказ)' % (lex, cs))
        else:
            print('t3 %s-vol on %r: НЕ молчание (%d B)!!'
                  % (lex, cs, len(g2)))
            shelf_ok = False

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
print('REGRESS OK (tracked IDENTICAL + 4-word-shelf 80/80 + T3-shelf '
      '30/30 + cross-silences + cold)')
