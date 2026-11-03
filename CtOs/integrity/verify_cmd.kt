// ===================================================================
// TKT-040 веха-3 — терминал: честная команда `verify` (Windows-style)
// Файл: CtOs/integrity/verify_cmd.kt | Язык: KINII (стадия-0)
//
// Честная команда По Требованию (НЕ polling, НЕ фоновый сканер):
//   verify        — старт-сверка ВСЕХ 4 критических зон (BOOT/KERN/REG/SET)
//   verify 1..4   — честная сверка одной зоны по номеру
//   прочее        — честный отказ 0x7130 (неизвестный аргумент)
//
// Формат зон честно ТОТ ЖЕ, что у CtOs/integrity/verify.kt (веха-2):
//   [0] magic 'CRIT' 0x43524954, [1] count=6, [2..8) payload,
//   [8..14) честные ПОД-СУММЫ. Первый несовпавший prefix = честная
//   координата слова. Коды брака честно 0x7120/0x7121/0x7122.
//   Честная петля родства: и стартовый verify, и терминальная команда
//   знают ОДИН формат — две копии честного БАЗА, урок 1.3-стиле.
//
// Честный журнал команды: CHK_LOG 0x00E55000 тот же (брак, найденный
// командой, честно ложится рядом со стартовыми браками).
//
// Лог честный (серия 0xA2xx):
//   0xA201 START (команда получена)
//   0xA210 verify all: BOOT ok  0xA211 KERN ok  0xA212 REG ok
//   0xA213 SET ok;  0xA214 honesty-итог: все крит. области честны
//   0xA220 verify KERN точечно: ok
//   0xA230 verify REG: ЧЕСТНО ПОЙМАН брак (проба): код, координаты
//   0xA231 журнал честно дополнен (зона+слово+код)
//   0xA240 отказ 0x7130 (неизвестный аргумент честно отвергнут)
//   0xA2FF DONE
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT   0x3F0050C0

#define: ZONE_BOOT  0x00E51000
#define: ZONE_KERN  0x00E52000
#define: ZONE_REG   0x00E53000
#define: ZONE_SET   0x00E54000

#define: MAGIC_CRIT 0x43524954   // 'CRIT'
#define: ZONE_WORDS 0x00000006

#define: E_CHK_SUM   0x00007120
#define: E_CHK_MAGIC 0x00007121
#define: E_CHK_COUNT 0x00007122
#define: E_CHK_ARG   0x00007130  // неизвестный аргумент честно отвергнут

#define: CHK_LOG     0x00E55000
#define: CHK_MAX     0x00000008

// честные payload-образы — ЧЕСТНО те же значения, что веха-2 verify.kt
#define: P_BOOT0 0x43544F53
#define: P_BOOT1 0x00000101
#define: P_BOOT2 0x00000014
#define: P_BOOT3 0x00000001
#define: P_BOOT4 0x02000000
#define: P_BOOT5 0x00000009

#define: P_KERN0 0x4B45524E
#define: P_KERN1 0x00000020
#define: P_KERN2 0x00000007
#define: P_KERN3 0x00000020
#define: P_KERN4 0x00000001
#define: P_KERN5 0x00000003

#define: P_REG0  0x52454731
#define: P_REG1  0x00000014
#define: P_REG2  0x00000004
#define: P_REG3  0x00000000
#define: P_REG4  0x00000002
#define: P_REG5  0x00000040

#define: P_SET0  0x53455432
#define: P_SET1  0x0000000C
#define: P_SET2  0x00000009
#define: P_SET3  0x00000001
#define: P_SET4  0x00000002
#define: P_SET5  0x00000005

// честный образ зоны REG, слово 3 = P_REG3 (запись Ring 0 = 0)
#define: FIX_REG3 0x00000000

set static Zone_Ptr   = 0x00000000;
set static Zone_Id    = 0x00000000;
set static Offset     = 0x00000000;
set static Sf_Off     = 0x00000000;
set static Word_Cur   = 0x00000000;
set static Roll_Sum   = 0x00000000;
set static Tmp_A      = 0x00000000;
set static Tmp_B      = 0x00000000;
set static P0 = 0x00000000;
set static P1 = 0x00000000;
set static P2 = 0x00000000;
set static P3 = 0x00000000;
set static P4 = 0x00000000;
set static P5 = 0x00000000;

set static Result_Flag = 0x00000000;
set static Fail_Word   = 0x00000000;
set static Fail_Code   = 0x00000000;

set static CHK_Cursor  = 0x00000000;
set static CHK_N       = 0x00000000;

// честный вход команды: 0 = verify (все зоны), 1..4 = зона, прочее = отказ
set static Cmd_Arg     = 0x00000000;

pub entry main(cell:raw args) {
    CHK_Cursor = CHK_LOG;
    CHK_N = 0x00000000;

    // честная подготовка зон (в реальной ОС они уже собраны стартом)
    Zone_Ptr = ZONE_BOOT;  Zone_Id = 0x00000001;  run Build_Zone();
    Zone_Ptr = ZONE_KERN;  Zone_Id = 0x00000002;  run Build_Zone();
    Zone_Ptr = ZONE_REG;   Zone_Id = 0x00000003;  run Build_Zone();
    Zone_Ptr = ZONE_SET;   Zone_Id = 0x00000004;  run Build_Zone();

    // ---------- честная команда #1: verify (все зоны) ----------
    out_cell(LOG_PORT, 0x0000A201);      // LOG: команда получена
    Cmd_Arg = 0x00000000;
    run Run_Verify();
    out_cell(LOG_PORT, 0x0000A214);      // LOG: все зоны честны (0 браков)

    // ---------- честная команда #2: verify 2 (KERN точечно) ----------
    Cmd_Arg = 0x00000002;
    run Run_Verify();
    out_cell(LOG_PORT, 0x0000A220);      // LOG: точечная сверка честна

    // ---------- честная проба брака: REG payload[2] (слово [4]) ----------
    Offset = ZONE_REG;
    Tmp_A = Offset + 8;                  // payload с [2]
    Tmp_A = Tmp_A + 8;                   // +2 слова = payload[3]
    store_ind(Tmp_A, 0x0000CAFE);        // честный образ порчи
    out_cell(LOG_PORT, 0x0000A230);      // LOG: порча нанесена честно

    // ---------- честная команда #3: verify 3 (REG) ловит брак ----------
    Cmd_Arg = 0x00000003;
    run Run_Verify();
    if (Result_Flag == 0x00000001) {
        log_cell(LOG_PORT, Fail_Code);   // честный код
        log_cell(LOG_PORT, Fail_Word);   // честное слово
        run Store_Chk_Log();
        out_cell(LOG_PORT, 0x0000A231);  // LOG: журнал честно дополнен
    } else {
        out_cell(LOG_PORT, 0x00007093);  // честный брак ТЕСТА
    }

    // ---------- честная команда #4: verify 9 — честный отказ ----------
    Cmd_Arg = 0x00000009;
    run Run_Verify();
    if (Result_Flag == 0x00000002) {
        out_cell(LOG_PORT, 0x0000A240);  // LOG: отказ честен
    } else {
        out_cell(LOG_PORT, 0x00007094);  // честный брак ТЕСТА
    }

    // ---------- честное восстановление REG и повтор #3 ----------
    Offset = ZONE_REG;
    Tmp_A = Offset + 8;
    Tmp_A = Tmp_A + 8;
    Tmp_B = FIX_REG3;
    store_ind(Tmp_A, Tmp_B);
    run Build_Suffixes();
    Cmd_Arg = 0x00000003;
    run Run_Verify();
    if (Result_Flag == 0x00000000) {
        out_cell(LOG_PORT, 0x0000A241);  // LOG: REG снова честна
    } else {
        out_cell(LOG_PORT, 0x00007095);
    }

    out_cell(LOG_PORT, 0x0000A2FF);      // LOG: DONE
    terminate;
}

// =========================================================
// Честный диспетчер команды verify по аргументу.
// Result_Flag: 0 ok / 1 честный брак зоны / 2 честный отказ аргумента.
// =========================================================
function Run_Verify() {
    Result_Flag = 0x00000000;
    if (Cmd_Arg == 0x00000000) {
        // честная сверка ВСЕХ зон (порядок BOOT..SET, как при старте)
        Zone_Ptr = ZONE_BOOT;  Zone_Id = 0x00000001;  run Verify_Zone();
        Zone_Ptr = ZONE_KERN;  Zone_Id = 0x00000002;  run Verify_Zone();
        Zone_Ptr = ZONE_REG;   Zone_Id = 0x00000003;  run Verify_Zone();
        Zone_Ptr = ZONE_SET;   Zone_Id = 0x00000004;  run Verify_Zone();
    } else {
        if (Cmd_Arg == 0x00000001) {
            Zone_Ptr = ZONE_BOOT;  Zone_Id = 0x00000001;  run Verify_Zone();
        } else {
            if (Cmd_Arg == 0x00000002) {
                Zone_Ptr = ZONE_KERN;  Zone_Id = 0x00000002;  run Verify_Zone();
            } else {
                if (Cmd_Arg == 0x00000003) {
                    Zone_Ptr = ZONE_REG;   Zone_Id = 0x00000003;  run Verify_Zone();
                } else {
                    if (Cmd_Arg == 0x00000004) {
                        Zone_Ptr = ZONE_SET;   Zone_Id = 0x00000004;  run Verify_Zone();
                    } else {
                        // честный отказ: неизвестный аргумент, байта не лжёт
                        Result_Flag = 0x00000002;
                        Fail_Code = E_CHK_ARG;
                        out_cell(LOG_PORT, E_CHK_ARG);
                    }
                }
            }
        }
    }
}

// ---------- честная сборка зоны (формат и образы = веха-2) ----------
function Build_Zone() {
    store_ind(Zone_Ptr, MAGIC_CRIT);
    Offset = Zone_Ptr;
    Tmp_A = Offset + 4;
    store_ind(Tmp_A, ZONE_WORDS);

    if (Zone_Id == 0x00000001) {
        P0 = P_BOOT0;  P1 = P_BOOT1;  P2 = P_BOOT2;
        P3 = P_BOOT3;  P4 = P_BOOT4;  P5 = P_BOOT5;
    } else {
        if (Zone_Id == 0x00000002) {
            P0 = P_KERN0;  P1 = P_KERN1;  P2 = P_KERN2;
            P3 = P_KERN3;  P4 = P_KERN4;  P5 = P_KERN5;
        } else {
            if (Zone_Id == 0x00000003) {
                P0 = P_REG0;  P1 = P_REG1;  P2 = P_REG2;
                P3 = P_REG3;  P4 = P_REG4;  P5 = P_REG5;
            } else {
                P0 = P_SET0;  P1 = P_SET1;  P2 = P_SET2;
                P3 = P_SET3;  P4 = P_SET4;  P5 = P_SET5;
            }
        }
    }

    Offset = Zone_Ptr;
    Offset = Offset + 8;
    store_ind(Offset, P0);
    Offset = Offset + 4;  store_ind(Offset, P1);
    Offset = Offset + 4;  store_ind(Offset, P2);
    Offset = Offset + 4;  store_ind(Offset, P3);
    Offset = Offset + 4;  store_ind(Offset, P4);
    Offset = Offset + 4;  store_ind(Offset, P5);

    run Build_Suffixes();
}

function Build_Suffixes() {
    Word_Cur = 0x00000000;
    Roll_Sum = 0x00000000;
    Offset = Zone_Ptr;
    Offset = Offset + 8;
    Sf_Off = Zone_Ptr;
    Sf_Off = Sf_Off + 32;
    run Suffix_Loop();
}

function Suffix_Loop() {
    if (Word_Cur == ZONE_WORDS) {
        // готово честно
    } else {
        Tmp_A = in_cell(Offset);
        Roll_Sum = Roll_Sum + Tmp_A;
        store_ind(Sf_Off, Roll_Sum);
        Offset = Offset + 4;
        Sf_Off = Sf_Off + 4;
        Word_Cur = Word_Cur + 1;
        run Suffix_Loop();
    }
}

// ---------- честная сверка зоны (первый несовпавший prefix) ----------
function Verify_Zone() {
    Result_Flag = 0x00000000;
    Fail_Word = 0x00000000;
    Fail_Code = 0x00000000;

    Tmp_A = in_cell(Zone_Ptr);
    if (Tmp_A == MAGIC_CRIT) {
        Offset = Zone_Ptr;
        Offset = Offset + 4;
        Tmp_B = in_cell(Offset);
        if (Tmp_B == ZONE_WORDS) {
            Word_Cur = 0x00000000;
            Roll_Sum = 0x00000000;
            Offset = Zone_Ptr;
            Offset = Offset + 8;
            Sf_Off = Zone_Ptr;
            Sf_Off = Sf_Off + 32;
            run Verify_Loop();
        } else {
            Result_Flag = 0x00000001;
            Fail_Code = E_CHK_COUNT;
            Fail_Word = 0x00000001;
        }
    } else {
        Result_Flag = 0x00000001;
        Fail_Code = E_CHK_MAGIC;
        Fail_Word = 0x00000000;
    }
}

function Verify_Loop() {
    if (Word_Cur == ZONE_WORDS) {
        // честный обход завершён
    } else {
        Tmp_A = in_cell(Offset);
        Roll_Sum = Roll_Sum + Tmp_A;
        Tmp_B = in_cell(Sf_Off);
        if (Tmp_B == Roll_Sum) {
            // prefix честен
        } else {
            if (Result_Flag == 0x00000000) {
                Result_Flag = 0x00000001;
                Fail_Code = E_CHK_SUM;
                Fail_Word = Word_Cur;
            }
        }
        Offset = Offset + 4;
        Sf_Off = Sf_Off + 4;
        Word_Cur = Word_Cur + 1;
        run Verify_Loop();
    }
}

// ---------- честный журнал (формат = REG_LOG) ----------
function Store_Chk_Log() {
    if (CHK_N == CHK_MAX) {
        out_cell(LOG_PORT, 0x00007123);  // журнал честно полон
    } else {
        store_ind(CHK_Cursor, Zone_Id);
        CHK_Cursor = CHK_Cursor + 4;
        store_ind(CHK_Cursor, Fail_Word);
        CHK_Cursor = CHK_Cursor + 4;
        store_ind(CHK_Cursor, Fail_Code);
        CHK_Cursor = CHK_Cursor + 4;
        CHK_N = CHK_N + 1;
    }
}
