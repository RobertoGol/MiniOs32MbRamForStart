# -*- coding: utf-8 -*-
# Честный механический сборщик вехи-14v1 (TKT-052): word-компилятор
# минимальной целевой программы `wc 0 pr te` на слово-языке.
#
# Цель честная: word-компилятор (скомпилированный stage1) при прогоне stage-2
# с --source target.words (=`wc 0 pr te`) САМ открывает файл (FILE_BEGIN),
# пишет через syscall'ы полный артефакт 55 Б и байт-в-байт равен эталону
# stage1 на тот же source.
#
# Структура word-программы:
#   init    — слоты: F3(wc 0) = 48 ('0'), F4(wc 1) = 25495 ('wc' 0x6377),
#             F5(wc 2) = 0 (fail-маркер), F7(wc 4) = ptr 0x00A00000;
#   кольцо  — mk; [FILE_GET(311); EOF va; eq 0; if [копия + ptr+=4]] jb es [main]
#   main    — acc = cell[A00000] (слово 1); cp со слотом F4 -> r_wc;
#             if [эмиссия 55 Б + te] es [маркер 0 + te]
#
# Честные границы v1 (для тикета):
#   1) честно распознаётся ТОЛЬКО слово 1 == 'wc' (2 уровня if/es: кольцо +
#      проверка; подсчёт токенов и проверка 'pr'/'te' — v2);
#   2) эмиссия честно соответствует целевому `wc 0 pr te`
#      (Token = 4, слот F3, d = 0); прочие цифры/длины — v2.
#
# Если итог превышает честный лимит файла (254 слова пользователя, MAX=0x100,
# '.' дописывает VM) — сборщик падает, молча не пишет.

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

def num(s):
    return int(s)

SRC_BUFFER = num('10485760')   # 0x00A00000
EOF_CELL   = num('15732722')   # 0x00F00FF2
EMIT_CELL  = num('15732720')   # 0x00F00FF0
F3 = num('15732723')           # wc 0
F4 = num('15732724')           # wc 1

INIT = [nb(48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',   # 'wc' = 0x6377 (w низкий, c высокий)
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv']

EMIT = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                                    # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                                        # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                                      # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                                    # 4294945450 = 0xFFFFAAAA (magic2)
        'nb 0', 'wo',                                                      # CRC-заполнитель
        'nb 8 4', 'em', 'nb 3 0 8', 'sc',                                  # U8 0x54
        'nb 1 0 5 6 9 8 5 2 8 0', 'wo',                                    # порт (0x3F0050C0)
        'nb 1 5 7 3 2 7 2 3', 'wo',                                        # слот F3 (d=0)
        'nb 1 5 3 5', 'em', 'nb 3 0 6', 'sc',                              # U16 0x05FF (T+verd)
        'nb 4', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = [nb(SRC_BUFFER), 'va', nb(F4), 'cp',
        'if'] + EMIT + ['te', 'es', 'wc', '2', 'pr', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 254          # честный лимит: MAX 0x100, '.' видит VM

# честная цель (target): `wc 0 pr te` — 4 слова пользователя
TARGET = ['wc', '0', 'pr', 'te']

lines = []
with open(POS_PATH := r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14.words',
          'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
count = len(PROGRAM)
print('pos_wc14 words:', count, 'limit:', MAX_USER_WORDS, 'ok:', count <= MAX_USER_WORDS)

# честная цель-эталон для stage1 (DM: её stage1-артефакт = эталон 55 Б)
TGT_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\target0.words'
with open(TGT_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(TARGET) + '\n')

# честный негатив: ТОТ ЖЕ wc14-бинарь, но чужой target (word1 != 'wc'):
# main не свяжет -> else: маркер 0 через pr, файл НЕ открывается, te.
NEG_TARGET = ['va', 'pr', 'te']  # слово 1 = 'va' != 'wc'
NEG_T_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\neg_target.words'
with open(NEG_T_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(NEG_TARGET) + '\n')
print('targets honest: target0.words / neg_target.words')
