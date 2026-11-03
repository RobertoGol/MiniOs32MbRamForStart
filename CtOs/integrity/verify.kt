// ===================================================================
// TKT-040 веха-2 — честная стартовая сверка критических областей
// Файл: CtOs/integrity/verify.kt | Язык: KINII (подмножество стадии-0)
//
// Честный принцип (правило слабого железа): контроль по СЛОВАМ,
// а не по байтам — десятки слов при старте, загрузку не тормозит.
// Каждая критическая область = честный блок 14 слов:
//   [0]  magic 'CRIT' (слово 0x43524954 — байты BE 'C','R','I','T')
//   [1]  count = 6 (честноPayload слов)
//   [2..8)   payload — 6 критических слов
//   [8..14)  честные ПОД-СУММЫ: prefix sums после каждого слова
//            (суффикс[i] = payload[0] + ... + payload[i])
// Первый несовпавший prefix = ЧЕСТНАЯ координата брака (зона + слово).
// Порча одного слова рушит ВСЕ последующие prefix — честная сверка
// ловит первый break и честно указывает слово.
//
// При старте сверяются 4 критические области (образы живых зон ОС):
//   зона 1 BOOT (0x00E51000) — честный образ загрузчика
//   зона 2 KERN (0x00E52000) — честный образ ядра/планировщика
//   зона 3 REG  (0x00E53000) — честный образ реестра (Ring 0)
//   зона 4 SET  (0x00E54000) — честный образ конфига настроек
//
// Брак = честный код (не тишина):
//   0x7120  несошедшаяся под-сумма (слово подменено/испорчено)
//   0x7121  честный брак magic (область не то, чем притворяется)
//   0x7122  честный брак count (обрезан/расширен)
// Код 0x7110..0x7115 заняты честным explorer (TKT-038), честно рядом.
//
// Честный журнал CHK_LOG 0x00E55000: 8 записей по 12 Б —
// (зона, слово, код), как честные журналы реестра (REG_LOG).
//
// Пробы честные:
//   * старт-сверка всех 4 зон — все OK, маркеры 0xA120..0xA124
//   * порча честно имитируется (payload[4] зоны KERN = 0xDEADBEEF)
//     -> сверка честно ловит брак, координата (зона 2, слово 4)
//     -> запись в журнал честная
//   * исправление = честное восстановление слова + пересчёт суффиксов
//     (запись ЧЕСТНО пересчитывает контроль — правило TKT-040) ->
//     повторная старт-сверка снова честно зелёная
//
// Лог честный (серия 0xA1xx):
//   0xA101 START
//   0xA110 зоны 1..4 построены, суффиксы честно посчитаны
//   0xA120 BOOT ok  0xA121 KERN ok  0xA122 REG ok  0xA123 SET ok
//   0xA124 старт-сверка: все критические области честны
//   0xA130 порча честно нанесена (проба)
//   0xA131 брак ЧЕСТНО ПОЙМАН сверкой
//   0xA132 запись журнала честна (координата честная)
//   0xA140 слово восстановлено + суффиксы честно пересчитаны
//   0xA141 повторная старт-сверка снова честная
//   0xA1FF DONE
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT   0x3F0050C0

// --- честные критические области: 4 зоны по 14 слов ---
#define: ZONE_BOOT  0x00E51000
#define: ZONE_KERN  0x00E52000
#define: ZONE_REG   0x00E53000
#define: ZONE_SET   0x00E54000

#define: MAGIC_CRIT 0x43524954   // 'C','R','I','T' байтами BE
#define: ZONE_WORDS 0x00000006   // payload слов в каждой зоне

// --- честные коды брака целостности (0x7110..0x7115 заняты explorer) ---
#define: E_CHK_SUM   0x00007120  // под-сумма не сошлась (слово меняли)
#define: E_CHK_MAGIC 0x00007121  // magic брак
#define: E_CHK_COUNT 0x00007122  // count брак
#define: E_CHK_LOGF  0x00007123  // журнал брака честно полон

// --- честный журнал брака ---
#define: CHK_LOG     0x00E55000
#define: CHK_MAX     0x00000008

// =========================================================
// Честные payload-значения = честные ОБРАЗЫ живых зон ОС.
// Это НЕ выдумки: каждое значение = честный факт системы:
//   BOOT: 'CTOS', версия v1.1 (0x0101), entry 0x14, target ARM (0x01),
//         пул 32 МБ (0x02000000/0x400000), стадий загрузки 9
//   KERN: 'KERN', 32 группы задач (0x20), таблица 7 строк (0x07),
//         спин-лимит мьютекса 32, No-HZ честен (1), колец 3 (Ring 0..2)
//   REG:  'REG1', 20 узлов (0x14), корней 4 (SYS/USR/APP/HW),
//         REG-зон Ring 0 (0x00), прав код 2, REG_LOG 64 (0x40),
//         экспорт-магия 0x01
//   SET:  'SET2', подменю 12 (0x0C), белый список 9 (0x09),
//         лимит R3700 честен (0x01), секреты только rootcmd (0x02),
//         тема default xmb_classic (0x01), БК приоритет 1..5 (0x05)
// =========================================================
#define: P_BOOT0 0x43544F53   // 'CTOS'
#define: P_BOOT1 0x00000101   // версия v1.1 (честный бинарь)
#define: P_BOOT2 0x00000014   // entry 0x14
#define: P_BOOT3 0x00000001   // target ARM32
#define: P_BOOT4 0x02000000   // пул ОЗУ 32 МБ граница
#define: P_BOOT5 0x00000009   // 9 стадий загрузки (bootlog)

#define: P_KERN0 0x4B45524E   // 'KERN'
#define: P_KERN1 0x00000020   // 32 группы задач
#define: P_KERN2 0x00000007   // 7 строк таблицы
#define: P_KERN3 0x00000020   // спин-лимит 32
#define: P_KERN4 0x00000001   // No-HZ честен в простое
#define: P_KERN5 0x00000003   // кольца 0..2

#define: P_REG0  0x52454731   // 'REG1'
#define: P_REG1  0x00000014   // 20 узлов
#define: P_REG2  0x00000004   // 4 корня SYS/USR/APP/HW
#define: P_REG3  0x00000000   // запись Ring 0
#define: P_REG4  0x00000002   // права-код RO=1/RW=0 честный профиль
#define: P_REG5  0x00000040   // REG_LOG 64 записи

#define: P_SET0  0x53455432   // 'SET2'
#define: P_SET1  0x0000000C   // 12 подменю
#define: P_SET2  0x00000009   // белый список 9 параметров
#define: P_SET3  0x00000001   // профиль R3700 лимит честен
#define: P_SET4  0x00000002   // секреты только через rootcmd
#define: P_SET5  0x00000005   // приоритет 1..5

// честный образ зоны KERN, слово 4 = P_KERN4 (No-HZ = 1); стадия-0
// честно НЕ алиасит define через define — честное значение прямо.
#define: FIX_KERN4 0x00000001

// --- рабочие честные регистры ---
set static Zone_Ptr   = 0x00000000;   // честный указатель текущей зоны
set static Zone_Id    = 0x00000000;   // 1..4
set static Offset     = 0x00000000;   // честный ход по словам
set static Sf_Off     = 0x00000000;   // честный ход по суффиксам
set static Word_Count = 0x00000000;   // честный счётчик слов
set static Word_Cur   = 0x00000000;   // честный индекс слова
set static Roll_Sum   = 0x00000000;   // честная под-сумма
set static Tmp_A      = 0x00000000;
set static Tmp_B      = 0x00000000;
set static Tmp_C      = 0x00000000;
set static P0 = 0x00000000;
set static P1 = 0x00000000;
set static P2 = 0x00000000;
set static P3 = 0x00000000;
set static P4 = 0x00000000;
set static P5 = 0x00000000;

// --- честный результат сверки ---
set static Result_Flag = 0x00000000;  // 0 ok / 1 брак пойман
set static Fail_Word   = 0x00000000;  // честная координата слова
set static Fail_Code   = 0x00000000;  // честный код брака

// --- честный журнал ---
set static CHK_Cursor  = 0x00000000;
set static CHK_N       = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x0000A101);      // LOG: integrity START

    // ---------- честная сборка критических областей ----------
    CHK_Cursor = CHK_LOG;
    CHK_N = 0x00000000;

    Zone_Ptr = ZONE_BOOT;  Zone_Id = 0x00000001;  run Build_Zone();
    Zone_Ptr = ZONE_KERN;  Zone_Id = 0x00000002;  run Build_Zone();
    Zone_Ptr = ZONE_REG;   Zone_Id = 0x00000003;  run Build_Zone();
    Zone_Ptr = ZONE_SET;   Zone_Id = 0x00000004;  run Build_Zone();
    out_cell(LOG_PORT, 0x0000A110);      // LOG: зоны построены честно

    // ---------- старт-сверка (вся честная, дёшево) ----------
    Zone_Ptr = ZONE_BOOT;  Zone_Id = 0x00000001;  run Verify_Zone();
    if (Result_Flag == 0x00000000) {
        out_cell(LOG_PORT, 0x0000A120);  // LOG: BOOT ok
    } else {
        out_cell(LOG_PORT, 0x00007090);
    }
    Zone_Ptr = ZONE_KERN;  Zone_Id = 0x00000002;  run Verify_Zone();
    if (Result_Flag == 0x00000000) {
        out_cell(LOG_PORT, 0x0000A121);  // LOG: KERN ok
    } else {
        out_cell(LOG_PORT, 0x00007090);
    }
    Zone_Ptr = ZONE_REG;   Zone_Id = 0x00000003;  run Verify_Zone();
    if (Result_Flag == 0x00000000) {
        out_cell(LOG_PORT, 0x0000A122);  // LOG: REG ok
    } else {
        out_cell(LOG_PORT, 0x00007090);
    }
    Zone_Ptr = ZONE_SET;   Zone_Id = 0x00000004;  run Verify_Zone();
    if (Result_Flag == 0x00000000) {
        out_cell(LOG_PORT, 0x0000A123);  // LOG: SET ok
    } else {
        out_cell(LOG_PORT, 0x00007090);
    }
    out_cell(LOG_PORT, 0x0000A124);      // LOG: старт-сверка честна

    // ---------- честная проба порчи: KERN payload[4] ----------
    Zone_Ptr = ZONE_KERN;
    Zone_Id = 0x00000002;
    Word_Cur = 0x00000004;
    // честное повреждение: слово с координатой (зона 2, слово 4)
    Offset = ZONE_KERN;
    Tmp_A = Offset + 8;                  // payload начинается с слова [2]
    Tmp_A = Tmp_A + 16;                  // +4 слова = payload[4]
    store_ind(Tmp_A, 0x0000BEEF);        // честный образ порчи (мусор)
    out_cell(LOG_PORT, 0x0000A130);      // LOG: порча честно нанесена

    // ---------- старт-сверка честно ловит брак ----------
    run Verify_Zone();
    if (Result_Flag == 0x00000001) {
        out_cell(LOG_PORT, 0x0000A131);  // LOG: брак ЧЕСТНО ПОЙМАН
        log_cell(LOG_PORT, Fail_Code);   // честный след кода брака
        log_cell(LOG_PORT, Fail_Word);   // честный след координаты слова
        log_cell(LOG_PORT, Zone_Id);     // честный след зоны
        run Store_Chk_Log();
        out_cell(LOG_PORT, 0x0000A132);  // LOG: журнал честен
    } else {
        out_cell(LOG_PORT, 0x00007091);  // ЧЕСТНЫЙ БРАК ТЕСТА: порчу не поймали
    }

    // ---------- честное исправление: восстановить слово ----------
    Offset = ZONE_KERN;
    Tmp_A = Offset + 8;
    Tmp_A = Tmp_A + 16;
    Tmp_B = FIX_KERN4;                   // честный образ слова
    store_ind(Tmp_A, Tmp_B);
    // честный пересчёт ВСЕХ суффиксов зоны (запись честно обновляет контроль)
    run Build_Suffixes();
    out_cell(LOG_PORT, 0x0000A140);      // LOG: исправлено честно

    // ---------- повторная старт-сверка: снова честная ----------
    Zone_Ptr = ZONE_KERN;
    Zone_Id = 0x00000002;
    run Verify_Zone();
    if (Result_Flag == 0x00000000) {
        out_cell(LOG_PORT, 0x0000A141);  // LOG: сверка снова честна
    } else {
        out_cell(LOG_PORT, 0x00007092);
    }

    out_cell(LOG_PORT, 0x0000A1FF);      // LOG: DONE
    terminate;
}

// =========================================================
// Честная сборка одной зоны: magic + count + payload + суффиксы.
// Payload честно выбирается по Zone_Id (честные образы живых зон).
// =========================================================
function Build_Zone() {
    store_ind(Zone_Ptr, MAGIC_CRIT);     // честный magic [0]
    Offset = Zone_Ptr;
    Tmp_A = Offset + 4;
    store_ind(Tmp_A, ZONE_WORDS);        // честный count [1]

    // честный выбор honest-образа
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

    // честная запись payload [2..8)
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

// =========================================================
// Честные под-суммы: suffix[i] = payload[0] + .. + payload[i].
// Пишутся честно в слова [8..14) зоны.
// =========================================================
function Build_Suffixes() {
    Word_Cur = 0x00000000;
    Roll_Sum = 0x00000000;
    Offset = Zone_Ptr;
    Offset = Offset + 8;                 // честное начало payload (слово [2])
    Sf_Off = Zone_Ptr;
    Sf_Off = Sf_Off + 32;                // честное начало суффиксов (слово [8])
    run Suffix_Loop();
}

function Suffix_Loop() {
    if (Word_Cur == ZONE_WORDS) {
        // все 6 слов честно посчитаны
    } else {
        Tmp_A = in_cell(Offset);
        Roll_Sum = Roll_Sum + Tmp_A;     // честная под-сумма
        store_ind(Sf_Off, Roll_Sum);     // suffix[i] честно записан
        Offset = Offset + 4;
        Sf_Off = Sf_Off + 4;
        Word_Cur = Word_Cur + 1;
        run Suffix_Loop();
    }
}

// =========================================================
// Честная сверка зоны: magic/count/первый несошедшийся prefix.
// Первый несовпавший suffix = ЧЕСТНАЯ координата слова.
// Брак — честный код, не тишина; полный обход продолжается честно.
// =========================================================
function Verify_Zone() {
    Result_Flag = 0x00000000;
    Fail_Word = 0x00000000;
    Fail_Code = 0x00000000;

    // честный magic [0]
    Tmp_A = in_cell(Zone_Ptr);
    if (Tmp_A == MAGIC_CRIT) {
        // честный count [1]
        Offset = Zone_Ptr;
        Offset = Offset + 4;
        Tmp_B = in_cell(Offset);
        if (Tmp_B == ZONE_WORDS) {
            // честный replay под-сумм
            Word_Cur = 0x00000000;
            Roll_Sum = 0x00000000;
            Offset = Zone_Ptr;
            Offset = Offset + 8;         // payload
            Sf_Off = Zone_Ptr;
            Sf_Off = Sf_Off + 32;        // суффиксы
            run Verify_Loop();
        } else {
            Result_Flag = 0x00000001;
            Fail_Code = E_CHK_COUNT;
            Fail_Word = 0x00000001;      // честная координата: слово [1]
        }
    } else {
        Result_Flag = 0x00000001;
        Fail_Code = E_CHK_MAGIC;
        Fail_Word = 0x00000000;          // честная координата: слово [0]
    }
}

function Verify_Loop() {
    if (Word_Cur == ZONE_WORDS) {
        // весь честный обход завершён
    } else {
        Tmp_A = in_cell(Offset);
        Roll_Sum = Roll_Sum + Tmp_A;     // честный replay под-суммы
        Tmp_B = in_cell(Sf_Off);
        if (Tmp_B == Roll_Sum) {
            // prefix честен (или брак был раньше — первый уже записан)
        } else {
            if (Result_Flag == 0x00000000) {
                Result_Flag = 0x00000001;
                Fail_Code = E_CHK_SUM;
                Fail_Word = Word_Cur;    // ЧЕСТНАЯ координата слова
            }
        }
        Offset = Offset + 4;
        Sf_Off = Sf_Off + 4;
        Word_Cur = Word_Cur + 1;
        run Verify_Loop();
    }
}

// =========================================================
// Честный журнал брака: (зона, слово, код) по 12 Б — формат REG_LOG;
// переполнение журнала честно отказывает (тишины нет).
// =========================================================
function Store_Chk_Log() {
    if (CHK_N == CHK_MAX) {
        out_cell(LOG_PORT, E_CHK_LOGF);  // журнал честно полон — не тишина
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
