// ===================================================================
// TKT-056 / memory path: честный менеджер памяти с привязкой к задаче
// Файл: CtOs/memmgr.kt | Язык: KINII (стадия-0, самотестируемый модуль)
//
// Поверх правила memory.ctos + SCHED_SPEC §4 (Zeroize-Exit):
//   * Выдача ячеек с честной привязкой (addr, tid) в журнале.
//   * Mem_Free: вычёркивание пары + честный zeroize ячейки + RW-компакт.
//   * Mem_Zeroize_Task: при выходе задачи (ZOMBIE) — обнулить ВСЕ недо-
//     возвращённые ячейки владельца tid и вычеркнуть пары. Утечка одной
//     задачи не убивает систему; leaked честно виден в логе.
//   * Честные границы: HEAP_END / LEDGER полон -> отказ (0xA79x), без panic.
//
// Карта (Ring 2, не пересекается с BOOT_LOG 0x00E30000+, SCHED 0x00A10000+,
//          SYSINFO/PANIC 0x00E31000+):
//   0x00E20000  HEAP_BASE   bump-область (ячейки по 4 Б)
//   0x00E21000  HEAP_END    честный предел heap
//   0x00E21000  MEM_LEDGER  16 пар (addr, tid) = 128 Б
//   0x00E21080  RW_ADDR     16 слов (компакт)
//   0x00E210C0  RW_TID      16 слов (компакт)
//
// Маркеры: 0xA7xx (memmgr), 0x99Ax BAD.
// Честно: стадия-0 без */; индексация — +4 шаги; рекурсия для циклов.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0

#define: HEAP_BASE   0x00E20000
#define: HEAP_END    0x00E21000
#define: MEM_LEDGER  0x00E21000
#define: LEDGER_MAX  0x00000010
#define: RW_ADDR     0x00E21080
#define: RW_TID      0x00E210C0

#define: E_HEAP      0x0000A791
#define: E_LEDGER    0x0000A792

set static Heap_Run      = 0x00000000;
set static Ledger_Run    = 0x00000000;
set static Ledger_Count  = 0x00000000;

set static Mem_Tid       = 0x00000000;   // вход: владелец
set static Mem_Addr      = 0x00000000;   // вход/выход: адрес ячейки
set static Mem_Fail      = 0x00000000;   // 0=OK, иначе E_*

set static Scan_Idx      = 0x00000000;
set static RW_Count      = 0x00000000;
set static RW_A_Run      = 0x00000000;
set static RW_T_Run      = 0x00000000;
set static Scan_Ledger   = 0x00000000;
set static Read_Addr     = 0x00000000;
set static Read_Tid      = 0x00000000;
set static Leaked_Count  = 0x00000000;
set static Tmp_A         = 0x00000000;
set static Tmp_B         = 0x00000000;
set static Tmp_C         = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x0000A701);      // START memmgr

    run Mem_Init();
    run Test_Init();

    run Test_Alloc_Free();
    run Test_Zeroize_Exit();
    run Test_Bounds();

    out_cell(LOG_PORT, 0x0000A7FF);      // DONE
    terminate;
}

// ---------- init ----------
function Mem_Init() {
    Heap_Run = HEAP_BASE;
    Ledger_Run = MEM_LEDGER;
    Ledger_Count = 0x00000000;
    Mem_Fail = 0x00000000;
}

function Test_Init() {
    if (Ledger_Count == 0x00000000) {
        if (Heap_Run == HEAP_BASE) {
            out_cell(LOG_PORT, 0x0000A710);  // init OK
        } else {
            out_cell(LOG_PORT, 0x000099A1);
        }
    } else {
        out_cell(LOG_PORT, 0x000099A2);
    }
}

// ---------- alloc: Mem_Tid -> Mem_Addr (или Mem_Fail) ----------
function Mem_Alloc() {
    Mem_Fail = 0x00000000;
    Mem_Addr = 0x00000000;
    if (Ledger_Count == LEDGER_MAX) {
        Mem_Fail = E_LEDGER;
        out_cell(LOG_PORT, 0x0000A792);      // ledger full (info)
    } else {
        if (Heap_Run == HEAP_END) {
            Mem_Fail = E_HEAP;
            out_cell(LOG_PORT, 0x0000A791);  // heap end (info)
        } else {
            Mem_Addr = Heap_Run;
            Heap_Run = Heap_Run + 4;
            store_ind(Ledger_Run, Mem_Addr);
            Ledger_Run = Ledger_Run + 4;
            store_ind(Ledger_Run, Mem_Tid);
            Ledger_Run = Ledger_Run + 4;
            Ledger_Count = Ledger_Count + 1;
            // честно: новая ячейка — ноль
            store_ind(Mem_Addr, 0x00000000);
        }
    }
}

// ---------- free: Mem_Addr + Mem_Tid -> вычеркнуть, zeroize ячейку ----------
function Mem_Free() {
    Mem_Fail = 0x00000000;
    RW_Count = 0x00000000;
    Scan_Idx = 0x00000000;
    RW_A_Run = RW_ADDR;
    RW_T_Run = RW_TID;
    Scan_Ledger = MEM_LEDGER;
    run Free_Scan();
    Ledger_Count = RW_Count;
    Ledger_Run = MEM_LEDGER;
    Scan_Idx = 0x00000000;
    RW_A_Run = RW_ADDR;
    RW_T_Run = RW_TID;
    run Restore_Ledger();
}

function Free_Scan() {
    if (Scan_Idx == Ledger_Count) {
        // done
    } else {
        Read_Addr = in_cell(Scan_Ledger);
        Scan_Ledger = Scan_Ledger + 4;
        Read_Tid = in_cell(Scan_Ledger);
        Scan_Ledger = Scan_Ledger + 4;
        if (Read_Addr == Mem_Addr) {
            if (Read_Tid == Mem_Tid) {
                store_ind(Mem_Addr, 0x00000000);  // честный zeroize
                // пропуск — удаляем пару
            } else {
                run Keep_Pair();
            }
        } else {
            run Keep_Pair();
        }
        Scan_Idx = Scan_Idx + 1;
        run Free_Scan();
    }
}

function Keep_Pair() {
    store_ind(RW_A_Run, Read_Addr);
    store_ind(RW_T_Run, Read_Tid);
    RW_A_Run = RW_A_Run + 4;
    RW_T_Run = RW_T_Run + 4;
    RW_Count = RW_Count + 1;
}

function Restore_Ledger() {
    if (Scan_Idx == Ledger_Count) {
        // ledger rebuilt
    } else {
        Tmp_A = in_cell(RW_A_Run);
        store_ind(Ledger_Run, Tmp_A);
        Ledger_Run = Ledger_Run + 4;
        Tmp_A = in_cell(RW_T_Run);
        store_ind(Ledger_Run, Tmp_A);
        Ledger_Run = Ledger_Run + 4;
        RW_A_Run = RW_A_Run + 4;
        RW_T_Run = RW_T_Run + 4;
        Scan_Idx = Scan_Idx + 1;
        run Restore_Ledger();
    }
}

// ---------- zeroize-exit: Mem_Tid -> обнулить все его ячейки, Leaked_Count ----------
function Mem_Zeroize_Task() {
    Leaked_Count = 0x00000000;
    RW_Count = 0x00000000;
    Scan_Idx = 0x00000000;
    RW_A_Run = RW_ADDR;
    RW_T_Run = RW_TID;
    Scan_Ledger = MEM_LEDGER;
    run Zero_Scan();
    Ledger_Count = RW_Count;
    Ledger_Run = MEM_LEDGER;
    Scan_Idx = 0x00000000;
    RW_A_Run = RW_ADDR;
    RW_T_Run = RW_TID;
    run Restore_Ledger();
    log_cell(LOG_PORT, Leaked_Count);        // честный отчёт leaked
}

function Zero_Scan() {
    if (Scan_Idx == Ledger_Count) {
        // done
    } else {
        Read_Addr = in_cell(Scan_Ledger);
        Scan_Ledger = Scan_Ledger + 4;
        Read_Tid = in_cell(Scan_Ledger);
        Scan_Ledger = Scan_Ledger + 4;
        if (Read_Tid == Mem_Tid) {
            store_ind(Read_Addr, 0x00000000);  // честный zeroize
            Leaked_Count = Leaked_Count + 1;
            // пара удаляется
        } else {
            run Keep_Pair();
        }
        Scan_Idx = Scan_Idx + 1;
        run Zero_Scan();
    }
}

// ---------- tests ----------
function Test_Alloc_Free() {
    // аккуратная задача tid=2: alloc 2, free 2 -> leaked 0
    Mem_Tid = 0x00000002;
    run Mem_Alloc();
    if (Mem_Fail == 0x00000000) {
        Tmp_A = Mem_Addr;            // save addr1
        // пишем мусор — free должен обнулить
        store_ind(Tmp_A, 0xDEADBEEF);
        run Mem_Alloc();
        if (Mem_Fail == 0x00000000) {
            Tmp_B = Mem_Addr;        // save addr2
            store_ind(Tmp_B, 0xCAFEBABE);
            // free addr1
            Mem_Addr = Tmp_A;
            run Mem_Free();
            Tmp_C = in_cell(Tmp_A);
            if (Tmp_C == 0x00000000) {
                out_cell(LOG_PORT, 0x0000A721);  // free zeroized
            } else {
                out_cell(LOG_PORT, 0x000099A3);
            }
            // free addr2
            Mem_Addr = Tmp_B;
            run Mem_Free();
            if (Ledger_Count == 0x00000000) {
                out_cell(LOG_PORT, 0x0000A722);  // ledger empty after frees
            } else {
                out_cell(LOG_PORT, 0x000099A4);
            }
        } else {
            out_cell(LOG_PORT, 0x000099A5);
        }
    } else {
        out_cell(LOG_PORT, 0x000099A6);
    }
}

function Test_Zeroize_Exit() {
    // задача tid=3: alloc 2, НЕ освобождает -> zeroize-exit leaked=2, ячейки=0
    Mem_Tid = 0x00000003;
    run Mem_Alloc();
    Tmp_A = Mem_Addr;
    store_ind(Tmp_A, 0x11111111);
    run Mem_Alloc();
    Tmp_B = Mem_Addr;
    store_ind(Tmp_B, 0x22222222);
    // tid=4 тоже владеет одной — не должна пострадать
    Mem_Tid = 0x00000004;
    run Mem_Alloc();
    Tmp_C = Mem_Addr;
    store_ind(Tmp_C, 0x44444444);

    Mem_Tid = 0x00000003;
    run Mem_Zeroize_Task();           // logs Leaked_Count (expect 2)
    if (Leaked_Count == 0x00000002) {
        out_cell(LOG_PORT, 0x0000A731);  // leaked=2 honest
    } else {
        out_cell(LOG_PORT, 0x000099A7);
    }
    // ячейки tid=3 обнулены
    Tmp_A = in_cell(Tmp_A);
    Tmp_B = in_cell(Tmp_B);
    if (Tmp_A == 0x00000000) {
        if (Tmp_B == 0x00000000) {
            out_cell(LOG_PORT, 0x0000A732);  // zeroized
        } else {
            out_cell(LOG_PORT, 0x000099A8);
        }
    } else {
        out_cell(LOG_PORT, 0x000099A9);
    }
    // ячейка tid=4 цела
    Tmp_C = in_cell(Tmp_C);
    if (Tmp_C == 0x44444444) {
        out_cell(LOG_PORT, 0x0000A733);  // other task intact
    } else {
        out_cell(LOG_PORT, 0x000099AA);
    }
    // cleanup tid=4
    Mem_Tid = 0x00000004;
    run Mem_Zeroize_Task();
}

function Test_Bounds() {
    // ledger bound: у нас 16 слотов; после cleanup count=0; заполним до 16
    run Fill_Ledger();
}

function Fill_Ledger() {
    if (Ledger_Count == LEDGER_MAX) {
        out_cell(LOG_PORT, 0x0000A740);      // ledger full reached
        // ещё один alloc -> E_LEDGER
        Mem_Tid = 0x00000009;
        run Mem_Alloc();
        if (Mem_Fail == E_LEDGER) {
            out_cell(LOG_PORT, 0x0000A741);  // honest ledger bound
        } else {
            out_cell(LOG_PORT, 0x000099AB);
        }
    } else {
        Mem_Tid = 0x00000008;
        run Mem_Alloc();
        if (Mem_Fail == 0x00000000) {
            run Fill_Ledger();
        } else {
            out_cell(LOG_PORT, 0x000099AC);
        }
    }
}
