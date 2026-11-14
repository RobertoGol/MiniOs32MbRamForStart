# -*- coding: utf-8 -*-
# Том-кольцо 24а (веха-24, спринт 92, W-112, TKT-052): generic 'nb d+ ne'
# + голые цифры. Приёмка: card112 позитивы BYTE-OK, неги = молчание.
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
#   82 POS2, 84/85 ZP2(&60,&82). SELF-консты: cell[46]:=46, [25198]:='nb',
#   [25966]:='ne' (сравнение W == cell[W]).

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

LB = []
LB += ABS(311, 'sc')                       # прочесть слово (311 = FILE_GET)
# E-блок
LB += ABS(EOFC, 'va') + ['wc', '7', 'sv']            # EFA = EOF
LB += ABS(EFASC, 'sv')                               # EFAsc = EOF
LB += ['wc', '7', 'va', 'eq', '0'] + ABS(NOEFA, 'sv')  # NOEA = (E==0)
# флаги слова
LB += ABS(WORDC, 'va') + ABS(NBW, 'cp') + ABS(NBFA, 'sv')    # is_nb
LB += ABS(WORDC, 'va') + ABS(NEW_, 'cp') + ABS(NEFA, 'sv')   # is_ne
LB += ABS(WORDC, 'va') + ABS(DOTW, 'cp') + ABS(DTFA, 'sv')   # is_dot
LB += ABS(WORDC, 'va') + ['su', '8'] * 6 + ABS(VSC, 'sv')    # V = W-48
LB += ABS(VSC, 'va') + ['gt', '9', 'eq', '0'] + ABS(DGFA, 'sv')  # is_dig
# bareK = (is_dig + (S==0)) == 2
LB += ['wc', '6', 'va', 'eq', '0'] + ABS(S0FA, 'sv')
LB += ABS(DGFA, 'va') + ABS(S0FA, 'aa') + ['eq', '2'] + ABS(BKFA, 'sv')
# neK = (S + is_ne)==2 (честно: acc-арифметика, БЕЗ мутации S — урок: bare 'as'
# не возвращает сумму в acc, acc не меняется)
LB += ['wc', '6', 'va'] + ABS(NEFA, 'aa') + ['eq', '2'] + ABS(NKFA, 'sv')
# f = (S_now==1) И (is_ne==0)
LB += ['wc', '6', 'va', 'eq', '1'] + ABS(FSA, 'sv')
LB += ABS(NEFA, 'va') + ['eq', '0'] + ABS(FSA, 'aa') + ['eq', '2'] + ABS(FSA, 'sv')
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
# EMIT-кольцо: while VCNT != 0: U8 0x15; BE32(cell[FB]); FB++; VCNT--
PS += ['mk']
PS += ['wc', '9', 'va', 'if']              # if#3: VCNT==0 -> TAIL
PS += ['wc', '8', 'gp', 'wc', '0', 'sv']   # NumAcc := cell[FB] (bare 'gp' после
                                           # 'wc 9 va if' читал бы cell[cell[9]])
PS += ['nb', '2', '1', 'em', 'nb', '3', '0', '8', 'sc']
PS += ['wc', '0', 'ow']
PS += ['wc', '8', 'va', 'ad', '1', 'sv']   # FB += 1
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

MAX_USER_WORDS = 1022
flat = ' '.join(PROGRAM)
TOKENS = len(flat.split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe111\pos_wc14v3ring.words'
assert TOKENS <= MAX_USER_WORDS, 'tokens %d > %d' % (TOKENS, MAX_USER_WORDS)
with open(POS_PATH, 'w', encoding='ascii', newline='') as f:
    f.write(flat + '\n')
print('pos_wc14v3ring tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
