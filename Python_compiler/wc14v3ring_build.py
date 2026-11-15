# -*- coding: utf-8 -*-
# Том-кольцо 24а+24б+24б-3+24в-1+24в-2 (веха-24, спринты 92-98,
# W-112..W-119, TKT-052): generic 'nb d+ ne' + голые цифры (24а) + A-виды
# nb-пары sv/sc (24б-1) + gp/sp (24б-2) + B-виды va/cp/aa (24б-3, спринт 96:
# граница тома поднята W-116 0x400->0x800 по бюджет-приговору W-115) +
# T3-формы 'wc d va|sv|gp|sp' и голые va/sv/gp/sp (24в-1, спринт 97: S-машина
# 0/1/2, SLC = модель W_Current, единая bare-kind запись) + eq/as/vw
# (24в-2, спринт 98: eq = 8·(is_eq+EQPA_old) — тег цифры; as = 2 рекорда
# [aa][sv] через pre-write; vw = 4Б-канал через is_b2=0; k2K-член для
# слот-форм без цифры 'wc as|vw' — probe121c). Приёмка: card112/card113/
# card97 позитивы BYTE-OK, неги = молчание; 'wc 5 eq'/'eq' = tracked-DIV
# (stage1-квирк rep Error=1/FCODE=6, probe121c дамп).
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
#   слоты: 'wc d va|sv|as|sp|gp|ow' (bare 'va/sv/sp/gp' = W_Current);
#   24в-2: bare 'eq <digit>' / 'wc d eq <digit>' (сравнение acc == цифра),
#   bare 'as' / 'wc d as' / 'wc as' (слот-аккумулятор, 2 рекорда),
#   bare 'vw' / 'wc vw' (4Б-канал BE32(W_Current)).
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
# 24в-1: WCW 25463='wc', WCFA 98, S2DIG 99, SLC 100 (init F00FF1), HSL 83,
#   K4FA 113 (= k4K: bare/slot-запись вида [X=SLC][tag]).
# 24в-2 (спринт 98): TAGTAB переезжает 90 -> 115 (10 входов k=0..9:
#   [8]=0x1216 eq — VM mode 0x16 «равно?» ctos_vm.py:399; [9]=0x00F0 vw —
#   U16-канал, is_b2=0 = VM-дефолт cell[240]); EQWC/ASWC/VWWC 129..131
#   (word-коды 'eq'=0x7165, 'as'=0x7361, 'vw'=0x7776 — KW-defines
#   stage1:63/168/169); EQFA/ASFA/VWFA 132..134 (флаги — ВНЕ TAGTAB, урок
#   W-114); EQPA 135 (pending-eq: eq ждёт СВОЮ цифру), PDGFA 136
#   (pending-цифра = EQPA_old+dig==2), EQKFA 137 (eqK-член легальности);
#   is_b2-семафоры НА АДРЕСАХ-ТЕГАХ: A-теги (5376/21760/4864/20992/21248)
#   := 1, B-теги (4633/4632/4629) := 2, eq-тег cell[4630] := 2, vw cell[240]
#   := 0 — эмита T = POSC + is_b2 (без '+1'), байт-идентично старому A/B.
#   as = 7 (общий вес/тег с aa: 0x1215), eq = 8, vw = 9; KINDA авто (k>0).

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
TAGTAB, K2FA, KINDA = 115, 101, 102          # 24в-2: TAGTAB переезд 90 -> 115 (10 входов k=0..9)
STREAM, POSC = 15732720, 114                # 0x00F00FF0 (ячейка-аргумент syscall); POSC = машина позиций
# 24в-1 (спринт 97): S-машина 0/1/2 + модель W_Current
WCW = 25463                                 # 'wc' = 0x6377 ('c'<<8|'w' — первый символ в МЛАДШЕМ байте)
WCFA, S2DIG, SLC, HSL, K4FA = 98, 99, 100, 83, 113  # is_wc; (S==2 и цифра); слот (init F00FF1); F3A+V; k4-запись
WC_BASE = 15732723                          # 0x00F00FF3 = F3A (WC_BASE + d, d=0..9 -> F3..FC)
# 24в-2 (спринт 98): eq/as/vw — word-коды (stage1 defines: KW_EQ 0x7165,
#   KW_AS 0x7361, KW_VW 0x7776), ячейки word-кодов, флаги, состояния
EQW, ASW, VWW = 29029, 29537, 30582
EQWC, ASWC, VWWC = 129, 130, 131            # ячейки word-кодов
EQFA, ASFA, VWFA = 132, 133, 134            # флаги (вне TAGTAB 115..124 — урок W-114)
EQPA, PDGFA, EQKFA = 135, 136, 137          # pending-eq; pending-цифра; eqK-член легальности

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
INIT += N(4630) + ABS(TAGTAB + 8, 'sv')     # [8] 0x1216 (eq, k=8; OP_LOAD mode 0x16 «равно?» ctos_vm.py:399)
INIT += N(240) + ABS(TAGTAB + 9, 'sv')      # [9] 0x00F0 (vw, k=9; U16-канал; is_b2=cell[240]=0 VM-дефолт)
INIT += N(GPW) + ABS(GPWC, 'sv')           # cell[103] := 28775
INIT += N(SPW) + ABS(SPWC, 'sv')           # cell[104] := 28787
# 24б-3: word-коды B-видов + is_b-семафоры + POSC-машина
INIT += N(VAW) + ABS(VAWC, 'sv')           # cell[107] := 24950
INIT += N(CPW) + ABS(CPWC, 'sv')           # cell[108] := 25456
INIT += N(AAW) + ABS(AAWC, 'sv')           # cell[109] := 24929
# 24в-2: is_b2-семафоры на АДРЕСАХ-ТЕГАХ (эмита T = POSC + is_b2, без '+1'):
#   A-теги := 1 (SEEK на P+1 -> PUT затирает болван U16 -> [TT][b0..b3] 5Б),
#   B-теги := 2 (SEEK на P+2 = no-op -> [0x12][канал][b0..b3] 6Б);
#   eq-тег := 2 (B-вид), vw-тег cell[240] := 0 = VM-дефолт (U16 затирается
#   PUT целиком -> BE32(W_Current) ровно 4Б — probe121/07, /00 'wc vw').
INIT += N(1) + ABS(5376, 'sv')             # cell[0x1500] := 1 (is_b2: ne/dig A)
INIT += N(1) + ABS(21760, 'sv')            # cell[0x5500] := 1 (is_b2: sv A)
INIT += N(1) + ABS(4864, 'sv')             # cell[0x1300] := 1 (is_b2: sc A)
INIT += N(1) + ABS(20992, 'sv')            # cell[0x5200] := 1 (is_b2: gp A)
INIT += N(1) + ABS(21248, 'sv')            # cell[0x5300] := 1 (is_b2: sp A)
INIT += N(2) + ABS(4633, 'sv')             # cell[0x1219] := 2 (is_b2: va B)
INIT += N(2) + ABS(4632, 'sv')             # cell[0x1218] := 2 (is_b2: cp B)
INIT += N(2) + ABS(4629, 'sv')             # cell[0x1215] := 2 (is_b2: aa/as B)
INIT += N(2) + ABS(4630, 'sv')             # cell[0x1216] := 2 (is_b2: eq B)
INIT += N(20) + ABS(POSC, 'sv')            # POSC := 20 (16 шапки + 4 CRC; байт-дифф a318d454)
# 24в-1: SLC := 0xF00FF1 (WORK_CELL — честный дефолт W_Current stage1;
#   зонд b_va: голая 'va' на свежем stage1 = [12 19 00F00FF1] 2e1d1bb3)
INIT += N(15732721) + ABS(SLC, 'sv')
# 24в-1: self-конста 'wc' — сравнение 'cp' компилится в OP_LOAD[0x18]
#   (acc == cell[arg]) и ЖИВЁТ только при cell[W] := W (поймано трассой
#   t_bad: OP_LOAD[0x18] на 0x6377 vs cell[25463]=0 -> WCFA := 0 -> WCK=0
#   -> S'=0 -> notbad=0 -> BSFA=1 -> кольцо молчало на ВСЕХ 'wc'-кейсах)
INIT += N(WCW) + ABS(WCW, 'sv')             # cell[25463] := 25463
# 24в-2: word-коды eq/as/vw (сравнение 'cp' = OP_LOAD[0x18], как 'wc' в 24в-1)
INIT += N(EQW) + ABS(EQWC, 'sv')           # cell[129] := 29029 ('eq')
INIT += N(ASW) + ABS(ASWC, 'sv')           # cell[130] := 29537 ('as')
INIT += N(VWW) + ABS(VWWC, 'sv')           # cell[131] := 30582 ('vw')

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
# 24в-1: is_wc ('wc' = 0x6377) — открытие слота: S 0 -> 2 (WCK: 'wc' при
#   открытом nb = недопустимое слово -> badsum -> молчание, див/сил);
#   повторный 'wc' при S==2 = ЧЕСТНОЕ перевыбор (зонд n_dblwc: stage1
#   'wc 5 wc 6 va' = [12 19 F00FF9] 0xFF — pending заменяется, НЕ брак).
LB += ['wc', '8', 'gp'] + ABS(WCW, 'cp') + ABS(WCFA, 'sv')       # is_wc (24в-1)
# 24в-2: is_eq/is_as/is_vw — новые слова ('eq'=0x7165, 'as'=0x7361,
#   'vw'=0x7776; ячейки word-кодов 129/130/131)
LB += ['wc', '8', 'gp'] + ABS(EQWC, 'cp') + ABS(EQFA, 'sv')      # is_eq
LB += ['wc', '8', 'gp'] + ABS(ASWC, 'cp') + ABS(ASFA, 'sv')      # is_as
LB += ['wc', '8', 'gp'] + ABS(VWWC, 'cp') + ABS(VWFA, 'sv')      # is_vw
LB += ['wc', '8', 'gp'] + ['su', '8'] * 6 + ABS(VSC, 'sv')   # V = W-48 (gp через FB)
LB += ABS(VSC, 'va') + ['gt', '9', 'eq', '0'] + ABS(DGFA, 'sv')  # is_dig
# 24в-2: PDG = pending-цифра = (EQPA_old + is_dig)==2 — цифра-операнд eq.
#   eq ставит pending (EQPA'=1), цифра его закрывает И ДАЁТ eq-запись
#   ([12 16][BE32(цифра)], X = V — probe121/10 'eq 3', /04 'wc 5 eq 3':
#   X = ЦИФРА, НЕ SLC — потому pending-цифра идёт через bareK, не k4K).
LB += ABS(EQPA, 'va') + ABS(DGFA, 'aa') + ['eq', '2'] + ABS(PDGFA, 'sv')
# взвешенный k = sv + 2sc + 3gp + 4sp + 5va + 6cp + 7(aa|as) + 8·(is_eq +
#   EQPA_old) + 9vw — 24в-2 ml-форма (va + ml w + aa в K2FA): aa-форма не
#   умеет 8·(is_eq+EQPA_old), ml дешевле 10-членной суммы; одна eq-строка
#   даёт И вес eq-слова, И тег цифры-операнда (EQPA_old=1 -> 8). БЕЗ ne —
#   ne/цифры дают k=0 → TAGTAB[0] = 0x15. KINDA = is_ne + (k>0): eq/as/vw —
#   авто-kinds. ЧЕСТНЫЕ УРОКИ: (1) 'as' с открытым nb = брак 0x0C; (2)
#   'aa'/'cp' честны только с nb-открытой ЯЧЕЙКОЙ; is_kind живёт в KINDA.
#   ml-кольцо (веха-12б) жжёт TMP_CNT = СЛОТ S — стеш S -> KA вокруг всего
#   весового блока (KA свободен до 174; FB жжётся, но V уже взят, а FB
#   честно перезаписывается в тег-блоке; FCODE ставится в PS).
LB += ['wc', '6', 'va'] + ABS(KA, 'sv')                 # стеш: KA := S
LB += ABS(SVFA, 'va') + ABS(K2FA, 'sv')                 # k := sv (w=1; sv-СТАРТ суммы в K2FA)
LB += ABS(SCFA, 'va') + ['ml', '2'] + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')   # + 2·sc
LB += ABS(GPFA, 'va') + ['ml', '3'] + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')   # + 3·gp
LB += ABS(SPFA, 'va') + ['ml', '4'] + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')   # + 4·sp
LB += ABS(VAFA, 'va') + ['ml', '5'] + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')   # + 5·va
LB += ABS(CPFA, 'va') + ['ml', '6'] + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')   # + 6·cp
LB += ABS(AAFA, 'va') + ['ml', '7'] + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')   # + 7·aa
LB += ABS(ASFA, 'va') + ['ml', '7'] + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')   # + 7·as (тег общий с aa: 0x1215)
# + 8·PDG — 24в-2 УРОК run-4: старая форма 8·(EQFA+EQPA) добавляла 8 КАЖДЫЙ
#   токен открытого pending ('eq va 3': у 'va' K2FA = 5+8 = 13 -> тег =
#   TAGTAB[13] = мусор -> is_b2 = 0 -> va-рекорд 4Б-вид вместо B-вида 0x1219;
#   поймано смоком). Вес eq нужен ТОЛЬКО на рекорде самого eq — а он стреляет
#   на цифре, закрывающей pending: PDGFA (строка выше) = (EQPA_old+dig)==2 —
#   точная пара. На eq-токене рекорда нет (K=0) — 8·EQFA был мёртвым грузом.
LB += ABS(PDGFA, 'va') + ['ml', '8'] + ABS(K2FA, 'aa') \
    + ABS(K2FA, 'sv')                                   # + 8·PDG (закрытие pending)
LB += ABS(VWFA, 'va') + ['ml', '9'] + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')   # + 9·vw
LB += ABS(KA, 'va') + ['wc', '6', 'sv']                 # стеш: S <- KA
# is_kind = (K2FA + EQFA > 0) + ne — УРОК run-6: с весом eq = 8·PDG у САМОГО
#   eq-токена K2FA = 0 (PDG=0, digit-нет) -> KINDA терял is_kind -> дыра
#   neK-исключения: (S=1, KINDA=0, is_eq=1) давало ровно 3 -> NKFA=1 ->
#   notbad=1 -> BSFA=0 -> stay -> 'nb 3 eq' ДОХОДИЛ до точки и ПЕЧАТАЛ
#   (поймано трассой tr_nb3eq: BSFA-добавки 0,0,1,0,0). eq+K2FA>0 восстанав-
#   ливает is_kind у eq (у as/vw он жив через их k-веса). Побочных эффектов
#   нет: f=(S+2·K)==1 и neK меняются только при S=1 (все такие кейсы = неги).
LB += ABS(K2FA, 'va') + ABS(EQFA, 'aa') + ['gt', '0'] + ABS(NEFA, 'aa') \
    + ABS(KINDA, 'sv')                  # is_kind = (k|eq)>0 + ne
# bareK = (is_dig + (S==0)) == 2
LB += ['wc', '6', 'va', 'eq', '0'] + ABS(S0FA, 'sv')
LB += ABS(DGFA, 'va') + ABS(S0FA, 'aa') + ['eq', '2'] + ABS(BKFA, 'sv')
# 24в-2: BKFA |= PDG — pending-цифра легальна при любом S: при S=0 её даёт
#   и так bareK ((dig+S0)==2), при S=2 только PDG ('wc 5 eq 3' = probe121/04,
#   X = V = цифра). OR-форма (BKFA+PDG)>0: K обязан остаться 1 (K'=(K==1)).
LB += ABS(BKFA, 'va') + ABS(PDGFA, 'aa') + ['gt', '0'] + ABS(BKFA, 'sv')
# 24в-2: k2K = (S + is_as + is_vw)==3 — слот-формы БЕЗ цифры ('wc as' =
#   probe121/19, 'wc vw' = probe121c/00): stage1 эмитит с X = SLC (текущая
#   модель W_Current; у 'wc as' это дефолт F00FF1). ЧЕСТНЫЙ УРОК смоука:
#   форма ==2 выстреливала при S=1+as ('nb 3 as' шёл через k2K-путь вместо
#   молчания) — ==3 уникально: S=2 И ровно один флаг (S=1+as = 2, S=0+as = 1).
#   eq при S=2 без цифры НЕ сюда ('wc 5 eq' = квирк stage1: пустое тело,
#   rep Error=1/FCODE=6 — probe121c/09 дамп; у кольца пустой 0xFF-артефакт
#   — tracked-DIV). PDGFA уже свободна (PDG поглощён bareK) — под k2K.
LB += ['wc', '6', 'va'] + ABS(ASFA, 'aa') + ABS(VWFA, 'aa') + ['eq', '3'] \
    + ABS(PDGFA, 'sv')
# 24в-1: S2DIG = (S==2)&&(is_dig) — слот-выбор цифрой; S_old + 3*dig == 5
#   уникально (S=2,dig=1; прочие комбинации 0..4 и 6..11 — не 5)
LB += ['wc', '6', 'va'] + ABS(DGFA, 'aa') * 3 + ['eq', '5'] + ABS(S2DIG, 'sv')
# 24в-1: WCK = is_wc И (S!=1) — 'wc' при открытом nb недопустим (stage1
#   потребляет nb-'wc'-форму вехи-10 — НЕ поддержана кольцом, див/сил);
#   повторный 'wc' при S==2 = честный перевыбор (зонд n_dblwc). S1 через
#   KA-стеш: (WCFA + 2*S1)==1 ⟺ wc-легален.
LB += ['wc', '6', 'va', 'eq', '1'] + ABS(KA, 'sv')                  # KA := S1
LB += ABS(KA, 'va') + ABS(KA, 'aa') + ABS(WCFA, 'aa') + ['eq', '1'] + ABS(KA, 'sv')  # KA := WCK
# 24в-2: RF := [(RF+WCK)>0] · ¬S2DIG — хвост-квирк stage1 'wc'-без-цифры:
#   rep Error=1/FCODE=8 ПОСЛЕ печати ('wc as' = probe121/19, 'wc vw' =
#   probe121c/00 — тела совпали, расходился хвост; поймано смоком run-4).
#   RF-слот ('wc 3') = аккумулятор wcd: OR-накоп WCK (gt-клэмп — 'wc wc'
#   re-select не раздувает), стирание по S2DIG (цифра закрыла слот). opennb
#   (PS) добавляется поверх — с wcd взаимоисключающ (S==1 после wc-open = BAD
#   -> молчание, хвоста нет). Читается KA (=WCK) прямо здесь — до KA:=K'.
#   ЧЕСТНЫЙ УРОК run-5: форма [(RF+WCK)>0 + S2DIG]==0 ИНВЕРТИРОВАЛА аккумулятор
#   (RF:=1 когда «ничего не было»: X=0, S2DIG=0 — ложный RF=1 на 'eq 3'/'nb 3 eq'
#   без единого 'wc'; на самом 'wc' X=1 -> RF:=0, md5 'wc as' не менялся с
#   run-4 = 10/20 регрессия). Конъюнкция X·¬S2DIG честно: gt0 -> eq0 (НЕ X) ->
#   +S2DIG -> eq0 -> НЕ(НЕ X + S2DIG) = X·¬S2DIG.
LB += ['wc', '3', 'va'] + ABS(KA, 'aa') + ['gt', '0'] + ['eq', '0'] \
    + ABS(S2DIG, 'aa') + ['eq', '0'] + ['wc', '3', 'sv']
# 24в-2: eqK-член легальности eq — КОНЪЮНККЦИЯ, ПОСЛЕ KA:=WCK (урок run-2:
#   блок между KA:=S1 и KA:=WCK перезаписывал KA -> WCK=(2*T+WCFA)==1 давал
#   0 у 'wc' при S=0 -> слот не открывался -> BAD -> слот-формы молчали;
#   поймано трассой tr_vwvw). T = ((S==1)+EQPA_old)==0. ЧЕСТНЫЙ УРОК run-3:
#   промежуточное 'eq 0' после 'eq 1' давало (S!=1), и финальное 'eq 0' по
#   сумме (S!=1)+EQPA ИНВЕРТИРОВАЛО конъюнкцию -> T=(S==1)&(EQPA==0) -> все
#   eq-кейсы BAD-молчали, а 'nb 3 eq' печатал (поймано смоком run-3: 7
#   ok-молчат + sil печатает). Форма без промежуточной инверсии: 'eq 1'
#   держит (S==1), 'aa' добавляет EQPA, 'eq 0' тестирует сумму. is_eq идёт
#   через 'aa' (не 'va' — acc уже держит T). eqK = (is_eq+T)==2. Покрытие:
#   bare-eq S=0 T=1 легален ('eq 3'); eq при S=2 T=1 легален
#   ('wc 5 eq 3' = probe121/04; 'wc 5 eq' -> пустой артефакт = ddiv);
#   eq-double EQPA_old=1 -> T=0 BAD ('eq eq 3' = 0xFE probe121b/05);
#   eq при S=1 -> T=0 BAD ('nb 3 eq' = 0xFE probe121/18).
LB += ['wc', '6', 'va', 'eq', '1'] + ABS(EQPA, 'aa') \
    + ['eq', '0']                                                   # T = ((S==1)+EQPA)==0
LB += ABS(EQFA, 'aa') + ['eq', '2'] + ABS(EQKFA, 'sv')               # eqK = is_eq & T
# 24в-2: EQPA' = ((is_eq + 2·EQPA_old + 3·dig) − 1) < 2 — pending-eq:
#   is_eq ставит pending (1), EQPA_old держит (2); eq-double (3), цифра (4),
#   pending+цифра (5) гасят; su — БЕЗЗНАКОВОЕ (0-1 = 0xFFFF -> lt2 = 0).
#   ПОСЛЕ KA:=WCK: EQPA_old уже прочитан весами и eqK-членом.
LB += ABS(EQFA, 'va') + ABS(EQPA, 'aa') * 2 + ABS(DGFA, 'aa') * 3 \
    + ['su', '1'] + ['lt', '2'] + ABS(EQPA, 'sv')
# f = (S==1) И NOTKIND ⟺ S + 2*KINDA == 1 (уникально S=1,K=0; урок: старая
#   форма (S+K)==1 рвалась на S=0,K=1 — голая va открывала S'=1 и ломала
#   персистентность 'wc 5 va va')
LB += ['wc', '6', 'va'] + ABS(KINDA, 'aa') * 2 + ['eq', '1'] + ABS(FSA, 'sv')
# neK = (S + 2*KINDA + 2*(is_eq+is_as+is_vw))==3 — 24в-2 ИСКЛЮЧЕНИЕ: новые
#   виды НЕ закрывают nb ('nb 3 as/eq/vw' = 0xFE probe121/17-/18 — stage1
#   бракует накопление в слот и eq-pending при открытом nb); старые A-виды
#   НЕ исключены ('nb 12 va' = див probe121/13 — stage1 читает ячейку,
#   сохраняем regr117-поведение). S=2 + KINDA = 4 — wc-состояние не даёт 3.
LB += ['wc', '6', 'va'] + ABS(KINDA, 'aa') * 2 + ABS(EQFA, 'aa') * 2 \
    + ABS(ASFA, 'aa') * 2 + ABS(VWFA, 'aa') * 2 + ['eq', '3'] + ABS(NKFA, 'sv')
# 24в-1: обновление SLC — модели W_Current: слот-цифра SLC := WC_BASE + V;
#   прочие слова SLC не трогают (персистентность 'wc 5 va va', дефолт F00FF1).
#   HSL := WC_BASE + V (держатель кандидата); sel_val по паре [61,100] через
#   перезапись cell[77]=100 / cell[78]=83, флаг = S2DIG.
LB += N(WC_BASE) + ABS(VSC, 'aa') + ABS(HSL, 'sv')                  # HSL := WC_BASE + V
LB += N(SLC) + ABS(77, 'sv') + N(HSL) + ABS(78, 'sv')               # пара := [100, 83]
LB += sel_val(77, S2DIG)                                            # acc = S2DIG ? HSL : SLC
LB += ABS(SLC, 'sv')                                                # SLC := выбор
LB += N(VSC) + ABS(77, 'sv') + N(F3A) + ABS(78, 'sv')               # пара := [61, F3A] (restore)
# 24в-1: WCE = (S==2)&&(конец источника) — хвостовой fail 'wc'-без-цифры:
#   stage1 даёт вердец 0xFF с rep Error=1/FCODE=8 (квирк хвост-проверки ПОСЛЕ
#   печати артефакта); кольцо честнее = молчание (див, tracked). Конец
#   источника в потоке = ТОЧКА (0x2E, is_dot) — EOFC не успевает встать
#   (dot-leave раньше; поймано трассой t_wc: 2-й FILE_GET = 0x2E, EFASC=0).
#   WCE читает S ДО S'-строки той же итерации (S_pre=2 жив у 'wc').
LB += ['wc', '6', 'va'] + ABS(DTFA, 'aa') * 3 + ['eq', '5'] + ABS(HSL, 'sv')
# 24в-1: S' = is_nb + f + 2*WCK (БЕЗ clamp: значение 2 легально = wc-открытие;
#   вложенное nb даёт 1+1=2 = wc-состояние, но word уже badsum -> уход)
LB += ABS(NBFA, 'va') + ABS(FSA, 'aa') + ABS(KA, 'aa') * 2 + ['wc', '6', 'sv']
# 24в-1: k4K = is_k4 И (S==0) — ЕДИНАЯ bare-kind запись: голые va/sv/gp/sp
#   (S==0) и слот-формы 'wc d op' (цифра закрыла S -> тоже S==0) пишут запись
#   [X=SLC][tag]; is_k4 = sv+gp+sp+va (sc/cp/aa слот-форм НЕ имеют — зонды
#   n_sc5/n_cp5/n_aa5 = 0xFE; голые sc/cp/aa = брак 0x0C — див/сил)
LB += ABS(SVFA, 'va') + ABS(GPFA, 'aa') + ABS(SPFA, 'aa') + ABS(VAFA, 'aa') \
    + ABS(ASFA, 'aa') + ABS(VWFA, 'aa') + ABS(S0FA, 'aa') + ['eq', '2'] \
    + ABS(K4FA, 'sv')
# 24в-2: K4FA |= k2K — слот-формы as/vw без цифры. OR безопасен: k4K требует
#   S0==1, k2K — S==2, взаимно исключающи (сумма 0/1). Дальше K4FA един:
#   K-строка, storeval level-1 (K4FA ? SLC : V), notbad-член.
LB += ABS(K4FA, 'va') + ABS(PDGFA, 'aa') + ABS(K4FA, 'sv')
# K = neK + bareK + k4K; K' = ((K==1) + notEOF) == 2
LB += ABS(NKFA, 'va') + ABS(BKFA, 'aa') + ABS(K4FA, 'aa')
LB += ['eq', '1'] + ABS(NOEFA, 'aa') + ['eq', '2'] + ABS(KA, 'sv')
# storeval = neK ? NumAcc : (k4K ? SLC : V) — 3-way: level-1 по паре [61,100]
#   (candA=V, candB=SLC) с перезаписью cell[78]=100, результат в VSC
#   (безопасно: цифры имеют k4K=0 -> VSC=V, их A-калькуляция не задета;
#   kinds дают NumAcc'=0, A не читается), level-2 = прежний sel_val(ZVA, NKFA).
LB += N(SLC) + ABS(78, 'sv')                                        # cell[78] := 100
LB += sel_val(77, K4FA)                                             # acc = k4K ? SLC : V
LB += ABS(VSC, 'sv')                                                # VSC := level-1
LB += N(F3A) + ABS(78, 'sv')                                        # cell[78] := F3A (restore)
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
# 24в-2: as = ДВА рекорда — rec2 pre-write [SLC][0x5500] по адресу PTR (после
#   += K' это ячейка СРАЗУ ЗА rec1): 'as' = OP_LOAD mode 0x15 (acc +=
#   cell[W]) + OP_STORE_AT 0x55 (cell[W] := acc) — probe121/06 'as' =
#   12 15 [BE32(WC)] 55 [BE32(WC)] 11Б; probe121c/01 'wc 7 as' = [..F8->FA].
#   БЕЗ ветвления (потолок if/es исчерпан): пишется на КАЖДОМ слове в
#   [PTR][PTR+1] — для не-as слов это мусор ЗА последним рекордом, который
#   следующий рекорд-слово честно затирает своими [X][tag]; на последнем
#   слове мусор за VCNT·2 ячейками не читается (FB идёт по парам). FB
#   переиспользуем как курсор (жжётся — перезаписывается в POS-stamp).
LB += ['wc', '1', 'va'] + ['wc', '8', 'sv']          # FB := PTR
LB += ABS(SLC, 'va') + ['wc', '8', 'sp']            # cell[PTR] := SLC
LB += ['wc', '8', 'va'] + ['ad', '1'] + ['wc', '8', 'sv']  # FB += 1
LB += N(21760) + ['wc', '8', 'sp']                  # cell[PTR+1] := 0x5500
# сдвиги as — ВНУТРИ стеша ml ниже (VCNT += ASFA; PTR += 2·ASFA)
# S-стеш вокруг 'ml': ml (веха-12б) честно компилируется в runtime-кольцо
#   умножения со скретчем TMP_X=0xF00FFB(FB), TMP_CNT=0xF00FF9(СЛОТ S!),
#   TMP_ACC=0xF00FFA — БЕЗ стеша S обнуляется каждым ml и машина состояний
#   nb-прогона умирает ('ne' становился bad-словом, честно поймано трассой).
#   KA свободен: K' уже поглощён (PTR/VCNT += K' выше).
LB += ['wc', '6', 'va'] + ABS(KA, 'sv')             # стеш S -> KA
# 24в-2: сдвиги as (2-й рекорд): VCNT += ASFA; PTR += 2·ASFA.
#   ЧЕСТНЫЙ УРОК смоука: 'as' (line выше) оставляет acc = VCNT+ASFA — ml 2
#   умножал ЭТО (PTR += 2·VCNT, квадратно-второй рекорд мимо, emit читал
#   застарелую pre-write пару [55][F1]). Перед ml АККУРАТНО перезагружаем
#   ASFA (va перезаписывает acc); ml 2 внутри стеша (TMP_CNT = слот S).
LB += ABS(ASFA, 'va') + ['wc', '9', 'as']           # VCNT += ASFA
LB += ABS(ASFA, 'va') + ['ml', '2'] + ['wc', '1', 'as']   # PTR += 2·ASFA
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
# notbad (24в-1): член = (NBFA + S')==2 — покрывает nb-легальность (1,1)
#   И wc-легальность (0,2) одним равенством: вложенное nb (1,2)->3 нет,
#   'wc' при открытом nb (0,1)->1 нет, голые kinds/нези (0,0)->0 нет —
#   их легальность дают свои члены (k4K/dig); + dot + dig + neK + k4K.
#   (24в-2 УРОК run-7: 'wc 6 aa' = БРАК — stage1 fail-fast на голом 'aa' после
#   'wc d' (голые sc/cp/aa = 0x0C), кольцо = brk-стаб 3290Б, rc=1 везде. Честная
#   форма: S грузится 'wc 6 va' (3 ток), NBFA — ABS-форма; сумма та же.)
LB += ['wc', '6', 'va'] + ABS(NBFA, 'aa') + ['eq', '2'] + ABS(DTFA, 'aa') \
    + ABS(DGFA, 'aa') + ABS(NKFA, 'aa') + ABS(K4FA, 'aa') + ABS(EQKFA, 'aa')
LB += ['eq', '0'] + ABS(BSFA, 'sv')
# L = (badsum + E + dot) > 0; stay = (L==0)
LB += ABS(BSFA, 'va') + ABS(EFASC, 'aa') + ABS(DTFA, 'aa') + ['gt', '0']
LB += ['eq', '0', 'if']                    # if#1: stay
LB += ['wc', '2', 'as']                    # CNT += stay (then-путь)
LB += ['jb', 'es']

PS = []
# opennb = ((S==1) + E + dot)==2 — БЕЗ S0FA-скретча (−10 ток): E и dot
#   взаимоисключающи (dot-leave раньше EOF, EFASC не успевает встать —
#   трасса t_wc), поэтому сумма 2 уникальна: S==1 И конец источника.
PS += ['wc', '6', 'va', 'eq', '1'] + ABS(EFASC, 'aa') + ABS(DTFA, 'aa') \
    + ['eq', '2'] + ABS(FSA, 'sv')         # opennb
# RF += opennb (wcd уже в RF из цикла; взаимоисключающи). FCODE = 8·RF + FSA:
#   (wcd=1)->8, (opennb=1)->9, чисто->0 — оба хвост-квирка stage1 одним
#   равенством (урок: прежний 9·RF давал 9 и на wc-квирке).
PS += ['wc', '3', 'as']
PS += ['wc', '3', 'va', 'ml', '8'] + ABS(FSA, 'aa') + ['wc', '7', 'sv']
# POS = opennb ? POS : 0
PS += ['wc', '5', 'va'] + ABS(POS2, 'sv')
PS += sel_val(ZP2A, FSA) + ['wc', '5', 'sv']
# Затвор (24в-1): te ⟺ (is_dot + E)==0 [bad-leave: не EOF и не точка]
#   ИЛИ WCE==1 ['wc' остался открыт на EOF — дизайн W-118: кольцо молчит,
#   stage1 печатает 45Б-квирк rep Error=1/FCODE=8 — див, tracked].
#   WCE (HSL) пишется в цикле на EOF-итерации ДО S'-строки (S_pre=2 жив).
#   silent==1 -> then='te' = ЧЕСТНОЕ молчание (rc==0, нет .out);
#   silent==0 (EOF- или dot-leave) -> es -> BEGIN (позитивы пишут артефакт).
PS += ABS(DTFA, 'va') + ABS(EFASC, 'aa') + ['eq', '0'] + ABS(HSL, 'aa') \
    + ['if']                                                   # if#2
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
# 24б-3+24в-2: единый 3-шаговый эмит (диспетчер БЕЗ ветвления, решение P4):
#   U16(TAG16) + SEEK(POSC + is_b2) + PUT(X); записи [X][TAG16] (порядок
#   скана, FB идёт по парам). is_b2 = cell[TAG16] — семафоры НА АДРЕСАХ-
#   ТЕГАХ (24в-2): A-теги := 1, B-теги := 2, eq := 2, vw := 0 (VM-дефолт).
#   A-виды: U16 = [TT][00], SEEK(P+1) -> PUT затирает болван b0 — байты
#   [TT][b0..b3] те же 5Б; B-виды: U16 = [0x12][канал], SEEK(P+2) = no-op ->
#   [0x12][канал][b0..b3] ровно 6Б; eq: [0x12][0x16][b0..b3] 6Б; vw: U16 =
#   [00][F0], SEEK(P+0) -> PUT затирает U16 ЦЕЛИКОМ -> BE32(W_Current) 4Б
#   (probe121/07 'vw', /00 'wc vw'). POSC (cell[114]) = позиция следующей
#   записи: init 20, advance T+4 = +5 (A) / +6 (B) / +4 (vw).
PS += ['wc', '8', 'gp', 'wc', '0', 'sv']   # NumAcc := cell[*FB] = X
PS += ['wc', '8', 'va', 'ad', '1', 'sv']   # FB += 1 (на TAG16)
PS += ['wc', '8', 'gp']                    # acc := TAG16
PS += ABS(STREAM, 'sv')                    # stream := TAG16
PS += ABS(306, 'sc')                       # FILE_U16 -> [b1][b2] @P
PS += ['wc', '1', 'sv']                    # PTR := TAG16 (holder для is_b2)
PS += ['gp']                               # acc := cell[TAG16] = is_b2 (0/1/2)
PS += ABS(POSC, 'aa')                      # acc := T = POSC + is_b2
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
