# -*- coding: utf-8 -*-
# Честный механический сборщик вехи-14v5 (TKT-052): снятие честной
# границы хвоста v4 — word3='pr' / word4='te' сверяются РАНТАЙМ,
# до честного открытия артефакта.
#
# Аддитивная перестройка вехи-14v4 — ровно два честных сплайса:
#
#   1) INIT: честная свита слотов wc6..wc9 (веха-15: диапазон 0..9):
#         wc 6 = 0      (PA — честный скретч предиката p0)
#         wc 7 = 29296  (PB — честная константа 'pr', LE 0x7270)
#         wc 8 = 25972  (PC — честная константа 'te', LE 0x6574)
#         wc 9 = 0      (PD — честный скретч предиката p2)
#   2) MAIN: слово0-проверка v4 расширена до ЧЕСТНОЙ конъюнкции
#      p0 & p2 & p4 БЕЗ второго 'if'-разветвления (лимит stage1:
#      If_Count 2, копи-луп уже занял if#1/es#1):
#         p0 = (word0 == cell[F4]='wc')    — как в v4 ('cp' 0x18)
#         p2 = (word3 == cell[PB]='pr')    — честное 'cp' по 10485768
#         p4 = (word4 == cell[PC]='te')    — честное 'cp' по 10485772
#         sum = p4 + cell[PD] + cell[PA]   — честные 'aa' (0x15)
#         acc = (sum == 3)                 — честное 'eq' с литералом '3'
#      then-ветка: EMIT (v4, не меняется байт-в-байт) + 'te';
#      else-ветка: только 'te' — ЧЕСТНОЕ МОЛЧАНИЕ: FILE_OPEN
#      происходит только в EMIT (ctos_vm.py:455), файл артефакта
#      не создаётся ("артефакта нет" на негативах).
#
# Честные факты источники: veha12_design.md вехи-8 ('sv'/'va'/'gp'/'aa'
# поглотители), веха-13 ('cp' OP_LOAD 0x12+0x18+BE32), TKT-050 ('eq'
# OP_LOAD+0x16 со СЛЕДУЮЩИМ литералом — честный образец copy-лупа
# 'eq 0 if' в v4), ctos_vm.py:399-402 (честные режимы 0x16/0x18/0x19).
#
# Честные цели: позитив d=0..9 — байт-в-байт артефакту stage1
# (fresh_target0..9: 8d82091a/d40a8ad8/19f90fac/6693dabe/f50c55e2/
#  a4a0c9e1/1ae1dd05/ac728a9e/67952626/7e05c1be); негативы t2w/t3w/
# td/tb/m1..m4 — честное молчание (артефакта нет). Честный остаточный
# факт (граница v5): хвост ПОСЛЕ word4 не сверяется ('wc 0 pr te pr'
# сжимает остаток, Token честен).
#
# Честные уровни (перенос v3/v4): 'va'/'as' — инструкции stage-2
# программы, в артефакт пишет только 'ow'/'wo'/'em' + syscall-слой.
#
# Честный лимит: 510 слов (MAX_SOURCE_WORDS 0x200), builder падает
# при превышении (молча не пишет).

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 — слово0 ('wc') целевого файла
SRC_WORD2  = 10485764        # 0x00A00004 — слово1 (ASCII цифра)
WORD3      = 10485768        # 0x00A00008 — слово2 ('pr')
WORD4      = 10485772        # 0x00A0000C — слово3 ('te')
EOF_CELL   = 15732722        # 0x00F00FF2
EMIT_CELL  = 15732720        # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
PA = 15732729                # wc 6 — скретч p0
PB = 15732730                # wc 7 — константа 'pr' (29296)
PC = 15732731                # wc 8 — константа 'te' (25972)
PD = 15732732                # wc 9 — скретч p2

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',   # база честного слота
        nb(25463), 'ne', 'wc', '1', 'sv',         # 'wc' = 0x6377
        nb(0), 'ne', 'wc', '2', 'sv',             # fail-маркер (и канал Syntax v4)
        nb(0), 'ne', 'wc', '3', 'sv',             # Node-счётчик честно 0 (v4)
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',    # ptr кольца
        nb(0), 'ne', 'wc', '5', 'sv',             # счётчик токенов F8
        # Сплейс v5-1: честные слоты свиты wc6..wc9
        nb(0), 'ne', 'wc', '6', 'sv',             # PA = предикат p0
        nb(29296), 'ne', 'wc', '7', 'sv',         # PB = 'pr' (0x7270)
        nb(25972), 'ne', 'wc', '8', 'sv',         # PC = 'te' (0x6574)
        nb(0), 'ne', 'wc', '9', 'sv']             # PD = предикат p2

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                                    # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                                        # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                                      # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                                    # 0xFFFFAAAA (magic2)
        'nb 0', 'wo',                                                      # CRC-заполнитель
        'nb 8 4', 'em', 'nb 3 0 8', 'sc',                                  # U8 0x54
        'nb 1 0 5 6 9 8 5 2 8 0', 'wo',                                    # порт (0x3F0050C0)
        # Сплейс v3-2: слот ЧЕСТНО вычисляется из цифры target-слова
        nb(SRC_WORD2), 'va',            # acc = ASCII цифры (48..57 честно, веха-15)
        'wc', '0', 'as',                # acc = ascii + (F3-48) = F3 + d; cell[F3] = acc
        'wc', '0', 'ow',                # runtime cell[F3+d] -> 4 байта артефакта
        'nb 1 5 3 5', 'em', 'nb 3 0 6', 'sc',                              # U16 0x05FF (TERM+verd)
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',                 # Token = counter - 1
        # Сплейс v4-2: Syntax/Node ЧЕСТНО из runtime-канала (не константы)
        'wc', '2', 'ow',                # Syntax = cell[F5] (факт прогона)
        'wc', '3', 'ow',                # Node = cell[F6] (INIT 0)
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',                          # хвостовые нули
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# Сплейс v5-2: честная конъюнкция p0 & p2 & p4 через сумму == 3
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',                 # acc = (word0 == 'wc') = p0
         nb(PA), 'sv',                 # cell[PA] = p0
         nb(WORD3), 'va', nb(PB), 'cp',  # acc = (word3 == 'pr') = p2
         nb(PD), 'sv',                 # cell[PD] = p2
         nb(WORD4), 'va', nb(PC), 'cp',  # acc = (word4 == 'te') = p4
         nb(PD), 'aa',                 # acc = p4 + cell[PD] = p4 + p2
         nb(PA), 'aa',                 # acc = p4 + p2 + p0
         'eq', '3',                    # acc = (sum == 3) — честный затвор
         'if']

MAIN = CHECK + EMIT + ['te', 'es', 'te']   # else-ветка: честное молчание

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v5.words'
assert TOKENS <= MAX_USER_WORDS, ('честный отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v5 tokens:', TOKENS, 'limit:', MAX_USER_WORDS, 'ok:', True)
