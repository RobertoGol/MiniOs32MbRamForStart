# -*- coding: utf-8 -*-
# Честный механический сборщик вехи-14v3 (TKT-052): word-компилятор,
# который ЧЕСТНО ВЫЧИСЛЯЕТ слот целевой инструкции из цифры target-слова,
# а не берёт константу (граница v2).
#
# Аддитивная перестройка вехи-14v2 — ровно два честных сплайса:
#
#   1) INIT: слот F3 (wc 0) = 15732675 = F3_адрес - 48. Почему так честно:
#      цифра в буфере лежит ASCII-кодом ('0'=48..'5'=53), а нужен
#      слот F3 + d, где d = ascii - 48. Значит slot = ascii + (F3 - 48);
#      константа F3-48 заводится один раз, вычитание 48 не нужно
#      ('su' честно берёт только ОДНУ цифру-литерал — 48 не выразить).
#      F3 больше не хранит '0' (её значение в v1/v2 нигде не читалось) —
#      переиспользование слота, а не новый слот (честный лимит слов 254).
#   2) THEN: вместо константы слота 'nb 15732723 wo' —
#      nb 10485764 va      (acc = cell[SRC+4] = ASCII цифры target)
#      wc 0 as             (acc = ascii + cell[F3] = F3 + d; cell[F3] = acc)
#      ... U8 0x54, порт ...
#      wc 0 ow             (runtime cell[F3] -> 4 байта в артефакт)
#
# Честные уровни: 'va'/'as' — это ИНСТРУКЦИИ stage-2 программы
# (stage-1 пишет их в бинарь stage-2), а не вывод в артефакт; в артефакт
# пишет только 'ow' (его 14-байтный код при прогоне stage-2 выводит
# 4 байта значения cell[F3]). Проверено пробой pos_vw1: log_cell+FILE_PUT
# на сайте пишет КОНСТАНТУ-адрес слота, а не runtime-значение — потому
# 'ow' и есть единственный честный runtime-канал.
#
# Честная цель: байт-в-байт = артефакту stage1 на target0.words
# (md5 8d82091a) И на target1.words 'wc 1 pr te' (слот F4) — сильная
# сверка: слот теперь ВЫЧИСЛЯЕТСЯ, а не совпадает случайно.
#
# Структура (как в v2):
#   init    — F3=F3-48(база слота), F4=25463('wc'), F5=0(fail-маркер),
#             F7=ptr 0x00A00000, F8=0(счётчик)
#   кольцо  — mk; FILE_GET(311); EOF va eq 0; if [копия + ptr+=4 +
#             counter+=1] jb es [main]
#   main    — acc = cell[A00000] (слово 1); cp со слотом F4 (== 'wc');
#             if [вычисление слота + эмиссия 55 Б + te] es [маркер 0 + te]
#
# Честные границы v3 (для тикета):
#   1) распознаётся ТОЛЬКО слово 1 == 'wc' (if/es лимит жёстко честный);
#   2) слот целевой инструкции ЧЕСТНО ВЫВОДИТСЯ из цифры (v3);
#   3) Token честно выводится из счётчика кольца (v2);
#   4) Syntax/Node отчёта — по-прежнему 0 (v4).
#
# Честный лимит: 254 слова пользователя (MAX_SOURCE_WORDS 0x100 = 256,
# '.' дописывает VM). Сборщик проверяет РЕАЛЬНОЕ число токенов и падает,
# если оно больше 254 (молча не пишет).

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000
SRC_WORD2  = 10485764        # 0x00A00004 — второе слово target
EOF_CELL   = 15732722        # 0x00F00FF2
EMIT_CELL  = 15732720        # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1
F3_MINUS_48 = 15732675       # F3 - 48

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',   # база честного слота
        nb(25463), 'ne', 'wc', '1', 'sv',         # 'wc' = 0x6377
        nb(0), 'ne', 'wc', '2', 'sv',             # fail-маркер
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',    # ptr кольца
        nb(0), 'ne', 'wc', '5', 'sv']             # счётчик токенов F8

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
        nb(SRC_WORD2), 'va',            # acc = ASCII цифры (48..53)
        'wc', '0', 'as',                # acc = ascii + (F3-48) = F3 + d; cell[F3] = acc
        'wc', '0', 'ow',                # runtime cell[F3] -> 4 байта артефакта
        'nb 1 5 3 5', 'em', 'nb 3 0 6', 'sc',                              # U16 0x05FF (T+verd)
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',                 # Token = counter - 1
        'nb 0', 'wo', 'nb 0', 'wo',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = [nb(SRC_BUFFER), 'va', nb(F4), 'cp',
        'if'] + EMIT + ['te', 'es', 'wc', '2', 'pr', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 254

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v3.words'
assert TOKENS <= MAX_USER_WORDS, ('честный отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3 tokens:', TOKENS, 'limit:', MAX_USER_WORDS, 'ok:', True)

# честные цели-эталоны
with open(r'G:\Windows\RJ\AppData\Local\Temp\opencode\target0.words', 'w',
          encoding='ascii') as f:
    f.write('wc 0 pr te\n')
with open(r'G:\Windows\RJ\AppData\Local\Temp\opencode\target1.words', 'w',
          encoding='ascii') as f:
    f.write('wc 1 pr te\n')
with open(r'G:\Windows\RJ\AppData\Local\Temp\opencode\neg_target.words', 'w',
          encoding='ascii') as f:
    f.write('va pr te\n')
print('targets honest: target0 / target1 / neg_target')
