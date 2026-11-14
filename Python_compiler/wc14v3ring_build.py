# -*- coding: utf-8 -*-
# Том-кольцо 24а+24б+24б-3 (веха-24, спринты 92-96, W-112..W-117, TKT-052):
# generic 'nb d+ ne' + голые цифры (24а) + A-виды nb-пары sv/sc (24б-1)
# + gp/sp (24б-2) + B-виды va/cp/aa (24б-3, спринт 96: граница тома
# поднята W-116 0x400->0x800 по бюджет-приговору W-115). Приёмка:
# card112/card113 позитивы BYTE-OK, неги = молчание.
#
# СТРУКТУРА (позиционные if/es-пары; 'if' = acc!=0 -> then, acc==0 -> es;
#   'te' = честное завершение программы; es-JMP -> TERM):
#   INIT | mk [SCAN] stay-if#1 ... jb es#1 | PS | silent-if#2 te es#2
#   | BEGIN header | mk [EMIT] vcnt-if#3 jb es#3 | TAIL(SEAL,END)
#   if#1: stay!=0 -> CNT+=1, jb (скан); stay==0 -> es#1 -> PS;
#   if#2: silent!=0 (дурь) -> te (молчание); silent==0 -> es#2 -> BEGIN;
#   if#3: VCNT!=0 -> emit-тело, jb; VCNT==0 -> es#3 -> TAIL.
#
# ГРАММАТИКА: поглотители БЕЗ ne: 'nb <digits> <va|sv|cp|aa|sc|em|wo|gp|sp>';
#   CONST = 'nb <digits> ne'; literal-опы = '<op> <digit>' (eq/su/gt/ad/ml);
#   слоты: 'wc d va|sv|as|sp|gp|ow' (bare 'va/sv/sp/gp' = W_Current).
#
# СЛОТЫ: F3 NumAcc(0), F4 PTR(1), F5 CNT(2), F6 RF(3), F7 EFA(4), F8 POS(5),
#   F9 S(6), FA FCODE(7), FB gp-регистр(8), FC VCNT(9).
# SCRAP: 60 Z0(0), 61 VSC, 62 NBFA, 63 NEFA, 64 DTFA, 65 DGFA, 66 NKFA,
#   67 BKFA, 68 S0FA, 69 FSA, 70 KA, 71 NOEFA, 72 EFAsc, 73 BSFA, 74 SINK,
#   75/76 ZP(&74,&F8), 77/78 ZV(&61,&F3), 79/80 ZN(&60,&81), 81 ACEL,
#   82 POS2, 84/85 ZP2(&60,&82). 24б: 86 SVFA, 87 SCFA, 88 SVWC, 89 SCWC.
#   24б-3 (переселение — TAGTAB вырос до 8): 90..97 TAGTAB[0..7] (U16-теги:
#   0x1500 ne/dig, 0x5500 sv, 0x1300 sc, 0x5200 gp, 0x5300 sp, 0x1219 va,
#   0x1218 cp, 0x1215 aa), 101 K2FA (веса: sv+2sc+3gp+4sp+5va+6cp+7aa;
#   ne/цифры → 0), 102 KINDA (is_kind = is_ne + (k>0)), 103 GPWC,
#   104 SPWC, 105 GPFA, 106 SPFA (ЧЕСТНЫЙ УРОК W-114: флаги НЕЛЬЗЯ ставить
#   в диапазон TAGTAB — флаг-блок забивает ячейку КАЖДЫЙ проход; пойман
#   байт-дифом: тег 0x01 вместо 0x52), 107 VAWC, 108 CPWC, 109 AAWC,
#   110 VAFA, 111 CPFA, 112 AAFA, 114 POSC (машина позиций записей, init 20).
# SELF-консты: cell[46]:=46, [25198]:='nb', [25966]:='ne', [30323]:='sv',
#   [25459]:='sc', [28775]:='gp', [28787]:='sp', [30305]:='va',
#   [25456]:='cp', [24929]:='aa' (сравнение W == cell[W]).

def N(v):
    return ['nb'] + list(str(int(v))) + ['ne']

def ABS(v, op):
    return ['nb'] + list(str(int(v))) + [op]

WORDC, EOFC = 15732720, 15732722
F3A, F4A, F8A = 15732723, 15732724, 15732728
ARR = 10489856
Z0, VSC, NBFA, NEFA, DTFA, DGFA = 60, 61, 62, 63, 64, 65
NKFA, BKFA, S0FA, FSA, KA, NOEFA = 66, 67, 68, 69, 70, 71
EFASC, BSFA, SINK, ZPA, ZPB = 72, 73, 74, 75, 76
ZVA, ZVB, ZNA, ZNB, ACEL, POS2 = 77, 78, 79, 80, 81, 82
ZP2A, ZP2B = 84, 85
NBW, NEW_, DOTW = 25198, 25966, 46
SVW, SCW = 30323, 25459                     # 'sv'=0x7673 ('v'<<8|'s'), 'sc'=0x6373 ('c'<<8|'s')
GPW, SPW = 28775, 28787                     # 'gp'=0x7067 ('p'<<8|'g'), 'sp'=0x7073
VAW, CPW, AAW = 24950, 28771, 24929         # 24б-3: 'va'=0x6176 ('v'<<0|'a'<<8), 'cp'=0x7063, 'aa'=0x6161
SVFA, SCFA, GPFA, SPFA = 86, 87, 105, 106   # флаги A-видов (105/106 — ВНЕ TAGTAB 90..97!)
VAFA, CPFA, AAFA = 110, 111, 112            # 24б-3: флаги B-видов (вне TAGTAB — урок W-114)
SVWC, SCWC, GPWC, SPWC = 88, 89, 103, 104   # ячейки word-кодов A-видов (103/104 переселены)
VAWC, CPWC, AAWC = 107, 108, 109            # 24б-3: word-коды B-видов
TAGTAB, K2FA, KINDA = 90, 101, 102          # TAGTAB = 8 тегов U16 (90..97); K2FA = веса; KINDA = is_kind
STREAM, POSC = 15732720, 114                # 0x00F00FF0 (ячейка-аргумент syscall); POSC = машина позиций

def sel_val(anchor, flag):
    """acc = flag ? cell[candB] : cell[candA]; двойной gp (затирает acc)."""
    return (N(anchor) + ['wc', '8', 'sv'] + ABS(flag, 'va')
            + ['wc', '8', 'as', 'gp', 'wc', '8', 'sv', 'gp'])

INIT = []
INIT += N(NBW) + ABS(NBW, 'sv')            # cell[25198] := 25198
INIT += N(NEW_) + ABS(NEW_, 'sv')          # cell[25966] := 25966
INIT += N(DOTW) + ABS(DOTW, 'sv')          # cell[46] := 46
INIT += N(0) + ABS(Z0, 'sv')               # Z0 = 0
INIT += N(SINK) + ABS(ZPA, 'sv') + N(F8A) + ABS(ZPB, 'sv')
INIT += N(VSC) + ABS(ZVA, 'sv') + N(F3A) + ABS(ZVB, 'sv')
INIT += N(Z0) + ABS(ZNA, 'sv') + N(ACEL) + ABS(ZNB, 'sv')
INIT += N(Z0) + ABS(ZP2A, 'sv') + N(POS2) + ABS(ZP2B, 'sv')
INIT += N(ARR) + ['wc', '1', 'sv']         # PTR = ARR
INIT += N(ARR) + ['wc', '8', 'sv']         # FB = ARR (emit-gp база)
INIT += N(0) + ['wc', '0', 'sv']           # NumAcc = 0
INIT += N(0) + ['wc', '2', 'sv']           # CNT = 0
INIT += N(0) + ['wc', '3', 'sv']           # RF = 0
INIT += N(0) + ['wc', '5', 'sv']           # POS = 0
INIT += N(0) + ['wc', '6', 'sv']           # S = 0
INIT += N(0) + ['wc', '9', 'sv']           # VCNT = 0
# 24б: word-коды новых видов + TAGTAB (0x15 CONST / 0x55 STORE_AT / 0x13 SYSCALL)
INIT += N(SVW) + ABS(SVWC, 'sv')           # cell[88] := 30323
INIT += N(SCW) + ABS(SCWC, 'sv')           # cell[89] := 25459
INIT += N(5376) + ABS(TAGTAB, 'sv')         # [0] 0x1500 (ne/dig, k=0; болван 00 @P+1 затирается b0)
INIT += N(21760) + ABS(TAGTAB + 1, 'sv')    # [1] 0x5500 (sv, k=1)
INIT += N(4864) + ABS(TAGTAB + 2, 'sv')     # [2] 0x1300 (sc, k=2)
INIT += N(20992) + ABS(TAGTAB + 3, 'sv')    # [3] 0x5200 (gp, k=3)
INIT += N(21248) + ABS(TAGTAB + 4, 'sv')    # [4] 0x5300 (sp, k=4)
INIT += N(4633) + ABS(TAGTAB + 5, 'sv')     # [5] 0x1219 (va, k=5; X@P+2)
INIT += N(4632) + ABS(TAGTAB + 6, 'sv')     # [6] 0x1218 (cp, k=6)
INIT += N(4629) + ABS(TAGTAB + 7, 'sv')     # [7] 0x1215 (aa, k=7)
INIT += N(GPW) + ABS(GPWC, 'sv')           # cell[103] := 28775
INIT += N(SPW) + ABS(SPWC, 'sv')           # cell[104] := 28787
# 24б-3: word-коды B-видов + is_b-семафоры + POSC-машина
INIT += N(VAW) + ABS(VAWC, 'sv')           # cell[107] := 30305
INIT += N(CPW) + ABS(CPWC, 'sv')           # cell[108] := 25456
INIT += N(AAW) + ABS(AAWC, 'sv')           # cell[109] := 24929
INIT += N(1) + ABS(4633, 'sv')             # cell[0x1219] := 1 (is_b: va)
INIT += N(1) + ABS(4632, 'sv')             # cell[0x1218] := 1 (is_b: cp)
INIT += N(1) + ABS(4629, 'sv')             # cell[0x1215] := 1 (is_b: aa)
INIT += N(20) + ABS(POSC, 'sv')            # POSC := 20 (16 шапки + 4 CRC; байт-дифф a318d454)

LB = []
LB += ABS(311, 'sc')                       # прочесть слово (311 = FILE_GET)
# E-блок
LB += ABS(EOFC, 'va') + ['wc', '7', 'sv']            # EFA = EOF
LB += ABS(EFASC, 'sv')                               # EFAsc = EOF
LB += ['wc', '7', 'va', 'eq', '0'] + ABS(NOEFA, 'sv')  # NOEA = (E==0)
# флаги слова
# 24б-2: FB := WORDC (restore — sel_val/ml/POS-stamp/tag-трюк клянут FB);
#   все WORDC-грузки = bare 'gp' через FB (3 ток вместо 10).
#   ЧЕСТНЫЙ УРОК (пойман FCODE=12/POS=363 на первом прогоне): 'as' с
#   открытым nb = fail-fast 0x0C — накопление cell[X] += acc НЕЛЕГАЛЬНО,
#   'as' честен только bare (*W_Current) или slot ('wc d as'). Поэтому
#   A-виды: флаг-ячейки (cp+sv), затем веса в acc через 'aa' (легально,
#   доказано 24б-1).
LB += N(WORDC) + ['wc', '8', 'sv']                               # FB := WORDC
LB += ['wc', '8', 'gp'] + ABS(NBW, 'cp') + ABS(NBFA, 'sv')       # is_nb
LB += ['wc', '8', 'gp'] + ABS(NEW_, 'cp') + ABS(NEFA, 'sv')      # is_ne
LB += ['wc', '8', 'gp'] + ABS(DOTW, 'cp') + ABS(DTFA, 'sv')      # is_dot
LB += ['wc', '8', 'gp'] + ABS(SVWC, 'cp') + ABS(SVFA, 'sv')      # is_sv
LB += ['wc', '8', 'gp'] + ABS(SCWC, 'cp') + ABS(SCFA, 'sv')      # is_sc
LB += ['wc', '8', 'gp'] + ABS(GPWC, 'cp') + ABS(GPFA, 'sv')      # is_gp
LB += ['wc', '8', 'gp'] + ABS(SPWC, 'cp') + ABS(SPFA, 'sv')      # is_sp
LB += ['wc', '8', 'gp'] + ABS(VAWC, 'cp') + ABS(VAFA, 'sv')      # is_va (24б-3)
LB += ['wc', '8', 'gp'] + ABS(CPWC, 'cp') + ABS(CPFA, 'sv')      # is_cp (24б-3)
LB += ['wc', '8', 'gp'] + ABS(AAWC, 'cp') + ABS(AAFA, 'sv')      # is_aa (24б-3)
# взвешенный k = is_sv + 2*is_sc + 3*is_gp + 4*is_sp (БЕЗ ne — ne/цифры дают
#   k=0 → TAGTAB[0] = 0x15, семантика 24б-1); KINDA = is_kind = is_ne + (k>0)
#   (ne и A-виды взаимоисключающи — ne не A-вид). ЧЕСТНЫЕ УРОКИ этого
#   спринта: (1) 'as' с открытым nb = брак 0x0C (накопление cell[X] += acc
#   нелегально — только bare/slot-'as'); (2) 'wc 6 aa' = slot-'aa' = брак
#   0x0C — 'aa'/'cp' честны только с nb-открытой ЯЧЕЙКОЙ (слот принимают
#   va/sp/as/gp/ow/sv). Поэтому is_kind живёт в ячейке KINDA.
LB += ABS(SVFA, 'va') + ABS(SCFA, 'aa') * 2 + ABS(GPFA, 'aa') * 3 \
    + ABS(SPFA, 'aa') * 4 + ABS(VAFA, 'aa') * 5 + ABS(CPFA, 'aa') * 6 \
    + ABS(AAFA, 'aa') * 7 + ABS(K2FA, 'sv')                        # K2FA := k
LB += ABS(K2FA, 'va') + ['gt', '0'] + ABS(NEFA, 'aa') + ABS(KINDA, 'sv')  # is_kind
LB += ['wc', '8', 'gp'] + ['su', '8'] * 6 + ABS(VSC, 'sv')   # V = W-48 (gp через FB)
LB += ABS(VSC, 'va') + ['gt', '9', 'eq', '0'] + ABS(DGFA, 'sv')  # is_dig
# bareK = (is_dig + (S==0)) == 2
LB += ['wc', '6', 'va', 'eq', '0'] + ABS(S0FA, 'sv')
LB += ABS(DGFA, 'va') + ABS(S0FA, 'aa') + ['eq', '2'] + ABS(BKFA, 'sv')
# neK = (S + is_kind)==2 (честно: acc-арифметика, БЕЗ мутации S — урок: bare 'as'
# не возвращает сумму в acc, acc не меняется; is_kind из KINDA — cell-'aa')
LB += ['wc', '6', 'va'] + ABS(KINDA, 'aa') + ['eq', '2'] + ABS(NKFA, 'sv')
# f = (S_now==1) И (is_kind==0) ≡ (S + KINDA)==1 — ОДНА строка (экономия 22
#   ток против пары eq-1/eq-0 конъюнкций; сумма∈{0,1,2}: 1 ⟺ S=1 и not-kind)
LB += ['wc', '6', 'va'] + ABS(KINDA, 'aa') + ['eq', '1'] + ABS(FSA, 'sv')
# S' = clamp(is_nb + f)  — ДО затвора (выполняется и на leave)
LB += ABS(NBFA, 'va') + ABS(FSA, 'aa') + ['gt', '0', 'wc', '6', 'sv']
# K = neK + bareK; K' = ((K==1) + notEOF) == 2
LB += ABS(NKFA, 'va') + ABS(BKFA, 'aa')
LB += ['eq', '1'] + ABS(NOEFA, 'aa') + ['eq', '2'] + ABS(KA, 'sv')
# storeval = neK ? NumAcc(старый) : V; cell[PTR] := storeval (sp-always).
#   ПОРЯДОК ЧЕСТНЫЙ: *p = v; p++ — storeval ДО инкремента PTR (урок трассы:
#   'wc 1 sp' после 'PTR += K'' писал на ячейку дальше, EMIT читал нули).
LB += sel_val(ZVA, NKFA) + ['wc', '1', 'sp']
# PTR += K; VCNT += K
LB += ABS(KA, 'va') + ['wc', '1', 'as']
LB += ABS(KA, 'va') + ['wc', '9', 'as']
# тег записи (24б-2): взвешенный k уже в K2FA (из блока флагов); FB :=
#   TAGTAB + k; *p = tag; p += K' — KA держит K' до этого места (S-стеш
#   ниже его забирает), KP2FA-ячейка устранена. Запись [X][tag].
LB += N(TAGTAB) + ['wc', '8', 'sv']                 # FB := TAGTAB
LB += ABS(K2FA, 'va') + ['wc', '8', 'as']           # FB += k
LB += ['wc', '8', 'gp']                             # acc := tag
LB += ['wc', '1', 'sp']                             # cell[PTR] := tag
LB += ABS(KA, 'va') + ['wc', '1', 'as']             # PTR += K'
# S-стеш вокруг 'ml': ml (веха-12б) честно компилируется в runtime-кольцо
#   умножения со скретчем TMP_X=0xF00FFB(FB), TMP_CNT=0xF00FF9(СЛОТ S!),
#   TMP_ACC=0xF00FFA — БЕЗ стеша S обнуляется каждым ml и машина состояний
#   nb-прогона умирает ('ne' становился bad-словом, честно поймано трассой).
#   KA свободен: K' уже поглощён (PTR/VCNT += K' выше).
LB += ['wc', '6', 'va'] + ABS(KA, 'sv')             # стеш S -> KA
# A = 10*NumAcc + V; ACEL := A
LB += ['wc', '0', 'va', 'ml', '9'] + ABS(F3A, 'aa') + ABS(VSC, 'aa')
LB += ABS(ACEL, 'sv')
LB += ABS(KA, 'va') + ['wc', '6', 'sv']             # restore S <- KA
# NumAcc' = is_dig ? A : 0
LB += sel_val(ZNA, DGFA) + ['wc', '0', 'sv']
# POS-stamp: g = (is_nb + notEOF)==2 (конъюнкция честно aa+eq2, без if);
#   addr = cell[ZPA+g] (74|F8A) через ОДИН gp; cell[addr] := CNT (штамп = CNT,
#   0-based индекс текущего слова; CNT-1 давал бы Pos=0xFFFFFFFF на 'nb').
#   KA переиспользуется: K' уже поглощён (PTR/VCNT += K' выше).
LB += ABS(NBFA, 'va') + ABS(NOEFA, 'aa') + ['eq', '2'] + ABS(KA, 'sv')
LB += N(ZPA) + ['wc', '8', 'sv']
LB += ABS(KA, 'va') + ['wc', '8', 'as']
LB += ['gp', 'wc', '8', 'sv']
LB += ['wc', '2', 'va', 'wc', '8', 'sp']
# notbad = is_nb+is_dot+is_dig+neK; badsum = (notbad==0) -> BSFA
LB += ABS(NBFA, 'va') + ABS(DTFA, 'aa') + ABS(DGFA, 'aa') + ABS(NKFA, 'aa')
LB += ['eq', '0'] + ABS(BSFA, 'sv')
# L = (badsum + E + dot) > 0; stay = (L==0)
LB += ABS(BSFA, 'va') + ABS(EFASC, 'aa') + ABS(DTFA, 'aa') + ['gt', '0']
LB += ['eq', '0', 'if']                    # if#1: stay
LB += ['wc', '2', 'as']                    # CNT += stay (then-путь)
LB += ['jb', 'es']

PS = []
# opennb = (S==1) И ((E+dot)>0)
PS += ABS(EFASC, 'va') + ABS(DTFA, 'aa') + ['gt', '0'] + ABS(S0FA, 'sv')
PS += ['wc', '6', 'va', 'eq', '1'] + ABS(S0FA, 'aa') + ['eq', '2']
PS += ABS(FSA, 'sv')                       # opennb
# RF += opennb; FCODE = 9*RF
PS += ['wc', '3', 'as']
PS += ['wc', '3', 'va', 'ml', '9', 'wc', '7', 'sv']
# POS = opennb ? POS : 0
PS += ['wc', '5', 'va'] + ABS(POS2, 'sv')
PS += sel_val(ZP2A, FSA) + ['wc', '5', 'sv']
# Затвор: silent = (is_dot + E)==0 (дурь = bad-leave: не EOF и не точка).
#   silent==1 -> then='te' = ЧЕСТНОЕ молчание (rc==0, нет .out);
#   silent==0 (EOF- или dot-leave) -> es -> BEGIN (позитивы пишут артефакт).
PS += ABS(DTFA, 'va') + ABS(EFASC, 'aa') + ['eq', '0', 'if']   # if#2
PS += ['te', 'es']
# BEGIN + заголовок (0x43544F53, 0x01010100, 0x14000000, 0xFFFFAAAA, CRC)
#   'wo' = ВОСЬМОЙ поглотитель nb: честная форма 'nb <цифры> wo' БЕЗ 'ne'
#   (урок: 'ne' закрывает консту -> wo без числа = fail-fast 0x12 BRK_WO_NO_NUM).
PS += ABS(304, 'sc')


def NW(v):
    return ['nb'] + list(str(int(v))) + ['wo']


PS += NW(1129598803)
PS += NW(16843008)
PS += NW(335544320)
PS += NW(4294945450)
PS += ['nb', '0', 'wo']
PS += N(ARR) + ['wc', '8', 'sv']           # FB = ARR заново
# EMIT-кольцо: while VCNT != 0: прочесть [X][tag]; U8(tag); BE32(X); FB+=2; VCNT--
PS += ['mk']
PS += ['wc', '9', 'va', 'if']              # if#3: VCNT==0 -> TAIL
# 24б-3: единый 3-шаговый эмит (диспетчер БЕЗ ветвления, решение P4):
#   U16(TAG16) + SEEK(POSC + 1 + is_b) + PUT(X); записи [X][TAG16] (порядок
#   скана, FB идёт по парам). A-виды: U16 = [TT][00], SEEK(P+1) -> PUT
#   затирает болван b0 — байты [TT][b0..b3] те же; B-виды: U16 =
#   [0x12][канал], SEEK(P+2) = no-op (указатель уже там) ->
#   [0x12][канал][b0..b3] ровно 6Б. is_b = cell[TAG16] (семафоры
#   4633/4632/4629 := 1; A-теги = честный дефолт VM 0). POSC (cell[114]) =
#   позиция следующей записи: init 20, advance T+4 = +5 (A) / +6 (B).
PS += ['wc', '8', 'gp', 'wc', '0', 'sv']   # NumAcc := cell[*FB] = X
PS += ['wc', '8', 'va', 'ad', '1', 'sv']   # FB += 1 (на TAG16)
PS += ['wc', '8', 'gp']                    # acc := TAG16
PS += ABS(STREAM, 'sv')                    # stream := TAG16
PS += ABS(306, 'sc')                       # FILE_U16 -> [b1][b2] @P
PS += ['wc', '1', 'sv']                    # PTR := TAG16 (holder для is_b)
PS += ['gp']                               # acc := cell[TAG16] = is_b (0/1)
PS += ABS(POSC, 'aa') + ['ad', '1']        # acc := T = POSC + 1 + is_b
PS += ABS(STREAM, 'sv')                    # stream := T
PS += ABS(310, 'sc')                       # FILE_SEEK(T): A@P+1, B@P+2 (no-op)
PS += ['wc', '0', 'ow']                    # PUT(X): BE32 @T; acc = T жив
PS += ['ad', '4'] + ABS(POSC, 'sv')        # POSC := T + 4 (+5 A / +6 B)
PS += ['wc', '8', 'va', 'ad', '1', 'sv']   # FB += 1 (на след. X)
PS += ['wc', '9', 'va', 'su', '1', 'sv']   # VCNT -= 1
PS += ['jb', 'es']
# TAIL: вердец 0xFF + отчёт [CNT,0,0,RF,FCODE,POS] + SEAL + END
PS += ['nb', '2', '5', '5', 'em', 'nb', '3', '0', '8', 'sc']
PS += ['wc', '2', 'ow', 'nb', '0', 'wo', 'nb', '0', 'wo']
PS += ['wc', '3', 'ow', 'wc', '7', 'ow', 'wc', '5', 'ow']
PS += ABS(309, 'sc') + ABS(307, 'sc')
# честный терминатор программы (канон scan7): без 'te' VM уходит в мусор
# после конца кода — KERNEL PANIC "недокументированный опкод 0xFF", rc=1.
PS += ['te']

PROGRAM = INIT + ['mk'] + LB + PS

MAX_USER_WORDS = 2046
flat = ' '.join(PROGRAM)
TOKENS = len(flat.split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe111\pos_wc14v3ring.words'
assert TOKENS <= MAX_USER_WORDS, 'tokens %d > %d' % (TOKENS, MAX_USER_WORDS)
with open(POS_PATH, 'w', encoding='ascii', newline='') as f:
    f.write(flat + '\n')
print('pos_wc14v3ring tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
