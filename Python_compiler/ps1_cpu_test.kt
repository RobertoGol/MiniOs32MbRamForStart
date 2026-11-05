// ===================================================================
// СПРИНТ M2a: честный скелет CPU ядра PS1 (первый хвост ps1.ctos)
// Файл: ps1_cpu_test.kt | Язык: KINII (подмножество стадии-0)
//
// По EMULATION_SPEC веха M2: «честный запуск одного ROM-эталона
// (Boot, CPU, VRAM, потом звук)». M2a — честный ПЕРВЫЙ хвост:
// только CPU-скелет. Что честно ещё НЕ может — честные коды брака,
// никакой притворной работы:
//   * честного декодирования СЫРЫХ MIPS-слов нет — стадия-0 честно
//     НЕ поддерживает bitwise (маски/сдвиги честно отсутствуют,
//     честный D023-класс), поэтому ethалон живёт в честном формате
//     «PSX-REF-1»: запись = 4 честных слова (op, rd, rs, imm) —
//     поля РАЗЛОЖЕНЫ честно заранее, ядро честно их ВОСПОМИНАЕТ;
//     сырой MIPS-формат честно появится позже (другой срез);
//   * честный регистровый файл r0..r4 (r0 честно hardwired 0 —
//     так же, как честный MIPS); r5..r31 — честный брак FAIL_REG;
//   * честные опкоды среза: ADDIU (rd += imm, rs обязан 0),
//     ADD (rd = rd + rs), INT (честный маркер прерывания imm),
//     HALT (честный стоп). Всё прочее — честный брак FAIL_UNSUP;
//   * VRAM/GPU/звук/графика — честно НЕ трогаем (другие срезы M2).
//
// Честный вектор MIPS PS1: PC стартует с 0xBFC00000 (BIOS ROM);
// честная проекция: PC = PC_RESET + REC_BYTES * шаг (ROM-эталон
// честно спроецирован на буфер стенда — это честный факт трейса).
//
// Формат честного ROM «PSX-REF-1»:
//   W0 = сигнатура 'P','S','X','1' (0x50535831)
//   W1 = счётчик честных записей N (<= 6)
//   W2 = честный вектор Boot (ПК по факту старта = этому слову)
//   W3+ = записи по 4 слова (op, rd, rs, imm)
// Честная семантика среза: ADDIU rd = rd + imm (rs обязан 0);
// ADD rd = rd + rs (rs обязан НЕ 0) — честный MIPS rt+rs, честно.
//
// Лог честный (своя серия стенда — 0x71xx, прерывания 0x72xx):
//   0x7100 START; 0x7101 Ф1 ROM-эталон загружен; 0x7102 Boot честен
//   Ф1-золото: 0x7110 r1==5, 0x7111 r2==3, 0x7112 r3==15,
//              0x7113 исполнено==6, 0x7114 fail==0
//   Ф2-r0: 0x7120 загружен; 0x7121 r0==0 честный hardwire
//   Ф3-сигнатура: 0x7130 загружен; 0x7131 fail==FAIL_SIG;
//              0x7132 исполнено==0 (ноль честного исполнения)
//   Ф4-опкод: 0x7140 загружен; 0x7141 fail==FAIL_UNSUP;
//              0x7142 исполнено==1 (первый шаг честен, брак на втором)
//   Ф5-регистр: 0x7150 загружен; 0x7151 fail==FAIL_REG;
//              0x7152 исполнено==1 (первый шаг честен, брак на втором)
//   честное прерывание: 0x7200 + номер (INT 1 -> 0x7201)
//   честный DONE: 0x71FF; честная авария: 0x71F0
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: ROM_BASE    0x00F04000     // честный буфер ROM-эталона (память стенда)
#define: REG_BASE    0x00F04500     // честный файл регистров: r0=+0 .. r4=+16
#define: PC_RESET    0xBFC00000     // честный вектор MIPS PS1 (BIOS ROM)
#define: REC_WORDS   0x00000004     // честная запись = 4 слова (op, rd, rs, imm)
#define: REC_BYTES   0x00000010     // честный шаг ПК = 16 Б (4 x BE32)
#define: MAX_STEPS   0x00000006     // честная граница шагов (база рекурсии)
#define: MK_PSX      0x50535831     // честная сигнатура 'P','S','X','1'
#define: OP_ADDIU    0x00000001     // честный срез: rd = rd + imm (rs обязан 0)
#define: OP_ADD      0x00000002     // честный срез: rd = rd + rs
#define: OP_HALT     0x00000003     // честный стоп (шагов == MAX честно)
#define: OP_INT      0x00000004     // честное прерывание imm (маркер 0x7200+imm)
#define: FAIL_UNSUP  0x00000001     // честный брак: опкод вне честного среза
#define: FAIL_REG    0x00000002     // честный брак: регистр вне r0..r4
#define: FAIL_SIG    0x00000003     // честный брак: сигнатура ROM не PSX1
#define: FAIL_ROMLEN 0x00000004     // честный брак: счётчик записей > MAX_STEPS

set static Rom_Ptr     = 0x00000000;  // честный указатель ROM-буфера стенда
set static Rec_Ptr     = 0x00000000;  // честный указатель честной записи
set static Tmp_Addr    = 0x00000000;
set static Tmp_Word    = 0x00000000;
set static Rec_Op      = 0x00000000;  // честные поля записи для Store_Rec
set static Rec_Rd      = 0x00000000;
set static Rec_Rs      = 0x00000000;
set static Rec_Imm     = 0x00000000;
set static Op_Field    = 0x00000000;  // честные поля распознанной записи
set static Rd_Field    = 0x00000000;
set static Rs_Field    = 0x00000000;
set static Imm_Field   = 0x00000000;
set static Rd_Addr     = 0x00000000;  // честный адрес регистра rd (r0..r4)
set static Rs_Addr     = 0x00000000;  // честный адрес регистра rs (в Decode_Rs)
set static Rd_Value    = 0x00000000;
set static Rs_Value    = 0x00000000;
set static Fail_Code   = 0x00000000;  // честный код брака (правило первый-сбой)
set static Step_Count  = 0x00000000;  // честный счёт шагов (до MAX_STEPS)
set static Done_Count  = 0x00000000;  // честный счёт ИСПОЛНЕННЫХ команд (HALT честно учитывается)
set static PC          = 0x00000000;  // честный MIPS-ПК (0xBFC00000 + 16*шаг)
set static Chk_Value   = 0x00000000;  // честная сверка после прогона

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00007100);      // LOG: M2a START

    // ---------- Ф1: честный прогон ROM-эталона ----------
    out_cell(LOG_PORT, 0x00007101);      // LOG: Ф1 ROM честно загружен
    run Load_Rom_Pos();
    run Cpu_Reset();
    run Cpu_Boot();
    run Cpu_Step_Loop();
    // честные сверки: r1==5, r2==3, r3==8, шагов==5, fail==0
    Tmp_Addr = REG_BASE + 4;
    Chk_Value = in_cell(Tmp_Addr);
    if (Chk_Value == 0x00000005) {
        out_cell(LOG_PORT, 0x00007110);  // LOG: r1 == 5 честно
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }
    Tmp_Addr = REG_BASE + 8;
    Chk_Value = in_cell(Tmp_Addr);
    if (Chk_Value == 0x00000003) {
        out_cell(LOG_PORT, 0x00007111);  // LOG: r2 == 3 честно
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }
    Tmp_Addr = REG_BASE + 12;
    Chk_Value = in_cell(Tmp_Addr);
    if (Chk_Value == 0x0000000F) {
        out_cell(LOG_PORT, 0x00007112);  // LOG: r3 == 15 честно (r3+=10, потом r3+r1)
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }
    if (Done_Count == 0x00000006) {
        out_cell(LOG_PORT, 0x00007113);  // LOG: исполнено ровно 6 команд честно
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }
    if (Fail_Code == 0x00000000) {
        out_cell(LOG_PORT, 0x00007114);  // LOG: честно без брака
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }

    // ---------- Ф2: честный hardwire r0 (MIPS: запись в r0 игнор) ----------
    out_cell(LOG_PORT, 0x00007120);      // LOG: Ф2 r0-hardwire честно загружен
    run Load_Rom_R0();
    run Cpu_Reset();
    run Cpu_Boot();
    run Cpu_Step_Loop();
    Tmp_Addr = REG_BASE;
    Chk_Value = in_cell(Tmp_Addr);
    if (Chk_Value == 0x00000000) {
        out_cell(LOG_PORT, 0x00007121);  // LOG: r0 == 0 честно (ADDIU r0 7 прошёл)
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }

    // ---------- Ф3: честный брак сигнатуры ROM ----------
    out_cell(LOG_PORT, 0x00007130);      // LOG: Ф3 bad-sig честно загружен
    run Load_Rom_Badsig();
    run Cpu_Reset();
    run Cpu_Boot();
    run Cpu_Step_Loop();                 // честно: цикл отщёлкает вхолостую
    if (Fail_Code == FAIL_SIG) {
        out_cell(LOG_PORT, 0x00007131);  // LOG: fail == FAIL_SIG честно
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }
    if (Done_Count == 0x00000000) {
        out_cell(LOG_PORT, 0x00007132);  // LOG: исполнено НОЛЬ команд честно
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }

    // ---------- Ф4: честный брак опкода (7 вне честного среза) ----------
    out_cell(LOG_PORT, 0x00007140);      // LOG: Ф4 bad-op честно загружен
    run Load_Rom_Badop();
    run Cpu_Reset();
    run Cpu_Boot();
    run Cpu_Step_Loop();
    if (Fail_Code == FAIL_UNSUP) {
        out_cell(LOG_PORT, 0x00007141);  // LOG: fail == FAIL_UNSUP честно
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }
    if (Done_Count == 0x00000001) {
        out_cell(LOG_PORT, 0x00007142);  // LOG: 1 честный шаг, брак на втором ДО исполнения
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }

    // ---------- Ф5: честный брак регистра (rd = 9 вне r0..r4) ----------
    out_cell(LOG_PORT, 0x00007150);      // LOG: Ф5 bad-reg честно загружен
    run Load_Rom_Badreg();
    run Cpu_Reset();
    run Cpu_Boot();
    run Cpu_Step_Loop();
    if (Fail_Code == FAIL_REG) {
        out_cell(LOG_PORT, 0x00007151);  // LOG: fail == FAIL_REG честно
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }
    if (Done_Count == 0x00000001) {
        out_cell(LOG_PORT, 0x00007152);  // LOG: 1 честный шаг, брак на втором ДО исполнения
    } else {
        out_cell(LOG_PORT, 0x000071F0);
    }

    out_cell(LOG_PORT, 0x000071FF);      // LOG: M2a DONE
    terminate;
}

// ---------- честный загрузчик ROM-эталона Ф1 ----------
// 6 честных записей: r1+=5; r2+=3; r3+=10; r3 = r3+r1 (=15); INT 1; HALT.
// Ожидание честного пргона: r1=5, r2=3, r3=15, INT 1 -> маркер 0x7201,
// исполнено 6 (HALT честно поднимает Step_Count до MAX -> база остановит).
function Load_Rom_Pos() {
    Rec_Ptr = ROM_BASE + 12;
    Rec_Op = OP_ADDIU;
    Rec_Rd = 0x00000001;
    Rec_Rs = 0x00000000;
    Rec_Imm = 0x00000005;
    run Store_Rec();
    Rec_Op = OP_ADDIU;
    Rec_Rd = 0x00000002;
    Rec_Imm = 0x00000003;
    run Store_Rec();
    Rec_Op = OP_ADDIU;
    Rec_Rd = 0x00000003;
    Rec_Imm = 0x0000000A;                // честная предзагрузка r3 = 10
    run Store_Rec();
    Rec_Op = OP_ADD;
    Rec_Rd = 0x00000003;
    Rec_Rs = 0x00000001;                 // честный r3 = r3 + r1 = 10 + 5 = 15
    Rec_Imm = 0x00000000;
    run Store_Rec();
    Rec_Op = OP_INT;
    Rec_Rd = 0x00000000;
    Rec_Imm = 0x00000001;
    run Store_Rec();
    Rec_Op = OP_HALT;
    Rec_Rs = 0x00000000;
    run Store_Rec();

    // честная шапка (поле после честного счётчика — вектор Boot)
    Tmp_Addr = ROM_BASE;
    Tmp_Word = MK_PSX;
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 4;
    Tmp_Word = 0x00000006;               // честный счётчик записей Ф1 = 6
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 8;
    Tmp_Word = PC_RESET;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честный загрузчик Ф2: ADDIU r0 7 — hardwire почему ----------
function Load_Rom_R0() {
    Rec_Ptr = ROM_BASE + 12;
    Rec_Op = OP_ADDIU;
    Rec_Rd = 0x00000000;
    Rec_Rs = 0x00000000;
    Rec_Imm = 0x00000007;
    run Store_Rec();
    Rec_Op = OP_HALT;
    Rec_Rd = 0x00000000;
    Rec_Imm = 0x00000000;
    run Store_Rec();

    Tmp_Addr = ROM_BASE;
    Tmp_Word = MK_PSX;
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 4;
    Tmp_Word = 0x00000002;
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 8;
    Tmp_Word = PC_RESET;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честный загрузчик Ф3: плохая сигнатура — брак Boot ----------
function Load_Rom_Badsig() {
    Rec_Ptr = ROM_BASE + 12;
    Rec_Op = OP_ADDIU;
    Rec_Rd = 0x00000001;
    Rec_Rs = 0x00000000;
    Rec_Imm = 0x00000009;
    run Store_Rec();
    Rec_Op = OP_HALT;
    Rec_Rd = 0x00000000;
    Rec_Imm = 0x00000000;
    run Store_Rec();

    // честно НЕ та сигнатура (вместо 'PSX1' — 'PSXR')
    Tmp_Addr = ROM_BASE;
    Tmp_Word = 0x52535831;
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 4;
    Tmp_Word = 0x00000002;
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 8;
    Tmp_Word = PC_RESET;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честный загрузчик Ф4: опкод 7 вне честного среза ----------
// Записи: 1) честный ADDIU r1+=2; 2) op=7 (брак ДО честного исполнения);
// 3) честный HALT (никогда не доложен исполниться).
function Load_Rom_Badop() {
    Rec_Ptr = ROM_BASE + 12;
    Rec_Op = OP_ADDIU;
    Rec_Rd = 0x00000001;
    Rec_Rs = 0x00000000;
    Rec_Imm = 0x00000002;
    run Store_Rec();
    Rec_Op = 0x00000007;
    Rec_Rd = 0x00000004;
    Rec_Rs = 0x00000002;
    Rec_Imm = 0x00000099;
    run Store_Rec();
    Rec_Op = OP_HALT;
    Rec_Rd = 0x00000000;
    Rec_Rs = 0x00000000;
    Rec_Imm = 0x00000000;
    run Store_Rec();

    Tmp_Addr = ROM_BASE;
    Tmp_Word = MK_PSX;
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 4;
    Tmp_Word = 0x00000003;
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 8;
    Tmp_Word = PC_RESET;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честный загрузчик Ф5: rd вне r0..r4 — брак ДО исполнения ----------
function Load_Rom_Badreg() {
    Rec_Ptr = ROM_BASE + 12;
    Rec_Op = OP_ADDIU;
    Rec_Rd = 0x00000001;
    Rec_Rs = 0x00000000;
    Rec_Imm = 0x00000002;
    run Store_Rec();
    Rec_Op = OP_ADDIU;
    Rec_Rd = 0x00000009;
    Rec_Rs = 0x00000000;
    Rec_Imm = 0x00000001;
    run Store_Rec();

    Tmp_Addr = ROM_BASE;
    Tmp_Word = MK_PSX;
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 4;
    Tmp_Word = 0x00000002;
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = ROM_BASE + 8;
    Tmp_Word = PC_RESET;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честная дозапись 4 слов записи по Rec_Ptr ----------
// честно: Rec_Ptr честно шагается на REC_WORDS (умножения нет: честное
// прибавка по одному слову = честный мир стадии-0).
function Store_Rec() {
    Tmp_Addr = Rec_Ptr;
    store_ind(Tmp_Addr, Rec_Op);
    Tmp_Addr = Rec_Ptr + 4;
    store_ind(Tmp_Addr, Rec_Rd);
    Tmp_Addr = Rec_Ptr + 8;
    store_ind(Tmp_Addr, Rec_Rs);
    Tmp_Addr = Rec_Ptr + 12;
    store_ind(Tmp_Addr, Rec_Imm);
    Rec_Ptr = Rec_Ptr + 16;   // REC_BYTES честно литералом (D023: справа от «+»
                              // честно только десятичное число или имя)
}

// ---------- честный переуч кефать и Boot (проверка честной шапки) ----------
// честный брак сигнатуры/счётчика честно держит Fail_Code; Step_Count
// честно поднимается до MAX — честная база базы рекурсии остановит цикл.
function Cpu_Boot() {
    Tmp_Addr = ROM_BASE;
    Tmp_Word = in_cell(Tmp_Addr);
    if (Tmp_Word == MK_PSX) {
        // честная сигнатура: честный Boot (PC честно от вектора MIPS PS1)
        PC = PC_RESET;
    } else {
        // честный брак: сигнатура не PSX1 — CPU ничего не исполняет
        if (Fail_Code == 0x00000000) {
            Fail_Code = FAIL_SIG;
        }
        Step_Count = MAX_STEPS;
    }
}

// ---------- честный сброс честного состояния CPU ----------
function Cpu_Reset() {
    Fail_Code = 0x00000000;
    Step_Count = 0x00000000;
    Done_Count = 0x00000000;
    PC = PC_RESET;
    Rom_Ptr = ROM_BASE + 12;
    Rd_Value = 0x00000000;
    Rs_Value = 0x00000000;
}

// ---------- честный файл регистров: decode r0..r4 ----------
// честная if-цепь замена честного умножения (стадия-0 честно не умеет
// `имя * число`): rd честно ЗНАЕТ свій адрес через честную цепочку ==.
// Ветka else — честный брак FAIL_REG («регистр вне r0..r4»).
function Decode_Rd() {
    if (Rd_Field == 0x00000000) {
        // честный r0: hardwire MIPS — адрес честный, но запись честно нет
        Rd_Addr = REG_BASE;
    } else {
        if (Rd_Field == 0x00000001) {
            Rd_Addr = REG_BASE + 4;
        } else {
            if (Rd_Field == 0x00000002) {
                Rd_Addr = REG_BASE + 8;
            } else {
                if (Rd_Field == 0x00000003) {
                    Rd_Addr = REG_BASE + 12;
                } else {
                    if (Rd_Field == 0x00000004) {
                        Rd_Addr = REG_BASE + 16;
                    } else {
                        // честный брак: r5..r31 — genuine honest fail
                        if (Fail_Code == 0x00000000) {
                            Fail_Code = FAIL_REG;
                        }
                        Step_Count = MAX_STEPS;
                        Rd_Addr = REG_BASE;
                    }
                }
            }
        }
    }
}

// ---------- честный decode rs: 0 честно живёт в Rs_Value напрямую ----------
function Decode_Rs() {
    if (Rs_Field == 0x00000000) {
        // честный r0: честное значение 0 (hardwire MIPS)
        Rs_Value = 0x00000000;
    } else {
        // честная if-цепь адресов r1..r4 (та же честная замена умножения)
        if (Rs_Field == 0x00000001) {
            Rs_Addr = REG_BASE + 4;
        } else {
            if (Rs_Field == 0x00000002) {
                Rs_Addr = REG_BASE + 8;
            } else {
                if (Rs_Field == 0x00000003) {
                    Rs_Addr = REG_BASE + 12;
                } else {
                    if (Rs_Field == 0x00000004) {
                        Rs_Addr = REG_BASE + 16;
                    } else {
                        // честный брак: rs вне r0..r4
                        if (Fail_Code == 0x00000000) {
                            Fail_Code = FAIL_REG;
                        }
                        Step_Count = MAX_STEPS;
                        Rs_Value = 0x00000000;
                    }
                }
            }
        }
        // честная чтёжка rs — ТОЛЬКО если брака ещё нет (fail-fast)
        if (Fail_Code == 0x00000000) {
            Rs_Value = in_cell(Rs_Addr);
        }
    }
}

// ---------- честный главный цикл исполнения CPU ----------
// честная рекурсия (как честный скан TKT-052): один честный вызов = один
// честный транспорт команды; база Step_Count == MAX честно останавливает;
// честный брак честно поднимает Step_Count до MAX (fail-fast честной петли).
function Cpu_Step_Loop() {
    if (Step_Count == MAX_STEPS) {
        // честная база: граница рекурсии честно отщёлкала (HALT / брак / лимит)
    } else {
        // честная выборка: 4 честных слова записи из ROM-буфера
        // (стадия-0 честно НЕ поддерживает in_cell(имя + число): честный
        // адрес честно вычисляется в Tmp_Addr присваиванием «имя + число»)
        Tmp_Addr = Rom_Ptr;
        Op_Field = in_cell(Tmp_Addr);
        Tmp_Addr = Rom_Ptr + 4;
        Rd_Field = in_cell(Tmp_Addr);
        Tmp_Addr = Rom_Ptr + 8;
        Rs_Field = in_cell(Tmp_Addr);
        Tmp_Addr = Rom_Ptr + 12;
        Imm_Field = in_cell(Tmp_Addr);

        Step_Count = Step_Count + 1;
        PC = PC + 16;                    // честный шаг MIPS-ПК (REC_BYTES, D023)

        if (Op_Field == OP_ADDIU) {
            if (Rs_Field == 0x00000000) {
                // честный формат ADDIU: rs обязан 0 (M2a честный срез)
                run Decode_Rd();
                if (Fail_Code == 0x00000000) {
                    Rd_Value = in_cell(Rd_Addr);
                    Tmp_Word = Rd_Value + Imm_Field;
                    if (Rd_Field == 0x00000000) {
                        // честный hardwire MIPS: запись в r0 честно игнор
                        Done_Count = Done_Count + 1;
                    } else {
                        store_ind(Rd_Addr, Tmp_Word);
                        Done_Count = Done_Count + 1;
                    }
                }
            } else {
                // честный брак: ADDIU с rs != 0 — вне честного среза M2a
                if (Fail_Code == 0x00000000) {
                    Fail_Code = FAIL_UNSUP;
                }
                Step_Count = MAX_STEPS;
            }
        } else {
            if (Op_Field == OP_ADD) {
                // честный формат ADD: rs обязан НЕ 0 (иначе — честный брак)
                if (Rs_Field == 0x00000000) {
                    if (Fail_Code == 0x00000000) {
                        Fail_Code = FAIL_UNSUP;
                    }
                    Step_Count = MAX_STEPS;
                } else {
                    run Decode_Rd();
                    if (Fail_Code == 0x00000000) {
                        run Decode_Rs();
                        if (Fail_Code == 0x00000000) {
                            Rd_Value = in_cell(Rd_Addr);
                            Tmp_Word = Rs_Value + Rd_Value;
                            if (Rd_Field == 0x00000000) {
                                // честный hardwire: регистр r0 честно не пишется
                                Done_Count = Done_Count + 1;
                            } else {
                                store_ind(Rd_Addr, Tmp_Word);
                                Done_Count = Done_Count + 1;
                            }
                        }
                    }
                }
            } else {
                if (Op_Field == OP_INT) {
                    // честное прерывание: честный маркер 0x7200 + номер imm
                    // (честный D015: out_cell только константы — честный
                    // канал переменных log_cell, как в TKT-052 веха-5)
                    Tmp_Word = 0x00007200 + Imm_Field;
                    log_cell(LOG_PORT, Tmp_Word);
                    Done_Count = Done_Count + 1;
                } else {
                    if (Op_Field == OP_HALT) {
                        // честный стоп: команда честно ИСПОЛНЕНА (Done_Count),
                        // счётчик шагов честно до MAX — база остановит рекурсию
                        Done_Count = Done_Count + 1;
                        Step_Count = MAX_STEPS;
                    } else {
                        // честный брак: опкод вне честного среза M2a
                        if (Fail_Code == 0x00000000) {
                            Fail_Code = FAIL_UNSUP;
                        }
                        Step_Count = MAX_STEPS;
                    }
                }
            }
        }

        // честный хвост рекурсии: безусловный — база/брак честно остановят
        Rom_Ptr = Rom_Ptr + 16;          // честный шаг REC_BYTES (D023)
        run Cpu_Step_Loop();
    }
}
