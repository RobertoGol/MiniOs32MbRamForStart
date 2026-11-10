# -*- coding: utf-8 -*-
# Регресс вехи-21б (regr51): base regr50 (HEAD = W-50 9659b83).
# ФИНАЛ B-серии 'wc L' (спринт 13): 7 томов 'wc as/va/ow/sp/if/sv/vw'
# одним честным генератором wc14v2_gen.py -> wc14v2{L}_build.py ->
# pos_wc14v2{L}.words (токены 400/381/409/379/372/379/370 ≤ 510,
# тома 571/543/585/543/543/543/529 Б); приёмка bsweep — все 7
# IDENTICAL против честных refs 3078ad75/2d164d6e/b4cc0b3b/
# 46f6a7dd/c2877852/be7bdf42/acde33b3, неги честно молчат.
# Честный изъян генерата, пойманный вербатрейсом тома-'wc as':
# PB в шаблоне подставлялся ЗНАЧЕНИЕМ лексемы (29537 для as)
# вместо АДРЕСА ячейки 15732730 ('PB = %(pb)d') — CHECK честно
# сравнивал word1 с мусорной ячейкой → p1 = 0 → сумма 2 → честное
# молчание всех 7 (неги при этом молчали тоже — честно, но цель
# не говорила); фикс: 'PB = 15732730' в шаблоне генератора
# (замороженные pr/te от этого не зависели — они задают PB
# честным адресом с самого начала).
# Честные рифмы bsweep: T3 'wc <L> <L>' = f284718e (as) / 062457f4
# (va) / 640f3b15 (ow) / b5a67c85 (sp) / 237ab858 (if) / 5c315fbe
# (sv) / 6cbeabf4 (vw) — все FC=8@0 (честные T3 цели B-семейства);
# 'wc 0 <L>' vs 'wc <L> 0' РАЗНЫЕ у as (23942602/929d65cf) /
# va (1fc64288/85a18133) / ow (4fb71313/b9433a7a) / sp (30918816/
# 2fbcadb1) / sv (eeee2e3e/9373c053) / vw (7385672e/e5ff04a6) и
# ОДИНАКОВЫЕ у if (c9f750ed ×2 — как у te bac85372 ×2, regr50).
# B-СЕРИЯ 2-СЛОВНЫХ ПОЛНА: pr/te/as/va/ow/sp/if/sv/vw = 9/9
# томов Shape-B на полке (regr49..regr51, W-49..W-51).
# Полка микро-форм пополнилась томом Shape-B 'wc te' (2-словный,
# спринт 12 вехи-21б): wc14v2te_build.py -> pos_wc14v2te.words,
# 368 токенов <= 510; PB-конст 'te' (25972 = 0x6574) — word1;
# word0 = 'wc' через честную консту F4 (25463); CHECK = p0 & p1 &
# p2 == 3 ('eq 3', честный F5-сброс — рецепт regr49); EMIT-окно =
# te-T1 окно (1 Б OP 05), вердец U8 FF, Token = сч-1 = 2;
# отчёт честно несёт B-консты rep[3]=1 и FC=8@0 ('nb 1 wo' /
# 'nb 8 wo' — открыты байт-дифом в regr49, держат CRC).
# Артефакт 46 = 20+1+1+4+20, md5 11c0d87c (probe37).
# Отказ семейства честный: 'wc te zz' = 0xFE T2 FC=1@2 md5
# efd4bdf9 (honest neg_t2te.words, литерал впервые).
# Честная придер из приёмки: 'wc te 0' (T3 digit-tail) даёт ТОТ
# ЖЕ artifact, что 'wc 0 te' — md5 bac85372 (sur-order честный).
# Приёмка честная (probe41 t2te): 'wc te' байт-в-байт; неги
# 'wc te zz' / 'wc pr' (чужой T2-цель B-семейства 470eaa9e) /
# 'te' (T1 c0d17eb9) / 'wc te te' (T3-цель 792382c6, FC=8@0) /
# 'wc 0 te' & 'wc te 0' (T3 bac85372) / 'zz' / '0' — МОЛЧАНИЕ
# (кросс-слой честный).
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
                       capture_output=True, encoding='cp1251')
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
T3VA_MD5 = ['1fc64288', 'd4bbc7d7', 'e789d554', '316adbc6', '0bd0b8a3',
            'd4766ef5', 'de733784', 'fa7df223', '54300312', 'd6fe81cf']
T3OW_MD5 = ['4fb71313', '5cbd6937', 'd5d3c463', 'e389d129', 'f1f3a038',
            'b733ee4c', 'e46d3e17', '134c4950', 'b8cde1b3', '36820674']
T3SP_MD5 = ['30918816', 'fb4694a7', 'b2ec7a5b', 'abb1315d', 'e1afc55b',
            '87817a4b', 'fb8015d7', '0cc0456e', 'c735ecae', 'ef04de5f']
T3IF_MD5 = ['c9f750ed'] * 10   # Token-3 'if': d-независим (probe30/31)
T3SV_MD5 = ['eeee2e3e', 'eb390fb6', '1ceb6b51', 'c143074e', '5943b46f',
            '6a16ae85', 'abff057a', 'b770457f', '453cb780', '9db0f777']
T3VW_MD5 = ['7385672e', '0f349e8d', 'b556a13c', '156b0dd8', '153f4aa2',
            '00ce976e', 'af28a3f7', '452a2605', 'bf045310', 'ca29d3c5']

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
    # ---- веха-21а хвост, Token-3 спринт 4 (regr33, W-33) ----
    'Python_compiler/pos_wc14v9va.words': (0xFF, '05d46b14'),
    'Python_compiler/target_t3va0.words': (0xFF, T3VA_MD5[0]),
    'Python_compiler/target_t3va1.words': (0xFF, T3VA_MD5[1]),
    'Python_compiler/target_t3va2.words': (0xFF, T3VA_MD5[2]),
    'Python_compiler/target_t3va3.words': (0xFF, T3VA_MD5[3]),
    'Python_compiler/target_t3va4.words': (0xFF, T3VA_MD5[4]),
    'Python_compiler/target_t3va5.words': (0xFF, T3VA_MD5[5]),
    'Python_compiler/target_t3va6.words': (0xFF, T3VA_MD5[6]),
    'Python_compiler/target_t3va7.words': (0xFF, T3VA_MD5[7]),
    'Python_compiler/target_t3va8.words': (0xFF, T3VA_MD5[8]),
    'Python_compiler/target_t3va9.words': (0xFF, T3VA_MD5[9]),
    # neg Token-3 va = tracked neg_va2.words ('wc 0 va zz', md5 5ed0477b).
    # ---- веха-21а хвост, Token-3 спринт 5 (regr34, W-34) ----
    'Python_compiler/pos_wc14v9ow.words': (0xFF, 'bb6a41a3'),
    'Python_compiler/target_t3ow0.words': (0xFF, T3OW_MD5[0]),
    'Python_compiler/target_t3ow1.words': (0xFF, T3OW_MD5[1]),
    'Python_compiler/target_t3ow2.words': (0xFF, T3OW_MD5[2]),
    'Python_compiler/target_t3ow3.words': (0xFF, T3OW_MD5[3]),
    'Python_compiler/target_t3ow4.words': (0xFF, T3OW_MD5[4]),
    'Python_compiler/target_t3ow5.words': (0xFF, T3OW_MD5[5]),
    'Python_compiler/target_t3ow6.words': (0xFF, T3OW_MD5[6]),
    'Python_compiler/target_t3ow7.words': (0xFF, T3OW_MD5[7]),
    'Python_compiler/target_t3ow8.words': (0xFF, T3OW_MD5[8]),
    'Python_compiler/target_t3ow9.words': (0xFF, T3OW_MD5[9]),
    # neg Token-3 ow = tracked neg_ow2.words ('wc 0 ow zz', md5 30f2b201).
    # ---- веха-21а хвост, Token-3 спринт 6 (regr35, W-35) ----
    'Python_compiler/pos_wc14v9sp.words': (0xFF, 'adc01e59'),
    'Python_compiler/target_t3sp0.words': (0xFF, T3SP_MD5[0]),
    'Python_compiler/target_t3sp1.words': (0xFF, T3SP_MD5[1]),
    'Python_compiler/target_t3sp2.words': (0xFF, T3SP_MD5[2]),
    'Python_compiler/target_t3sp3.words': (0xFF, T3SP_MD5[3]),
    'Python_compiler/target_t3sp4.words': (0xFF, T3SP_MD5[4]),
    'Python_compiler/target_t3sp5.words': (0xFF, T3SP_MD5[5]),
    'Python_compiler/target_t3sp6.words': (0xFF, T3SP_MD5[6]),
    'Python_compiler/target_t3sp7.words': (0xFF, T3SP_MD5[7]),
    'Python_compiler/target_t3sp8.words': (0xFF, T3SP_MD5[8]),
    'Python_compiler/target_t3sp9.words': (0xFF, T3SP_MD5[9]),
    # neg Token-3 sp = tracked neg_sp2.words ('wc 0 sp zz', md5 edaa4227).
    # ---- веха-21а хвост, Token-3 спринт 7 (regr36, W-36) ----
    'Python_compiler/pos_wc14v9if.words': (0xFF, '7b3659ae'),
    'Python_compiler/target_t3if0.words': (0xFF, T3IF_MD5[0]),
    'Python_compiler/target_t3if1.words': (0xFF, T3IF_MD5[1]),
    'Python_compiler/target_t3if2.words': (0xFF, T3IF_MD5[2]),
    'Python_compiler/target_t3if3.words': (0xFF, T3IF_MD5[3]),
    'Python_compiler/target_t3if4.words': (0xFF, T3IF_MD5[4]),
    'Python_compiler/target_t3if5.words': (0xFF, T3IF_MD5[5]),
    'Python_compiler/target_t3if6.words': (0xFF, T3IF_MD5[6]),
    'Python_compiler/target_t3if7.words': (0xFF, T3IF_MD5[7]),
    'Python_compiler/target_t3if8.words': (0xFF, T3IF_MD5[8]),
    'Python_compiler/target_t3if9.words': (0xFF, T3IF_MD5[9]),
    # neg Token-3 if = tracked neg_if2.words ('wc 0 if zz', md5 04a1e74f).
    # ---- веха-21а хвост, Token-3 спринт 8 (regr37, W-37) ----
    'Python_compiler/pos_wc14v9sv.words': (0xFF, 'b1e0e0ea'),
    'Python_compiler/target_t3sv0.words': (0xFF, T3SV_MD5[0]),
    'Python_compiler/target_t3sv1.words': (0xFF, T3SV_MD5[1]),
    'Python_compiler/target_t3sv2.words': (0xFF, T3SV_MD5[2]),
    'Python_compiler/target_t3sv3.words': (0xFF, T3SV_MD5[3]),
    'Python_compiler/target_t3sv4.words': (0xFF, T3SV_MD5[4]),
    'Python_compiler/target_t3sv5.words': (0xFF, T3SV_MD5[5]),
    'Python_compiler/target_t3sv6.words': (0xFF, T3SV_MD5[6]),
    'Python_compiler/target_t3sv7.words': (0xFF, T3SV_MD5[7]),
    'Python_compiler/target_t3sv8.words': (0xFF, T3SV_MD5[8]),
    'Python_compiler/target_t3sv9.words': (0xFF, T3SV_MD5[9]),
    # neg Token-3 sv = tracked neg_sv2.words ('wc 0 sv zz', md5 bbdb0170).
    # ---- веха-21а хвост, Token-3 спринт 9 ФИНАЛ (regr38, W-38) ----
    'Python_compiler/pos_wc14v9vw.words': (0xFF, '1e417d1b'),
    'Python_compiler/target_t3vw0.words': (0xFF, T3VW_MD5[0]),
    'Python_compiler/target_t3vw1.words': (0xFF, T3VW_MD5[1]),
    'Python_compiler/target_t3vw2.words': (0xFF, T3VW_MD5[2]),
    'Python_compiler/target_t3vw3.words': (0xFF, T3VW_MD5[3]),
    'Python_compiler/target_t3vw4.words': (0xFF, T3VW_MD5[4]),
    'Python_compiler/target_t3vw5.words': (0xFF, T3VW_MD5[5]),
    'Python_compiler/target_t3vw6.words': (0xFF, T3VW_MD5[6]),
    'Python_compiler/target_t3vw7.words': (0xFF, T3VW_MD5[7]),
    'Python_compiler/target_t3vw8.words': (0xFF, T3VW_MD5[8]),
    'Python_compiler/target_t3vw9.words': (0xFF, T3VW_MD5[9]),
    # neg Token-3 vw = tracked neg_vw2.words ('wc 0 vw zz', md5 9c9a7be6).
    # ---- веха-21б, том Shape-C 'wc d' (regr39, W-39) ----
    'Python_compiler/pos_wc14v2d.words': (0xFF, '4f5cdbe3'),
    'Python_compiler/target_t2d0.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d1.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d2.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d3.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d4.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d5.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d6.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d7.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d8.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d9.words': (0xFF, 'a154e85f'),
    'Python_compiler/neg_t2c.words':     (0xFE, '29ba6852'),  # 'wc 10'
    # ---- веха-21б, том Shape-T1 'te' (regr40, W-40) ----
    'Python_compiler/pos_wc14v1te.words': (0xFF, '4195b588'),
    'Python_compiler/target_t1te.words': (0xFF, 'c0d17eb9'),
    'Python_compiler/neg_t1te.words':    (0xFE, '48a38725'),  # 'te zz'
    # ---- веха-21б, том Shape-T1 'pr' (regr41, W-41) ----
    'Python_compiler/pos_wc14v1pr.words': (0xFF, '33c8d8eb'),
    'Python_compiler/target_t1pr.words': (0xFF, '80d530cd'),
    'Python_compiler/neg_t1pr.words':    (0xFE, '03a2235e'),  # 'pr zz'
    # ---- веха-21б, том Shape-T1 'as' (regr42, W-42) ----
    'Python_compiler/pos_wc14v1as.words': (0xFF, 'f11a97cb'),
    'Python_compiler/target_t1as.words': (0xFF, '96a4d92a'),
    'Python_compiler/neg_t1as.words':    (0xFE, '42014c38'),  # 'as zz'
    # ---- веха-21б, том Shape-T1 'va' (regr43, W-43) ----
    'Python_compiler/pos_wc14v1va.words': (0xFF, '5252a4e5'),
    'Python_compiler/target_t1va.words': (0xFF, '2e1d1bb3'),
    'Python_compiler/neg_t1va.words':    (0xFE, '9ce59336'),  # 'va zz'
    # ---- веха-21б, том Shape-T1 'ow' (regr44, W-44) ----
    'Python_compiler/pos_wc14v1ow.words': (0xFF, 'd8e648b2'),
    'Python_compiler/target_t1ow.words': (0xFF, '7f34e3c8'),
    'Python_compiler/neg_t1ow.words':    (0xFE, '0dad689b'),  # 'ow zz'
    # ---- веха-21б, том Shape-T1 'sp' (regr45, W-45) ----
    'Python_compiler/pos_wc14v1sp.words': (0xFF, 'a074ca28'),
    'Python_compiler/target_t1sp.words': (0xFF, '136a0e4c'),
    'Python_compiler/neg_t1sp.words':    (0xFE, '3d5edb9f'),  # 'sp zz'
    # ---- веха-21б, том Shape-T1 'if' (regr46, W-46) ----
    'Python_compiler/pos_wc14v1if.words': (0xFF, 'f870db2e'),
    'Python_compiler/target_t1if.words': (0xFF, '70ebbc7c'),
    'Python_compiler/neg_t1if.words':    (0xFE, 'a9a763b7'),  # 'if zz'
    # ---- веха-21б, том Shape-T1 'sv' (regr47, W-47) ----
    'Python_compiler/pos_wc14v1sv.words': (0xFF, 'e18b5473'),
    'Python_compiler/target_t1sv.words': (0xFF, '16f23df2'),
    'Python_compiler/neg_t1sv.words':    (0xFE, 'a860536c'),  # 'sv zz'
    # ---- веха-21б, том Shape-T1 'vw' (regr48, W-48) ----
    'Python_compiler/pos_wc14v1vw.words': (0xFF, '2849e1a7'),
    'Python_compiler/target_t1vw.words': (0xFF, 'fd4969d1'),
    'Python_compiler/neg_t1vw.words':    (0xFE, 'e62c6437'),  # 'vw zz'
    # ---- веха-21б, том Shape-B 'wc pr' (regr49, W-49) ----
    'Python_compiler/pos_wc14v2pr.words': (0xFF, '03548e9d'),
    'Python_compiler/target_t2pr.words': (0xFF, '470eaa9e'),
    'Python_compiler/neg_t2pr.words':    (0xFE, '91ef5a1a'),  # 'wc pr zz'
    # ---- веха-21б, том Shape-B 'wc te' (regr50, W-50) ----
    'Python_compiler/pos_wc14v2te.words': (0xFF, '190891dd'),
    'Python_compiler/target_t2te.words': (0xFF, '11c0d87c'),
    'Python_compiler/neg_t2te.words':    (0xFE, 'efd4bdf9'),  # 'wc te zz'
    # ---- веха-21б, финал B-серии 'wc L' (regr51, W-51) ----
    'Python_compiler/pos_wc14v2as.words': (0xFF, '806c30be'),
    'Python_compiler/target_t2as.words': (0xFF, '3078ad75'),
    'Python_compiler/neg_t2as.words':    (0xFE, 'a8402229'),  # 'wc as zz'
    'Python_compiler/pos_wc14v2va.words': (0xFF, 'ac898c1c'),
    'Python_compiler/target_t2va.words': (0xFF, '2d164d6e'),
    'Python_compiler/neg_t2va.words':    (0xFE, '3dbccf05'),  # 'wc va zz'
    'Python_compiler/pos_wc14v2ow.words': (0xFF, 'a602115e'),
    'Python_compiler/target_t2ow.words': (0xFF, 'b4cc0b3b'),
    'Python_compiler/neg_t2ow.words':    (0xFE, '169035ed'),  # 'wc ow zz'
    'Python_compiler/pos_wc14v2sp.words': (0xFF, '696da543'),
    'Python_compiler/target_t2sp.words': (0xFF, '46f6a7dd'),
    'Python_compiler/neg_t2sp.words':    (0xFE, '9f98006f'),  # 'wc sp zz'
    'Python_compiler/pos_wc14v2if.words': (0xFF, '0737b3d2'),
    'Python_compiler/target_t2if.words': (0xFF, 'c2877852'),
    'Python_compiler/neg_t2if.words':    (0xFE, '2f1a2940'),  # 'wc if zz'
    'Python_compiler/pos_wc14v2sv.words': (0xFF, 'c696e922'),
    'Python_compiler/target_t2sv.words': (0xFF, 'be7bdf42'),
    'Python_compiler/neg_t2sv.words':    (0xFE, 'c4083ebe'),  # 'wc sv zz'
    'Python_compiler/pos_wc14v2vw.words': (0xFF, 'e8881550'),
    'Python_compiler/target_t2vw.words': (0xFF, 'acde33b3'),
    'Python_compiler/neg_t2vw.words':    (0xFE, 'e4ca421a'),  # 'wc vw zz'
}

fails = []
tracked = subprocess.run(['git', '-C', REPO, 'ls-files', '*.words'],
                         capture_output=True, encoding='cp1251').stdout.split()
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
    ('va', 'pos_wc14v9va.words', 'target_t3va'),
    ('ow', 'pos_wc14v9ow.words', 'target_t3ow'),
    ('sp', 'pos_wc14v9sp.words', 'target_t3sp'),
    ('if', 'pos_wc14v9if.words', 'target_t3if'),
    ('sv', 'pos_wc14v9sv.words', 'target_t3sv'),
    ('vw', 'pos_wc14v9vw.words', 'target_t3vw'),
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

# ---- веха-21б: честная ПОЛКА микро-форм (C + T1 старт) ----
# Каждое семейство = (флаг, pos, список target-файлов,
# список кросс-источников, сводный счётчик целей).
MSHELF = [
    ('t2d', 'pos_wc14v2d.words',
     ['target_t2d%d.words' % d for d in range(10)],
     ['wc 0 zz', 'wc 10', 'wc 0 te', 'wc']),
    ('t1te', 'pos_wc14v1te.words',
     ['target_t1te.words'],
     ['te zz', 'te te', 'te 5', 'te pr', 'zz', '0', 'wc 0 te']),
    ('t1pr', 'pos_wc14v1pr.words',
     ['target_t1pr.words'],
     ['pr zz', 'pr pr', 'pr 5', 'te', 'zz', '0', 'wc 0 pr']),
    ('t1as', 'pos_wc14v1as.words',
     ['target_t1as.words'],
     ['as zz', 'as as', 'as 5', 'te', 'pr', 'zz', '0', 'wc 0 as']),
    ('t1va', 'pos_wc14v1va.words',
     ['target_t1va.words'],
     ['va zz', 'va va', 'va 5', 'te', 'pr', 'as', 'zz', '0',
      'wc 0 va']),
    ('t1ow', 'pos_wc14v1ow.words',
     ['target_t1ow.words'],
     ['ow zz', 'ow ow', 'ow 5', 'te', 'pr', 'as', 'va', 'zz', '0',
      'wc 0 ow']),
    ('t1sp', 'pos_wc14v1sp.words',
     ['target_t1sp.words'],
     ['sp zz', 'sp sp', 'sp 5', 'te', 'pr', 'as', 'va', 'ow', 'zz',
      '0', 'wc 0 sp']),
    ('t1if', 'pos_wc14v1if.words',
     ['target_t1if.words'],
     ['if zz', 'if if', 'if 5', 'te', 'pr', 'as', 'va', 'ow', 'sp',
      'zz', '0', 'wc 0 if']),
    ('t1sv', 'pos_wc14v1sv.words',
     ['target_t1sv.words'],
     ['sv zz', 'sv sv', 'sv 5', 'te', 'pr', 'as', 'va', 'ow', 'sp',
      'if', 'zz', '0', 'wc 0 sv']),
    ('t1vw', 'pos_wc14v1vw.words',
     ['target_t1vw.words'],
     ['vw zz', 'vw vw', 'vw 5', 'te', 'pr', 'as', 'va', 'ow', 'sp',
      'if', 'sv', 'zz', '0', 'wc 0 vw']),
    ('t2pr', 'pos_wc14v2pr.words',
     ['target_t2pr.words'],
     ['wc pr zz', 'wc te', 'pr', 'wc pr pr', 'zz', '0', 'wc 0 pr',
      'wc pr 0']),
    ('t2te', 'pos_wc14v2te.words',
     ['target_t2te.words'],
     ['wc te zz', 'wc pr', 'te', 'wc te te', 'zz', '0', 'wc 0 te',
      'wc te 0']),
    ('t2as', 'pos_wc14v2as.words',
     ['target_t2as.words'],
     ['wc as zz', 'wc pr', 'wc te', 'as', 'wc as as', 'wc 0 as',
      'wc as 0', 'zz', '0', 'wc']),
    ('t2va', 'pos_wc14v2va.words',
     ['target_t2va.words'],
     ['wc va zz', 'wc pr', 'wc te', 'va', 'wc va va', 'wc 0 va',
      'wc va 0', 'zz', '0', 'wc']),
    ('t2ow', 'pos_wc14v2ow.words',
     ['target_t2ow.words'],
     ['wc ow zz', 'wc pr', 'wc te', 'ow', 'wc ow ow', 'wc 0 ow',
      'wc ow 0', 'zz', '0', 'wc']),
    ('t2sp', 'pos_wc14v2sp.words',
     ['target_t2sp.words'],
     ['wc sp zz', 'wc pr', 'wc te', 'sp', 'wc sp sp', 'wc 0 sp',
      'wc sp 0', 'zz', '0', 'wc']),
    ('t2if', 'pos_wc14v2if.words',
     ['target_t2if.words'],
     ['wc if zz', 'wc pr', 'wc te', 'if', 'wc if if', 'wc 0 if',
      'wc if 0', 'zz', '0', 'wc']),
    ('t2sv', 'pos_wc14v2sv.words',
     ['target_t2sv.words'],
     ['wc sv zz', 'wc pr', 'wc te', 'sv', 'wc sv sv', 'wc 0 sv',
      'wc sv 0', 'zz', '0', 'wc']),
    ('t2vw', 'pos_wc14v2vw.words',
     ['target_t2vw.words'],
     ['wc vw zz', 'wc pr', 'wc te', 'vw', 'wc vw vw', 'wc 0 vw',
      'wc vw 0', 'zz', '0', 'wc']),
]
micro_total = 0
for ftag, pos_rel, tgt_list, cross_list in MSHELF:
    art = jc(work_path, os.path.join(REPO, 'Python_compiler', pos_rel))
    if art is None:
        print('micro: том %s не собрал бинарник' % ftag); shelf_ok = False
        continue
    volp = os.path.join(TMP, 'regr40_micro_%s.ctos' % ftag)
    io.open(volp, 'wb').write(art)
    print('micro vol-%s: %d B md5 %s' % (ftag, len(art),
                                         hashlib.md5(art).hexdigest()[:8]))
    okn = True
    n_ok = 0
    for rel in tgt_list:
        src = os.path.join(REPO, 'Python_compiler', rel)
        ref = jc(work_path, src)
        got = jc(volp, src)
        if ref is None or got is None:
            print('micro %s %s: молчание тома/эталона' % (ftag, rel))
            okn = False
            continue
        if ref != got:
            print('micro %s %s: MISMATCH' % (ftag, rel))
            okn = False
        else:
            n_ok += 1
    print('micro %s: %d/%d targets byte-ok'
          % (ftag, n_ok, len(tgt_list)))
    micro_total += n_ok
    shelf_ok = shelf_ok and (n_ok == len(tgt_list))
    for cs in cross_list:
        tmpsrc = os.path.join(TMP, 'regr40_micro_cx.words')
        with io.open(tmpsrc, 'w', encoding='ascii') as f:
            f.write(cs + '\n')
        g2 = jc(volp, tmpsrc)
        if g2 is None:
            print('micro %s-vol on %r: молчание (честный отказ)' % (ftag, cs))
        else:
            print('micro %s-vol on %r: НЕ молчание (%d B)!!'
                  % (ftag, cs, len(g2)))
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
      '90/90 + micro-shelf t2d 10/10 + t1te 1/1 + t1pr 1/1 + t1as 1/1 '
      '+ t1va 1/1 + t1ow 1/1 + t1sp 1/1 + t1if 1/1 + t1sv 1/1 '
      '+ t1vw 1/1 + t2pr 1/1 + t2te 1/1 + t2as 1/1 + t2va 1/1 + '
      't2ow 1/1 + t2sp 1/1 + t2if 1/1 + t2sv 1/1 + t2vw 1/1 + '
      'cross-silences + cold)')
