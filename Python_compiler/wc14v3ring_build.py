# -*- coding: utf-8 -*-
# Том-кольцо 24а+24б+24б-3+24в-1+24в-2+24в-3+24г (веха-24, спринты 92-100,
# W-112..W-121, TKT-052). 24г (спринт 100): управляющие слова if/es/mk/jb
# через site_store-патч TAIL до FILE_SEAL; 3 if + 3 es + 2 mk + 2 jb, sticky
# BADIF/BADEJ/BADJB; исходное слово 'su' (KW_SUB 0x7573) с pending-литералом
# и тегом 0x1217; forecast pr/ow = 4Б хвоста поверх 5Б базы (урок кейса 68:
# старый ml·9 сдвигал все if/es/jb-цели). 24д (спринт 101 W-122): ad/gt/lt
# через обобщённую pending-машину su/eq; MAX_SOURCE_WORDS 0x1000->0x2000
# ( MAX_USER_WORDS 8190, прецедент W-120 ); Итог: 4375 ток (лимит 8190),
# 10674 Б 0xFF md5 cc678b3e; probe125 21/25 BYTE-OK, фиксепоинт BLOCKED at ml.
# Generic 'nb d+ ne' + голые цифры (24а) + A-виды
# nb-пары sv/sc (24б-1) + gp/sp (24б-2) + B-виды va/cp/aa (24б-3, спринт 96:
# граница тома поднята W-116 0x400->0x800 по бюджет-приговору W-115) +
# T3-формы 'wc d va|sv|gp|sp' и голые va/sv/gp/sp (24в-1, спринт 97: S-машина
# 0/1/2, SLC = модель W_Current, единая bare-kind запись) + eq/as/vw
# (24в-2, спринт 98: eq = 8·(is_eq+EQPA_old) — тег цифры; as = 2 рекорда
# [aa][sv] через pre-write; vw = 4Б-канал через is_b2=0; k2K-член для
# слот-форм без цифры 'wc as|vw' — probe121c) + te/pr/ow (24в-3,
# спринт 99 W-120: KW_TERM/PR/OW self-консты через 'cp', флаги
# 140/141/142, порт 0x3F0050C0 @127, поток OW, te-аккумулятор, ad-выбор,
# NumAcc сохраняется на 'pr' через scratch 152/153; граница тома поднята
# 0x800->0x1000 / MAX_USER_WORDS 2046->4094 — 2724 ток, 6507 Б 64c0bed1).
# Приёмка: card112/card113/card97 + probe123 позитивы BYTE-OK, неги =
# молчание; 'wc 5 eq'/'eq' = tracked-DIV (stage1-квирк rep Error=1/FCODE=6,
# probe121c дамп); 'as te'/'nb 7 pr ne' байт-дифы W-120 починены точечно.
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
TAGTAB, K2FA, KINDA = 160, 101, 102          # 24г: TAGTAB переезд 115 -> 160 (15 входов k=0..14)
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
# 24в-3 (спринт 99): te/pr/ow — word-коды (KW_TERM 0x6574, KW_PR 0x7270,
#   KW_OW 0x776F), self-консты (сравнение 'cp' = OP_LOAD[0x18]), флаги,
#   порт-конста, STREAM-конста, te-аккумулятор, adр-выбор, adскрипт-вес
TEW, PRW, OWW = 25972, 29296, 30575
TEFA, PRFA, OWFA = 140, 141, 142            # флаги (вне TAGTAB 115..126 — урок W-114)
PRTA, XPA = 127, 139                        # порт 0x3F0050C0 @127 (разность 27=3·9 от 100 — ml-чистая: 78 := 100+49te+27pr+45ow, все разности = произведение 2 цифр); ХРА свободна
PGOF, K2BF = 143, 144                       # ПГОЯ = PRFA+OWFA (вес 11); K2BЯ = 1·ASFA+9·ПГОЯ (таг-2 скрипта)
STRA, KHAD = 145, 146                       # СТРЯ = 0x00F00FF0 (конста-ячейка STREAM @145); ХАД-146 = скретч-адрес-выбор (пересчёт 3×: 147+2te+ow / ХАДРЯ / 148+as+ПГОЯ)
SCRE, SCR1, SCR2 = 149, 147, 148            # СКРЕ-149 = цепь X_te (последнее записанное значение пары); 147/148 — мусор-приёмники
SLOT2 = 128                                 # te/ow слот-запись: (S + TEFA + OWFA)==3 ('wc te|ow' эмитит, при открытом nb S=1 → 2 → брак)
# 24г (спринт 100 W-121): if/es/mk/jb — word-коды (KW_IF 0x6669, KW_ELSE 0x7365,
#   KW_MK 0x6B6D, KW_JB 0x626A), self-консты, флаги, ячейки сайтов/целей.
IFW, ESW, MKW, JBW = 26217, 29541, 27501, 25194
IFWC, ESWC, MKWC, JBWC = 176, 177, 178, 179   # ячейки word-кодов (вне TAGTAB 160..174)
IFFA, ESFA, MKFA, JBFA = 180, 181, 182, 183   # флаги (вне TAGTAB — урок W-114)
# 24г Stage2: ВСЕ адреса cstore содержат только НЕНУЛЕВЫЕ цифры (ml-цепочка
# flag*addr обнуляется на цифре 0); свалка = cell[0] (возвращается в 0 в конце).
SITE1, SITE2, SITE3 = 401, 402, 403           # слоты if: 400+flag·1 +n-1
ESITE1, ESITE2 = 404, 405                     # слоты es: 400+flag·4 +n-1
EJ1, EJ2, EJ3 = 409, 410, 411                 # else-join: site_store base 392−1 + 18·flag +n-1
IFCNT, JSCNT = 195, 196                       # счётчики if/es
TERMP, MARKP = 154, 156                       # TERM: 100+flag·69 / MARK: 100+flag·78
CTXA, CTXB = 204, 205                         # пара селектора X: XORD / 20
XORD, CTLFL, MKLG = 206, 207, 208             # X обычный / флаг управляющего / mk-легальность
FPOS, FPOL = 211, 212                         # forecast позиции / позиция текущей записи
DEFC, DEFV = 219, 221                         # пара [CT20,TERMP] / результат DEF
TMPB, SCRV, SCRA = 125, 223, 244              # is_b2: 100+flag·55
KFA, TMPF = 245, 246                          # K' / is_b2 тега
BADIF, BADEJ, BADJB = 241, 242, 243           # отказы 4-й if / 4-й es / jb без метки
PXPA, PXPB = 231, 232                         # пара селектора: VAL / JBX
VAL, JBX, XFIN = 236, 237, 238                # X-значение / цель jb / финальный X
SK = 239                                      # стеш S вокруг ml-цепочек
C100, C400 = 249, 250                         # константы-базы для адресов
CT20 = 203                                    # конста 20 (адрес для селекторов)
IFPA, IFPB, IFPC = 224, 226, 228              # пары селекторов if-target (224/225 ...)
IFTGT = 233                                    # scratch цели if (НЕ затирает DEF для es)
# 24г W-121: 'su' (KW_SUB 0x7573) — беззнаковое вычитание литерала.
#   Переиспользуем pending-eq машину: su ставит EQFA=1 → EQPA=1; на цифре-
#   операнде SUPA_old=1 переключает TAGTAB[8] с 0x1216 на 0x1217 (is_b2=2 уже
#   проинициализирован общей N(2)-группой). SUPA держится ровно до этой цифры.
SUW, SUWC = 30067, 57                          # KW_SUB 0x7573 / ячейка self-консты
SUFL, SUPA = 58, 59                            # is_su / sticky «pending от su»
TAGEQ = 4630                                   # TAGTAB[8] по умолчанию (eq)
# 24д W-122: ad/gt/lt — такие же pending-опы (word+digit), что eq/su.
#   Тег цифры = 4628 + 2*EQOA + 3*SUPA + 6*GTUA + 7*LTOA:
#   eq 4630(0x1216), su 4631(0x1217), ad 4628(0x1214), gt 4634(0x121A), lt 4635(0x121B).
ADW, GTW, LTW = 25697, 29799, 29804
ADWC, GTWC, LTWC = 184, 185, 186
ADFL, GTFL, LTFL = 187, 188, 189
EQSG = 190                                     # is_eq «чистый» (до OR с su/ad/gt/lt)
EQOA, ADOA, GTUA, LTOA = 191, 192, 193, 194    # sticky-флаги тега
TAGV = 197                                     # scratch суммы тега
SSAV = 198                                     # стеш S вокруг ml-суммы тега

def sel_val(anchor, flag):
    """acc = flag ? cell[candB] : cell[candA]; двойной gp (ячейки держат АДРЕСА)."""
    return (N(anchor) + ['wc', '8', 'sv'] + ABS(flag, 'va')
            + ['wc', '8', 'as', 'gp', 'wc', '8', 'sv', 'gp'])

SITE_DUMP = 392                                          # flag=0 → cell[392+cnt-1] (мусор)
CSDP = 251                                               # ячейка-константа: cell[251] := 392
SITE_FACTORS = {401: ('9',), 404: ('3', '4'), 409: ('2', '9')}

def site_store(start, cnt, flag, new_tokens, adj=0):
    """cell[392 + flag*(start-391) + cell[cnt]-1+adj] := new.
    Урок: старая база 400 при flag=0 давала 400+cnt-1 — ЖИВОЙ сайт if#1,
    который затирался на каждом es-слове (два if → первый target = 20).
    409 = 392 + 18 - 1; 18 = 2*9 (ml-цепочка), лишняя −1 даёт adj=-1."""
    facs = SITE_FACTORS[start]
    ml_tokens = [tok for d in facs for tok in ('ml', d)]
    return (ABS(flag, 'va') + ml_tokens
            + ABS(CSDP, 'aa') + ['su', '1'] * (-adj)
            + ABS(cnt, 'aa') + ['su', '1', 'wc', '8', 'sv']
            + new_tokens + ['sp'])

CS_DUMP = 124                                             # безопасная свалка (cell[100] = SLC!)
CSD = 138                                                  # ячейка-константа: cell[138] := 124
CS_FACTORS = {125: ('1', '1'), 154: ('5', '6'), 156: ('4', '8')}  # (addr-CS_DUMP) = d1*d2

def cstore(addr, flag, value_tokens):
    """cell[150 + flag*(addr-150)] := value; flag=0 → свалка cell[150].
    Урок-1: 'ml d1 d2' = ml*d1 + OP_CONST(d2) — вторая цифра ЗАТИРАЕТ
    умножение; честное произведение требует 'ml d1 ml d2'.
    Урок-2: свалка 100 затирала SLC (0x00F00FF1) → байт-диф на 'pr'."""
    d1, d2 = CS_FACTORS[addr]
    return (ABS(flag, 'va') + ['ml', d1, 'ml', d2]
            + ABS(CSD, 'aa')
            + ['wc', '8', 'sv'] + value_tokens + ['sp'])

def put_abs(target_tokens):
    """FILE_SEEK(target) + FILE_PUT(cell[STREAM]-независимое значение в acc)."""
    return (target_tokens + ABS(STREAM, 'sv') + ABS(310, 'sc'))


INIT = []
# --- общие консты (экономия токенов: одна N на группу ADC-независимых записей) ---
# НОЛЬ: Z0, ZNA, ZP2A, NumAcc/CNT/RF/POS/S/VCNT, EJ/IFCNT/JSCNT/TERMP
INIT += N(0) + ABS(Z0, 'sv') + ABS(ZNA, 'sv') + ABS(ZP2A, 'sv') \
    + ['wc', '0', 'sv', 'wc', '2', 'sv', 'wc', '3', 'sv', 'wc', '5', 'sv',
       'wc', '6', 'sv', 'wc', '9', 'sv'] \
    + [t for c in (EJ1, EJ2, EJ3, IFCNT, JSCNT, TERMP) for t in ABS(c, 'sv')]
# ДВАДЦАТЬ: POSC, CT20, MARKP, FPOS
INIT += N(20) + ABS(POSC, 'sv') + ABS(CT20, 'sv') + ABS(MARKP, 'sv') + ABS(FPOS, 'sv')
# БАЗА МАССИВА: PTR и FB
INIT += N(ARR) + ['wc', '1', 'sv', 'wc', '8', 'sv']
INIT += N(NBW) + ABS(NBW, 'sv')            # cell[25198] := 25198
INIT += N(NEW_) + ABS(NEW_, 'sv')          # cell[25966] := 25966
INIT += N(DOTW) + ABS(DOTW, 'sv')          # cell[46] := 46
INIT += N(SINK) + ABS(ZPA, 'sv') + N(F8A) + ABS(ZPB, 'sv')
INIT += N(VSC) + ABS(ZVA, 'sv') + N(F3A) + ABS(ZVB, 'sv')
INIT += N(ACEL) + ABS(ZNB, 'sv')
INIT += N(POS2) + ABS(ZP2B, 'sv')
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
# общая конста 1/2 для всех is_b2-ячеек (экономия N-блоков: 21 токен)
INIT += N(1) + ABS(5376, 'sv') + ABS(21760, 'sv') + ABS(4864, 'sv') \
    + ABS(20992, 'sv') + ABS(21248, 'sv') + ABS(21504, 'sv') \
    + ABS(1536, 'sv') + ABS(1792, 'sv')  # ne/dig, sv, sc, gp, sp, pr/ow, if, es — A-виды
INIT += N(2) + ABS(4633, 'sv') + ABS(4632, 'sv') + ABS(4629, 'sv') \
    + ABS(4630, 'sv') + ABS(4631, 'sv')   # va, cp, aa/as, eq, su — B-виды
INIT += ABS(4628, 'sv') + ABS(4634, 'sv') + ABS(4635, 'sv')  # ad/gt/lt — B-виды (24д)
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
# 24в-3: word-коды te/pr/ow (self-консты — сравнение 'cp' живо при cell[W] := W)
INIT += N(TEW) + ABS(TEW, 'sv')             # cell[25972] := 25972 ('te')
INIT += N(PRW) + ABS(PRW, 'sv')             # cell[29296] := 29296 ('pr')
INIT += N(OWW) + ABS(OWW, 'sv')             # cell[30575] := 30575 ('ow')
# 24в-3: TAGTAB вырос до 12: [10] 0x0500 te, [11] 0x5400 pr/ow-пар1 (A-вид)
INIT += N(1280) + ABS(TAGTAB + 10, 'sv')    # [10] 0x0500 (te)
INIT += N(21504) + ABS(TAGTAB + 11, 'sv')   # [11] 0x5400 (pr/ow A)
# 24в-3: is_b2-семафоры новых тегов: te = −3 (T = POSC−3; PUT BE32(X_te)
#   @POSC−3..POSC переписывает последние 3Б предыдущей записи теми же
#   значениями, младший = 05; POSC := T+4 = +1); pr/ow-пар1 = A-вид
INIT += N(0) + ['su', '3'] + ABS(1280, 'sv')  # cell[0x0500] := 0−3 = 0xFFFFFFFD (−3)
# 24в-3: конст-ячейки значений пары-1 (storeval candB = cell[cell[78]],
#   cell[78] := 100+49te+27pr+45ow → {100 SLC, 149 SCRE, 127 PRTA, 145 STRA})
INIT += N(1056985280) + ABS(PRTA, 'sv')     # cell[127] := 0x3F0050C0 ('pr')
INIT += N(15732720) + ABS(STRA, 'sv')       # cell[145] := 0x00F00FF0 ('ow')
# 24г: word-коды if/es/mk/jb в ячейках сравнения + self-консты
INIT += N(IFW) + ABS(IFWC, 'sv')            # cell[176] := 26217 ('if')
INIT += N(ESW) + ABS(ESWC, 'sv')            # cell[177] := 29541 ('es')
INIT += N(MKW) + ABS(MKWC, 'sv')            # cell[178] := 27501 ('mk')
INIT += N(JBW) + ABS(JBWC, 'sv')            # cell[179] := 25194 ('jb')
# 24г: TAGTAB вырос до 14: [12] 0x0600 if, [13] 0x0700 es/jb (A-виды)
INIT += N(1536) + ABS(TAGTAB + 12, 'sv')    # [12] 0x0600 (if)
INIT += N(1792) + ABS(TAGTAB + 13, 'sv')    # [13] 0x0700 (es/jb)
# 24г Stage2: сайты патча = 16 (CRC-слот, FILE_SEAL пересчитает);
#   EJ/TERM/MARKP/счётчики/флаги = 0.
# общая конста 16 на 5 сайтов патча (экономия 4 N-блоков)
INIT += N(16) + [t for c in (SITE1, SITE2, SITE3, ESITE1, ESITE2)
                 for t in ABS(c, 'sv')]
INIT += N(SUW) + ABS(SUWC, 'sv')            # self-конста 'su' (cp = OP_LOAD 0x18 живёт при cell[SUWC]=SUW)
INIT += N(ADW) + ABS(ADWC, 'sv')            # self-конста 'ad' (24д)
INIT += N(GTW) + ABS(GTWC, 'sv')            # self-конста 'gt' (24д)
INIT += N(LTW) + ABS(LTWC, 'sv')            # self-конста 'lt' (24д)
INIT += N(100) + ABS(C100, 'sv')            # C100 := 100
INIT += N(SITE_DUMP) + ABS(CSDP, 'sv')      # CSDP := 392 (база site_store)
INIT += N(CS_DUMP) + ABS(CSD, 'sv')         # CSD := 124 (свалка cstore)
# пары селекторов (ячейки держат АДРЕСА нужных значений)
for anchor, a, b in ((CTXA, XORD, Z0), (DEFC, TERMP, CT20),
                     (IFPA, EJ1, DEFV), (IFPB, EJ2, DEFV), (IFPC, EJ3, DEFV)):
    INIT += N(a) + ABS(anchor, 'sv') + N(b) + ABS(anchor + 1, 'sv')

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
LB += ['wc', '8', 'gp'] + ABS(EQWC, 'cp') + ABS(EQFA, 'sv')     + ABS(EQSG, 'sv')                                             # is_eq + is_eq «чистый» (24д)
LB += ['wc', '8', 'gp'] + ABS(ASWC, 'cp') + ABS(ASFA, 'sv')      # is_as
LB += ['wc', '8', 'gp'] + ABS(VWWC, 'cp') + ABS(VWFA, 'sv')      # is_vw
# 24в-3: is_te/is_pr/is_ow ('te'=0x6574, 'pr'=0x7270, 'ow'=0x776F)
LB += ['wc', '8', 'gp'] + ABS(TEW, 'cp') + ABS(TEFA, 'sv')       # is_te
LB += ['wc', '8', 'gp'] + ABS(PRW, 'cp') + ABS(PRFA, 'sv')       # is_pr
LB += ['wc', '8', 'gp'] + ABS(OWW, 'cp') + ABS(OWFA, 'sv')       # is_ow
# 24г: is_if/is_es/is_mk/is_jb
LB += ['wc', '8', 'gp'] + ABS(IFWC, 'cp') + ABS(IFFA, 'sv')      # is_if
LB += ['wc', '8', 'gp'] + ABS(ESWC, 'cp') + ABS(ESFA, 'sv')      # is_es
LB += ['wc', '8', 'gp'] + ABS(MKWC, 'cp') + ABS(MKFA, 'sv')      # is_mk
LB += ['wc', '8', 'gp'] + ABS(JBWC, 'cp') + ABS(JBFA, 'sv')      # is_jb
# 24г W-121: is_su — self-конста + 'cp' (OP_LOAD 0x18); su берёт ТОЛЬКО одну
#   цифру-литерал (Num_Pending=0), поэтому вычитание 30067 здесь не работает.
LB += ['wc', '8', 'gp'] + ABS(SUWC, 'cp') + ABS(SUFL, 'sv')  # is_su
LB += ['wc', '8', 'gp'] + ABS(ADWC, 'cp') + ABS(ADFL, 'sv')  # is_ad (24д)
LB += ['wc', '8', 'gp'] + ABS(GTWC, 'cp') + ABS(GTFL, 'sv')  # is_gt (24д)
LB += ['wc', '8', 'gp'] + ABS(LTWC, 'cp') + ABS(LTFL, 'sv')  # is_lt (24д)
# eq/su/ad/gt/lt — один pending (слова взаимоисключающи)
LB += ABS(SUFL, 'va') + ABS(ADFL, 'aa') + ABS(GTFL, 'aa')     + ABS(LTFL, 'aa') + ABS(EQFA, 'aa') + ABS(EQFA, 'sv')
LB += ['wc', '8', 'gp'] + ['su', '8'] * 6 + ABS(VSC, 'sv')   # V = W-48 (gp через FB)
LB += ABS(VSC, 'va') + ['gt', '9', 'eq', '0'] + ABS(DGFA, 'sv')  # is_dig
# 24в-2: PDG = pending-цифра = (EQPA_old + is_dig)==2 — цифра-операнд eq.
#   eq ставит pending (EQPA'=1), цифра его закрывает И ДАЁТ eq-запись
#   ([12 16][BE32(цифра)], X = V — probe121/10 'eq 3', /04 'wc 5 eq 3':
#   X = ЦИФРА, НЕ SLC — потому pending-цифра идёт через bareK, не k4K).
LB += ABS(EQPA, 'va') + ABS(DGFA, 'aa') + ['eq', '2'] + ABS(PDGFA, 'sv')
# 24д W-122: тег = 4628 + 2*EQOA + 3*SUPA + 6*GTUA + 7*LTOA;
#   ml жжёт слот S — стешим S в SSAV вокруг суммы (TAGV), восстанавливаем сразу.
LB += ['wc', '6', 'va'] + ABS(SSAV, 'sv')
LB += N(4628) + ABS(TAGV, 'sv')
LB += ABS(EQOA, 'va') + ['ml', '2'] + ABS(TAGV, 'aa') + ABS(TAGV, 'sv')
LB += ABS(SUPA, 'va') + ['ml', '3'] + ABS(TAGV, 'aa') + ABS(TAGV, 'sv')
LB += ABS(GTUA, 'va') + ['ml', '6'] + ABS(TAGV, 'aa') + ABS(TAGV, 'sv')
LB += ABS(LTOA, 'va') + ['ml', '7'] + ABS(TAGV, 'aa') + ABS(TAGV, 'sv')
LB += ABS(TAGV, 'va') + ABS(TAGTAB + 8, 'sv')
LB += ABS(SSAV, 'va') + ['wc', '6', 'sv']
#   SUPA' = (2·PDG + SUPA_old + is_su)==1: цифра ЗАКРЫВАЕТ pending (в том
#   числе обычного eq — урок regr120 'eq 3 eq 4', где старая формула
#   (su+SUPA+PDG)==1 ставила su-тег на втором eq).
LB += ABS(PDGFA, 'va') + ABS(PDGFA, 'aa') + ABS(SUPA, 'aa') \
    + ABS(SUFL, 'aa') + ['eq', '1'] + ABS(SUPA, 'sv')
# 24д: sticky эка/ad/gt/lt — та же формула (2*PDG + X_old + is_X)==1
LB += ABS(PDGFA, 'va') + ABS(PDGFA, 'aa') + ABS(EQOA, 'aa') \
    + ABS(EQSG, 'aa') + ['eq', '1'] + ABS(EQOA, 'sv')
LB += ABS(PDGFA, 'va') + ABS(PDGFA, 'aa') + ABS(ADOA, 'aa') \
    + ABS(ADFL, 'aa') + ['eq', '1'] + ABS(ADOA, 'sv')
LB += ABS(PDGFA, 'va') + ABS(PDGFA, 'aa') + ABS(GTUA, 'aa') \
    + ABS(GTFL, 'aa') + ['eq', '1'] + ABS(GTUA, 'sv')
LB += ABS(PDGFA, 'va') + ABS(PDGFA, 'aa') + ABS(LTOA, 'aa') \
    + ABS(LTFL, 'aa') + ['eq', '1'] + ABS(LTOA, 'sv')
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
# 24в-3: скретч-адрес X_te-скрипта: 147 + 2·TEFA + OWFA → {147 pr/др, 148 ow,
#   149 te} — на te-слове кандидaт пишется в СКРЕ (цепь ХРА), на прочих —
#   мусор в SCR1/SCR2 (конст-ячейки 127/145 целы). KHAD-146 = temp.
LB += ABS(TEFA, 'va') + ['ml', '2'] + ABS(OWFA, 'aa') + ABS(146, 'sv')
LB += N(147) + ABS(146, 'aa') + ABS(146, 'sv')
# 24в-3: X_te = (X_prev·256+5) mod 2^32 — мл-2×8 = ×256, ад-5 = |05:
#   BE32(X_te) = [X_prev>>16][X_prev>>8][X_prev&FF][05] — верхние 3Б = те же
#   байты последней записи (не портят), младший = 05 (опкод OP_TERM)
LB += ['wc', '1', 'va'] + ['su', '2'] + ['wc', '8', 'sv'] + ['gp'] \
    + ['ml', '2'] * 8 + ['ad', '5']   # X_prev = предыдущая РЕАЛЬНАЯ запись [PTR-2] (не SCRE: mk портил цепь)
LB += ABS(148, 'sv')                                            # temp X_te (ml жжёт FB — курсор ставится ПОСЛЕ цепи)
LB += ABS(146, 'va') + ['wc', '8', 'sv']                        # FB := cell[146] = скретч-адрес
LB += ABS(148, 'va') + ['wc', '8', 'sp']                        # cell[скретч] := X_te (te→149; ow→148 идемп.; pr/др→147)
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
# 24в-3: ПГОЯ = pr+ow; веса тегов te = 10 (TAGTAB[10] = 0x0500),
#   pr/ow = 11·ПГОЯ (TAGTAB[11] = 0x5400): 9·ПГОЯ + ПГОЯ + ПГОЯ
LB += ABS(PRFA, 'va') + ABS(OWFA, 'aa') + ABS(PGOF, 'sv')        # ПГОЯ := pr+ow
LB += ABS(TEFA, 'va') + ['ml', '5'] + ['ml', '2'] + ABS(K2FA, 'aa') \
    + ABS(K2FA, 'sv')                                            # + 10·te
LB += ABS(PGOF, 'va') + ['ml', '9'] + ABS(PGOF, 'aa') + ABS(PGOF, 'aa') \
    + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')                          # + 11·ПГОЯ
# 24г: веса if/es/jb = 12/13/13 = 9·(сумма) + 3·if + 4·(es+jb)
LB += ABS(IFFA, 'va') + ABS(ESFA, 'aa') + ABS(JBFA, 'aa') + ['ml', '9'] \
    + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')
LB += ABS(IFFA, 'va') + ['ml', '3'] + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')
LB += ABS(ESFA, 'va') + ABS(JBFA, 'aa') + ['ml', '4'] \
    + ABS(K2FA, 'aa') + ABS(K2FA, 'sv')
# 24в-3: K2BЯ = 9·ПГОЯ + 1·ASFA — тег rec2-пары: as → TAGTAB[1] = 0x5500
#   (as-rec2 без правок), pr/ow → TAGTAB[9] = 0x00F0 (vw-вид)
LB += ABS(PGOF, 'va') + ['ml', '9'] + ABS(ASFA, 'aa') + ABS(K2BF, 'sv')
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
# 24в-3: te/ow-слот-запись = (S + TEFA + OWFA)==3 — 'wc te|ow' (S=2) пишут
#   запись; при открытом nb (S=1) = 2 ≠ 3 → K4FA=0 → notbad=0 → брак
#   молчанием (0x0C-див stage1, tracked); при S=0 тоже 1 ≠ 3 (k4K-путь ниже)
LB += ['wc', '6', 'va'] + ABS(TEFA, 'aa') + ABS(OWFA, 'aa') + ['eq', '3'] \
    + ABS(SLOT2, 'sv')
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
    + ABS(ASFA, 'aa') * 2 + ABS(VWFA, 'aa') * 2 + ABS(OWFA, 'aa') * 2 \
    + ABS(TEFA, 'aa') * 2 + ABS(PRFA, 'aa') * 2 \
    + ABS(IFFA, 'aa') * 2 + ABS(ESFA, 'aa') * 2 + ABS(JBFA, 'aa') * 2 \
    + ['eq', '3'] + ABS(NKFA, 'sv')
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
# 24в-3: pr-член = pr·(S==1) — 'pr' НЕ закрывает открытый nb ('nb 7 pr ne'
#   = 18f130e1: конста [15 00 00 00 07] после pr-пар; S=1 переживает pr).
#   Конъюнкция честно: (S==1) + PRFA == 2; приёмник SINK-74 (POS-stamp
#   перезапишет его позже своим мусором — безвредно).
LB += ['wc', '6', 'va', 'eq', '1'] + ABS(PRFA, 'aa') + ['eq', '2'] + ABS(74, 'sv')
LB += ABS(NBFA, 'va') + ABS(FSA, 'aa') + ABS(KA, 'aa') * 2 + ABS(74, 'aa') \
    + ['wc', '6', 'sv']
# 24в-1: k4K = is_k4 И (S==0) — ЕДИНАЯ bare-kind запись: голые va/sv/gp/sp
#   (S==0) и слот-формы 'wc d op' (цифра закрыла S -> тоже S==0) пишут запись
#   [X=SLC][tag]; is_k4 = sv+gp+sp+va (sc/cp/aa слот-форм НЕ имеют — зонды
#   n_sc5/n_cp5/n_aa5 = 0xFE; голые sc/cp/aa = брак 0x0C — див/сил)
LB += ABS(SVFA, 'va') + ABS(GPFA, 'aa') + ABS(SPFA, 'aa') + ABS(VAFA, 'aa') \
    + ABS(ASFA, 'aa') + ABS(VWFA, 'aa') + ABS(OWFA, 'aa') + ABS(TEFA, 'aa') \
    + ABS(IFFA, 'aa') + ABS(ESFA, 'aa') + ABS(JBFA, 'aa') \
    + ABS(S0FA, 'aa') + ['eq', '2'] \
    + ABS(K4FA, 'sv')
# 24в-3: голые te/pr/ow легальны при S==0: (флаг + S0FA)==2 → K4FA=1 (k4K-путь:
#   запись [X][tag] с X = ХАДРЯ-конста). При S=1: (0+1)==1 → K4FA=0 → брак
#   (кроме pr: ниже |= строка добавляет PRFA безусловно — 'nb 7 pr' легален).
# 24в-2: K4FA |= k2K — слот-формы as/vw без цифры. OR безопасен: k4K требует
#   S0==1, k2K — S==2, взаимно исключающи (сумма 0/1). Дальше K4FA един:
#   K-строка, storeval level-1 (K4FA ? SLC : V), notbad-член.
LB += ABS(K4FA, 'va') + ABS(PDGFA, 'aa') + ABS(PRFA, 'aa') \
    + ABS(SLOT2, 'aa') + ABS(K4FA, 'sv')
# 24в-3: K4FA |= k2K + PRFA + te/ow-слот: 'pr' легален ПРИ ЛЮБОМ S ('nb 7 pr'
#   = 89dc4f78, FCODE=9, nb жив — pr НЕ поглотитель, не закрывает, не бракует)
#   и эмитит пары-1+2; te/ow только при S=2 (SLOT2). ХРА-цепь жива.
# K = neK + bareK + k4K; K' = ((K==1) + notEOF) == 2
LB += ABS(NKFA, 'va') + ABS(BKFA, 'aa') + ABS(K4FA, 'aa')
LB += ['eq', '1'] + ABS(NOEFA, 'aa') + ['eq', '2'] + ABS(KA, 'sv')
# 24в-3: ХАДРЯ-адрес пары-1: cell[78] := 100 + 49·te + 27·pr + 45·ow (все
#   разности от 100 — произведение двух цифр: 49=7·7, 27=3·9, 45=5·9, БЕЗ
#   ад-хвостов → ml-цепи честны и при флаге 0). candB = cell[cell[78]]:
#   te → cell[149] = СКРЕ (X_te), pr → cell[127] = порт, ow → cell[145] =
#   STREAM, прочие → cell[100] = SLC. ml жжёт TMP (слоты S/FB/FA) — стеш S
#   в S2DIG-99 (мёртва после SLC-выбора); acc-накопитель = SLOT2-128
#   (мёртва после |= строки выше).
LB += ['wc', '6', 'va'] + ABS(99, 'sv')                 # стеш: S2DIG := S
LB += ABS(TEFA, 'va') + ['ml', '7'] + ['ml', '7'] + ABS(128, 'sv')
LB += ABS(PRFA, 'va') + ['ml', '3'] + ['ml', '9'] + ABS(128, 'aa') \
    + ABS(128, 'sv')                                    # 128 := 49te+27pr
LB += ABS(OWFA, 'va') + ['ml', '5'] + ['ml', '9'] + ABS(128, 'aa') \
    + ABS(128, 'sv')                                    # 128 := +45ow
LB += ABS(99, 'va') + ['wc', '6', 'sv']                 # стеш: S <- S2DIG
# storeval = neK ? NumAcc : (k4K ? SLC : V) — 3-way: level-1 по паре [61,100]
#   (candA=V, candB=SLC) с перезаписью cell[78]=100, результат в VSC
#   (безопасно: цифры имеют k4K=0 -> VSC=V, их A-калькуляция не задета;
#   kinds дают NumAcc'=0, A не читается), level-2 = прежний sel_val(ZVA, NKFA).
LB += N(SLC) + ABS(78, 'sv')                                        # cell[78] := 100
LB += N(100) + ABS(128, 'aa') + ABS(78, 'sv')                       # 24в-3: cell[78] := 100+49te+27pr+45ow (ХАДРЯ)
LB += sel_val(77, K4FA)                                             # acc = k4K ? SLC : V
LB += ABS(VSC, 'sv')                                                # VSC := level-1
LB += N(F3A) + ABS(78, 'sv')                                        # cell[78] := F3A (restore)
LB += sel_val(ZVA, NKFA) + ABS(XORD, 'sv')            # X обычный -> XORD
# 24г: X = (if|es|jb) ? 20 : XOrd (селектор держит ЗНАЧЕНИЯ, не адреса)
LB += ABS(IFFA, 'va') + ABS(ESFA, 'aa') + ABS(JBFA, 'aa') + ABS(CTLFL, 'sv')
LB += N(XORD) + ABS(CTXA, 'sv')                       # candA := адрес XOrd
LB += sel_val(CTXA, CTLFL) + ABS(VAL, 'sv')           # VAL := CTLFL ? 20 : XOrd
# 24г: JBX := MARKP + 20 (MARKP — эмиссионная позиция метки mk)
LB += ABS(MARKP, 'va') + ABS(JBX, 'sv')
LB += N(VAL) + ABS(PXPA, 'sv')                        # candA := адрес VAL
LB += N(JBX) + ABS(PXPB, 'sv')                        # candB := адрес JBX
LB += sel_val(PXPA, JBFA) + ABS(XFIN, 'sv')           # XFIN := JBFA ? JBX : VAL
# 3-й es: Jmp_Slot_3 не патчится stage1 — сайт остаётся 16 (CRC, пересчитан SEAL)
LB += ABS(XFIN, 'va') + ['wc', '1', 'sp']             # cell[PTR] := X
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
# ===== 24г Stage2 (компактный): forecast + cstore на ml-цепочках =====
# ml жжёт СЛОТ S — один стеш на весь блок; KA (=K') не трогается ml.
LB += ['wc', '6', 'va'] + ABS(SK, 'sv')             # SK := S
LB += ABS(FPOS, 'va') + ABS(FPOL, 'sv')             # FPOL := FPOS до записи
LB += ['wc', '8', 'gp'] + ABS(TMPF, 'sv')           # TMPF := tag (cell[TMPF] = tag)
LB += ABS(TMPF, 'va') + ['wc', '8', 'sv']           # W8 := tag как АДРЕС
LB += ['wc', '8', 'gp'] + ABS(SCRV, 'sv')           # SCRV := cell[cell[W8]] = is_b2(tag)
LB += N(0) + ABS(TMPB, 'sv')                        # TMPB := 0 (сброс stale-значения)
LB += cstore(TMPB, KA, ABS(SCRV, 'va'))             # TMPB := K' ? is_b2 : 0
# размер = 4·K' + is_b2(K') + 5·as + 4·(pr+ow)
#   УРОК W-121/кейс68: pr/ow эмитит 9Б = 5Б базы + 4Б хвоста, НЕ 9Б хвоста;
#   старый ml·9 давал +5 на каждое pr → все if/es/TERM/JB-цели ехали вперёд.
LB += ABS(KA, 'va') + ['ml', '4'] + ABS(TMPB, 'aa') + ABS(SCRA, 'sv')
LB += ABS(ASFA, 'va') + ['ml', '5'] + ABS(DEFV, 'sv')
LB += ABS(PGOF, 'va') + ['ml', '4'] + ABS(DEFV, 'aa') + ABS(DEFV, 'sv')
LB += ABS(FPOS, 'va') + ABS(SCRA, 'aa') + ABS(DEFV, 'aa') + ABS(FPOS, 'sv')
# счётчики и номера записей (IFFA+IFCNT == n+1 однозначно)
LB += ABS(IFCNT, 'va') + ABS(IFFA, 'aa') + ABS(IFCNT, 'sv')
LB += ABS(JSCNT, 'va') + ABS(ESFA, 'aa') + ABS(JSCNT, 'sv')
# отказы: 4-й if/es (сумма 5) и jb без живой метки. Sticky: на EOF-итерации
# IFFA/JBFA/ESFA сбрасываются, поэтому без '+ABS(BADxx,"va")' флаг теряется.
LB += ABS(MARKP, 'va') + ABS(CT20, 'cp') + ABS(JBFA, 'aa') \
    + ['eq', '2'] + ABS(BADJB, 'aa') + ABS(BADJB, 'sv')  # sticky (jb): MARKP==20 (mk в 1-й позиции)
LB += ABS(IFFA, 'va') + ABS(IFCNT, 'aa') + ['eq', '5'] \
    + ABS(BADJB, 'aa') + ABS(BADJB, 'sv')    # sticky (if)
LB += ABS(ESFA, 'va') + ABS(JSCNT, 'aa') + ['eq', '5'] \
    + ABS(BADJB, 'aa') + ABS(BADJB, 'sv')    # sticky (es)
# FPOL уже файловая позиция (P+20): слот=R+1, EJ=R+5, TERM=R
V21 = ABS(FPOL, 'va') + ['ad', '1']
V25 = ABS(FPOL, 'va') + ['ad', '5']
V20 = ABS(FPOL, 'va')
LB += site_store(401, IFCNT, IFFA, V21)       # if-слоты → 401..403
LB += site_store(404, JSCNT, ESFA, V21)       # es-слоты → 404..405
LB += site_store(409, JSCNT, ESFA, V25, adj=-1)  # else-join → 409..411 (Jmp_Slot_3: X=0)
LB += cstore(TERMP, TEFA, V20)
LB += cstore(MARKP, MKFA, ABS(FPOL, 'va'))         # mk: метка = текущая позиция
LB += cstore(MARKP, JBFA, N(20))                   # jb: одноразовый сброс в сигнал «метки нет»
LB += ABS(SK, 'va') + ['wc', '6', 'sv']             # S <- SK
# ============================================================
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
LB += ABS(SLC, 'va') + ['wc', '8', 'sp']            # cell[PTR] := SLC (rec2-значение: SLC у as/pr/ow)
# 24в-3: тег rec2-пары = TAGTAB[K2BЯ] (as → 0x5500, pr/ow → 0x00F0); темп
#   cell[148] — FB нужен дважды: база lookup И курсор store
LB += N(TAGTAB) + ['wc', '8', 'sv']          # FB := TAGTAB (иначе K2BF затирает базу — байт-диф 'as')
LB += ABS(K2BF, 'va') + ['wc', '8', 'as'] + ['wc', '8', 'gp']
LB += ABS(148, 'sv')                                # temp: cell[148] := тег
LB += ['wc', '1', 'va'] + ['ad', '1'] + ['wc', '8', 'sv']   # FB := PTR+1 пере-сет
LB += ABS(148, 'va') + ['wc', '8', 'sp']            # cell[PTR+1] := тег
# 24в-3: SEL2-дозапись cell[149] := SLC на as/pr/ow ((1) писал порт/STREAM —
#   restore цепи X_te); te/прочие → 148-мусор (cell[149] цел)
LB += N(148) + ABS(ASFA, 'aa') + ABS(PGOF, 'aa') + ABS(146, 'sv')
LB += ABS(146, 'va') + ['wc', '8', 'sv']            # FB := cell[146] = 148+as+ПГОЯ
LB += ABS(100, 'va') + ['wc', '8', 'sp']            # cell[цель] := SLC
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
LB += ABS(ASFA, 'va') + ABS(PRFA, 'aa') + ABS(OWFA, 'aa') + ['wc', '9', 'as']     # VCNT += as+pr+ow
LB += ABS(ASFA, 'va') + ABS(PRFA, 'aa') + ABS(OWFA, 'aa') \
    + ['ml', '2'] + ['wc', '1', 'as']                   # PTR += 2·(as+pr+ow)
# A = 10*NumAcc + V; ACEL := A
LB += ['wc', '0', 'va', 'ml', '9'] + ABS(F3A, 'aa') + ABS(VSC, 'aa')
LB += ABS(ACEL, 'sv')
LB += ABS(KA, 'va') + ['wc', '6', 'sv']             # restore S <- KA
# 24в-3: ow-пара-3 [0x131][0x1300] — после S-restore (ml-free): FB := PTR,
#   cell[PTR] := 305, cell[PTR+1] := 4864; VCNT += OWFA; PTR += 2·OWFA.
#   На не-ow словах пара @PTR = мусор ЗА рекордом (as: за rec2-парой, PTR уже
#   += 2·ASFA) — затирается следующим рекордом; за VCNT·2 не читается.
LB += ['wc', '1', 'va'] + ['wc', '8', 'sv']                  # FB := PTR
LB += N(305) + ['wc', '8', 'sp']                             # cell[PTR] := 0x131
LB += ['wc', '8', 'va'] + ['ad', '1'] + ['wc', '8', 'sv']    # FB := PTR+1
LB += N(4864) + ['wc', '8', 'sp']                            # cell[PTR+1] := 0x1300
LB += ABS(OWFA, 'va') + ['wc', '9', 'as']                    # VCNT += OWFA
LB += ABS(OWFA, 'va') + ABS(OWFA, 'aa') + ['wc', '1', 'as']  # PTR += 2·OWFA
# NumAcc' = is_dig ? A : 0; 24в-3: pr НЕ сбрасывает NumAcc — 'nb 7 pr ne'
#   ждёт цифру 7 из старого NumAcc (иначе neK-ветка читает 0 — байт-диф @33).
LB += sel_val(ZNA, DGFA) + ABS(151, 'sv')           # base := is_dig ? A : 0
LB += ABS(0, 'va') + ABS(152, 'sv')                 # cell[152] := адрес нуля
LB += N(F3A) + ABS(153, 'sv')                       # cell[153] := адрес NumAcc
LB += sel_val(152, PRFA) + ABS(151, 'aa') \
    + ['wc', '0', 'sv']                             # NumAcc' := base + (pr ? NumAcc_old : 0)
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
# 24г: mk-легальность = MKFA & (S==0) — 'mk' не поглощает nb (0x0C при открытом)
LB += ABS(MKFA, 'va') + ABS(S0FA, 'aa') + ['eq', '2'] + ABS(MKLG, 'sv')
LB += ['wc', '6', 'va'] + ABS(NBFA, 'aa') + ['eq', '2'] + ABS(DTFA, 'aa') \
    + ABS(DGFA, 'aa') + ABS(NKFA, 'aa') + ABS(K4FA, 'aa') + ABS(EQKFA, 'aa') \
    + ABS(MKLG, 'aa') + ABS(BADIF, 'aa') + ABS(BADEJ, 'aa') + ABS(BADJB, 'aa')
LB += ['eq', '0'] + ABS(BSFA, 'sv')
# L = (badsum + E + dot) > 0; stay = (L==0)
LB += ABS(BSFA, 'va') + ABS(EFASC, 'aa') + ABS(DTFA, 'aa') + ['gt', '0']
LB += ['eq', '0', 'if']                    # if#1: stay (BADJB уже в BSFA)
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
    + ABS(BADJB, 'aa') \
    + ['if']                              # if#2: sticky jb-отказ -> молчание
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
# 24г Stage2: патч 5 слотов в записанном теле (до SEAL).
# DEF = TERMP!=0 ? cell[TERMP] : 20 (пара DEFC=[CT20,TERMP])
PS += ABS(TERMP, 'va') + ['eq', '0'] + ABS(TMPF, 'sv')
PS += sel_val(DEFC, TMPF) + ABS(DEFV, 'sv')
# if n: target = EJn!=0 ? EJn : DEF (пары IFPA/IFPB/IFPC = [DEFV,EJn]).
#   УРОК 24г: EJn привязан к 'es' (Else_Join), поэтому при 'es' без 'if'
#   EJn!=0 и cleanup-цикл перезаписывал DEF — es-патч получал мусор. Цель if
#   идёт в ОТДЕЛЬНЫЙ IFTGT, а DEFV=d e f остаётся нетронутым для es-патчей.
for site, ej, pair in ((SITE1, EJ1, IFPA), (SITE2, EJ2, IFPB), (SITE3, EJ3, IFPC)):
    PS += ABS(ej, 'va') + ['eq', '0'] + ABS(TMPF, 'sv')
    PS += sel_val(pair, TMPF) + ABS(IFTGT, 'sv')
    PS += ABS(site, 'va') + ABS(STREAM, 'sv') + ABS(310, 'sc')
    PS += ABS(IFTGT, 'va') + ['wc', '8', 'sv', 'wc', '8', 'ow']
# es 1/2: target = DEF (3-й es не патчится)
for site in (ESITE1, ESITE2):
    PS += ABS(site, 'va') + ABS(STREAM, 'sv') + ABS(310, 'sc')
    PS += ABS(DEFV, 'va') + ['wc', '8', 'sv', 'wc', '8', 'ow']
PS += ABS(309, 'sc') + ABS(307, 'sc')
# честный терминатор программы (канон scan7): без 'te' VM уходит в мусор
# после конца кода — KERNEL PANIC "недокументированный опкод 0xFF", rc=1.
PS += ['te']

PROGRAM = INIT + ['mk'] + LB + PS

MAX_USER_WORDS = 8190  # 24д W-122: граница тома поднята 4094→8190 (MAX_SOURCE_WORDS 0x1000→0x2000, спринт 101 — прецедент W-120)
flat = ' '.join(PROGRAM)
TOKENS = len(flat.split())
POS_PATH = r'H:\Project\MiniOS_CtOS\Python_compiler\pos_wc14v3ring.words'
assert TOKENS <= MAX_USER_WORDS, 'tokens %d > %d' % (TOKENS, MAX_USER_WORDS)
with open(POS_PATH, 'w', encoding='ascii', newline='') as f:
    f.write(flat + '\n')
print('pos_wc14v3ring tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
