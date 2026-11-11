# -*- coding: utf-8 -*-
# Сборщик СМЕШАННОГО честного тома 'wc d pr d3 wc d2 te d32'
# Shape-T4x2 mixed-L (веха-23, спринт 37, W-57, TKT-052). База =
# wc14v3te2_build.py (двойной te-том 683 ток, W-56) + честные окна
# wc14v3_gen.py (pr: U8 84 + BE32-порт 0x3F0050C0 + слот 'wc 0 ow' +
# U8 21 + BE32(d3); te: U8 5 + U8 21 + BE32(d3)) + честная карта
# probe53 (refs stage1 для смешанных целей: 'wc 5 pr 3 wc 5 te 3' =
# 65 Б 1c775e42, emit = 54 3F 00 50 C0 00 F0 0F F8 15 BE32(d31) +
# 05 15 BE32(d32); СЛОТ-БАЙТ ЖИВ: 'wc 7 pr 3 wc 5 te 3' = 66baed44
# (слот FA = F3+7); d2-ИНВАРИАНТНОСТЬ: 'wc 5 pr 3 wc 7 te 3' = ТОТ ЖЕ
# 1c775e42 — слот стейтмента-2 не доходит до артефакта (te-окно без
# слота); trailing-dot игнорируется обеими сторонами; reversed
# 'wc 5 te 3 wc 5 pr 3' stage1 компилит (3f3634ef) — том обязан
# молчать (кросс-молчание слоя pr×te).
# Честный дизайн: C-блоки (v3-слот) УХОДЯТ из CHECK — слот-калькуляция
# переезжает в секцию эмиссии, т.к. pr-emit ЧИТАЕТ cell[F3]:
#   SLOT1 (13 ток) = 'nb(SRC_WORD2) va wc 0 as' — cell[F3] =
#   F3_MINUS_48 (INIT pristine, в CHECK больше нет F3-записей) +
#   ASCII(d1) = F3 + d1 — ПЕРЕД pr-окном (иначе слот-байт честно
#   испорчен); SLOT2 (26 ток) = RESET cell[F3] = F3_MINUS_48 +
#   повторный 'wc 0 as' на word5 — честный side-effect стейтмента-2
#   (ПОСЛЕ emit1; te-окно слот не читает, но семантика T4 честно
#   выполняется). CHECK1: p0 (word0=='wc', PA+=), valid(d1)
#   digit-block (57), p2 (word2=='pr', конст F6=wc3, PD+=),
#   valid(d31) (57). CHECK2: p0-2 (word4=='wc', PA+=), valid(d2)
#   digit-block (57), p2-2 (word6=='te', конст PB=wc7, PD+=),
#   valid(d32) (57). RELOAD1 d31 -> wc2 ПОСЛЕ последнего F5-cp (B4)
#   (прецедент W-56/probe52: reload до F5-cp портит valid); E2 d32
#   в секции эмиссии перед BE32(d32). Затвор: PA(6) + PD(2) +
#   ppunkt(word8=='.') == 9; Token = 8 (конст отчёта). Кросс-молчания
#   честны: te×pr reversed (word2='te') / te×te (word2='te') /
#   pr×pr (word6='pr') / single / 3-form / хвост-мусор -> сумма != 9.
# Лимит честного тома вехи-23 = 1022 ток (regr55).
# pos_wc14v3prte.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('pr')
WORD4      = 10485772        # word3 (d31)
WORD5      = 10485776        # word4 ('wc' стейтмента-2)
WORD6      = 10485780        # word5 (d2)
WORD7      = 10485784        # word6 ('te' стейтмента-2)
WORD8      = 10485788        # word7 (d32)
WORD9      = 10485792        # word8 ('.' терминатор)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725
F6 = 15732726                # wc 3 - АДРЕС-конст LE2('pr') = 29296 (INIT)
PA = 15732729
PB = 15732730                # wc 7 - АДРЕС-конст LE2('te') = 25972 (INIT)
PC = 15732731                # wc 8 - 46 ('.' терминатор)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(29296), 'ne', 'wc', '3', 'sv',           # 'pr' (LE2)
        nb(25972), 'ne', 'wc', '7', 'sv',           # 'te' (LE2)
        nb(46), 'ne', 'wc', '8', 'sv']               # '.' (терминатор)

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

# CHECK1 = честный скан стейтмента-1 (слова 0..3), БЕЗ C-блока:
# слот-калькуляция в секции эмиссии (pr-emit читает cell[F3])
CHECK1 = [nb(SRC_BUFFER), 'va',
          nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
          'wc', '6', 'sv',              # PA = p0
          # B1: честный digit-block (d1): bad в PF
          nb(SRC_WORD2), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid1 = (bad1 == 0)
          'wc', '6', 'as',              # PA += valid1
          # D1: p2 = (word2 == LE2('pr'), конст F6 = wc 3)
          nb(WORD3), 'va', nb(F6), 'cp',
          'wc', '9', 'sv',              # PD = p2
          # B2: честный digit-block (d31)
          nb(WORD4), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid2 = (bad2 == 0)
          'wc', '6', 'as']              # PA += valid2

# CHECK2 = честный скан стейтмента-2 (слова 4..7), БЕЗ C-блока
CHECK2 = [
          # A2: p0-2 = (word4 == 'wc'), PA +=
          nb(WORD5), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B3: честный digit-block (d2): bad3 в PF
          nb(WORD6), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # D2: p2-2 = (word6 == LE2('te')), PD +=
          nb(WORD7), 'va', nb(PB), 'cp',
          'wc', '9', 'as',
          # B4: честный digit-block (d32): bad4 в PF
          nb(WORD8), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid4 = (bad4 == 0)
          'wc', '6', 'as']              # PA += valid4

# RELOAD1: d31 -> wc2 (= F5) ДЛЯ BE32 pr-хвоста. Честный порядок
# (прецедент W-56/probe52): reload ПОСЛЕ последнего F5-cp (B4).
RELOAD1 = [nb(WORD4), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d31

# F2/G2: ppunkt = (word8 == '.' — терминатор: ровно 8 токенов);
# затвор: PA (6) + PD (2) + ppunkt == 9
TAIL_CHECK = [nb(WORD9), 'va', nb(PC), 'cp',
              nb(PA), 'aa',
              nb(PD), 'aa',
              'eq', '9',
              'if']

EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель

# SLOT1: cell[F3] = F3_MINUS_48 (INIT pristine) + ASCII(d1) = F3 + d1
# — ПЕРЕД pr-окном (слот-байт читает cell[F3])
SLOT1 = [nb(SRC_WORD2), 'va', 'wc', '0', 'as']

# PR-WIN1 (окно pr, wc14v3_gen.py): U8 84 + BE32-порт + слот +
# U8 21 + BE32(d31)
PRWIN1 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',     # U8 84 (pr)
          'nb 1 0 5 6 9 8 5 2 8 0', 'wo',       # 0x3F0050C0
          'wc', '0', 'ow',                      # BE32(F3+d1)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',     # T4-хвост U8 21
          'wc', '2', 'ow']                      # BE32(d31)

# SLOT2: честный side-effect стейтмента-2: RESET cell[F3] = F3 - 48,
# затем 'wc 0 as' на word5 -> cell[F3] = F3 + d2 (ПОСЛЕ emit1 —
# pr-слот уже честно в артефакте; te-окно слот не читает)
SLOT2 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
         nb(WORD6), 'va', 'wc', '0', 'as']

# E2: reload d32 -> wc2 (BE32 te-хвоста)
E2 = [nb(WORD8), 'va',
      'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
      'wc', '2', 'sv']

# TE-WIN2 (окно te): U8 5 + U8 21 + BE32(d32)
TEWIN2 = ['nb 5', 'em', 'nb 3 0 8', 'sc',       # U8 5 (te)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',     # T4-хвост U8 21
          'wc', '2', 'ow']                      # BE32(d32)

EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 8', 'wo',                                    # Token = 8 (конст)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK1 + CHECK2 + RELOAD1 + TAIL_CHECK + EMIT_HEAD + SLOT1 \
       + PRWIN1 + SLOT2 + E2 + TEWIN2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v3prte.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3prte tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
