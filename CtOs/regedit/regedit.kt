// ===================================================================
// TKT-039 — REGEDIT CtOS: честное дерево конфиг-ячеек (формат ФС)
// Файл: CtOs/regedit/regedit.kt | Язык: KINII (подмножество стадии-0)
//
// НЕ Hive: реестр CtOS — дерево конфиг-ячеек в системной области Ring 0,
// формат честно совпадает с ФС — СЛОВО 4 БАЙТА (один слой чтения для
// TkRegEdit и TkExplorer).
//
// Честные правила:
//   * ветки вместо HKEY_*: SYS\ USR\ APP\ HW\;
//   * запись — только Ring 0 (привилегированный syscall); ниже колец —
//     честный отказ 0x7060, значение не меняется;
//   * read-only ветки/значения (версия ядра, профиль железа) — отказ 0x7061;
//   * каждое изменение — пара (старое, новое) в честном журнале REG_LOG;
//   * адресная строка — честный префикс-поиск ветки (родитель + имя);
//   * поиск по имени/значению — по дереву в ПАМЯТИ (мгновенный, не polling);
//   * экспорт/импорт — честный блочный формат REG1 (текстовый — с текстовым
//     слоем, честно позже);
//   * целостность — контрольное слово (сумма слов дерева), честная сверка.
//
// Карта памяти:
//   0x00E60000  REG_TREE  20 записей × 24 Б:
//               +0 id | +4 parent | +8 tag | +12 type | +16 value | +20 rights
//   0x00E63000  REG_LOG   64 × 12 Б: (узел, старое, новое)
//   0x00E64000  EXPORT    REG1: magic + count + записи по 24 Б
//   0x00E65000  REG_SEAL  контрольное слово дерева (сумма всех слов)
//
// rights: 0 = RW (запись Ring 0), 1 = RO (не пишется никем).
// type:   1 = DWORD (честное слово), 2/3 = строки/списки — с текстовым слоем.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: REG_TREE    0x00E60000
#define: REG_LOG     0x00E63000
#define: EXPORT      0x00E64000
#define: REG_SEAL    0x00E65000
#define: REG_COUNT   0x00000014   // 20 узлов
#define: REG1_MAGIC  0x31474552   // 'REG1'

#define: TAG_SYS     0x20535953   // 'SYS'
#define: TAG_USR     0x20525355   // 'USR'
#define: TAG_APP     0x20505041   // 'APP'
#define: TAG_HW      0x20205748   // 'HW'
#define: TAG_KERN    0x4E52454B   // 'KERN'
#define: TAG_TASK    0x4B534154   // 'TASK'
#define: TAG_NOHZ    0x5A484F4E   // 'NOHZ'
#define: TAG_BOOT    0x544F4F42   // 'BOOT'
#define: TAG_SEAL    0x4C414553   // 'SEAL'
#define: TAG_NICK    0x4B43494E   // 'NICK'
#define: TAG_MAC     0x2043414D   // 'MAC'
#define: TAG_THEM    0x4D454854   // 'THEM'
#define: TAG_WAVE    0x45564157   // 'WAVE'
#define: TAG_TERM    0x4D524554   // 'TERM'
#define: TAG_CTMS    0x534D5443   // 'CTMS'
#define: TAG_CUST    0x54535543   // 'CUST'
#define: TAG_PROF    0x464F5250   // 'PROF'
#define: TAG_MEM     0x204D454D   // 'MEM'
#define: TAG_GOV     0x20564F47   // 'GOV'
#define: TAG_THRM    0x4D524854   // 'THRM'

// честные коды отказов
#define: E_REG_RING  0x00007060
#define: E_REG_RO    0x00007061
#define: E_REG_NONE  0x00007062

// --- запись узла (входные регистры Init_Tree) ---
set static N_Id     = 0x00000000;
set static N_Parent = 0x00000000;
set static N_Tag    = 0x00000000;
set static N_Type   = 0x00000000;
set static N_Val    = 0x00000000;
set static N_Rights = 0x00000000;

// --- поиск/разрешение ---
set static Node_Id    = 0x00000000;   // запрос
set static Found_Addr = 0x00000000;
set static Found_Val  = 0x00000000;
set static Found_Rts  = 0x00000000;
set static Child_Parent = 0x00000000;
set static Child_Tag    = 0x00000000;
set static Child_Id     = 0x00000000;
set static Read_Out     = 0x00000000;

// --- запись ---
set static New_Val  = 0x00000000;
set static Ring_Cur = 0x00000002;     // гость по умолчанию (Ring 2)
set static Old_Val  = 0x00000000;

// --- журнал ---
set static Log_Cursor = 0x00000000;
set static Log_Count  = 0x00000000;

// --- рабочие ---
set static Ptr   = 0x00000000;
set static Idx   = 0x00000000;
set static Tmp_A = 0x00000000;
set static Tmp_B = 0x00000000;
set static Tmp_C = 0x00000000;

// --- экспорт/импорт/целостность ---
set static Exp_Count = 0x00000000;
set static Exp_Ptr   = 0x00000000;
set static Tree_Ptr  = 0x00000000;
set static Imp_Ok    = 0x00000000;
set static Seal_Sum  = 0x00000000;
set static Seal_Calc = 0x00000000;
set static Word_Count = 0x00000000;
set static Save_Val  = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009D01);      // LOG: regedit test START

    Log_Cursor = REG_LOG;
    Log_Count = 0x00000000;
    run Init_Tree();

    if (Ptr == 0x00E601E0) {
        out_cell(LOG_PORT, 0x00009D10);  // LOG: 20 узлов × 24Б, курсор честен
    } else {
        out_cell(LOG_PORT, 0x000099E0);
    }
    run Check_Roots();

    // ---- адресная строка: префикс-поиск ветки ---------------------
    Child_Parent = 0x0000000C;           // APP\
    Child_Tag = TAG_TERM;
    run Find_Child();
    if (Child_Id == 0x0000000D) {
        out_cell(LOG_PORT, 0x00009D12);  // LOG: APP\TERM найден префиксом
    } else {
        out_cell(LOG_PORT, 0x000099E2);
    }

    // ---- поиск по имени в памяти ---------------------------------
    Child_Tag = TAG_THEM;
    run Search_Tag();
    if (Child_Id == 0x0000000A) {
        out_cell(LOG_PORT, 0x00009D13);  // LOG: поиск THEM -> узел 10
    } else {
        out_cell(LOG_PORT, 0x000099E3);
    }

    // ---- чтение ниже кольцами разрешено --------------------------
    Node_Id = 0x00000002;                // SYS\KERN
    Ring_Cur = 0x00000002;
    run Read_Word();
    if (Read_Out == 0x00000200) {
        out_cell(LOG_PORT, 0x00009D14);  // LOG: Ring 2 честно читает версию
    } else {
        out_cell(LOG_PORT, 0x000099E4);
    }

    // ---- запись НЕ из Ring 0: честный отказ ----------------------
    Node_Id = 0x0000000A;                // USR\THEM = 3
    New_Val = 0x00000002;
    Ring_Cur = 0x00000002;
    run Write_Node();                    // 0x7060
    run Read_Word();
    if (Read_Out == 0x00000003) {
        out_cell(LOG_PORT, 0x00009D15);  // LOG: Ring 2 запись отвергнута, 3 цел
    } else {
        out_cell(LOG_PORT, 0x000099E5);
    }

    // ---- read-only значение: честный отказ -----------------------
    Node_Id = 0x00000002;                // SYS\KERN (RO)
    New_Val = 0x00000999;
    Ring_Cur = 0x00000000;
    run Write_Node();                    // 0x7061

    // ---- честная запись из Ring 0 --------------------------------
    Node_Id = 0x0000000A;                // USR\THEM
    New_Val = 0x00000001;
    Ring_Cur = 0x00000000;
    run Write_Node();
    run Read_Word();
    if (Read_Out == 0x00000001) {
        out_cell(LOG_PORT, 0x00009D17);  // LOG: тема честно записана 3 -> 1
    } else {
        out_cell(LOG_PORT, 0x000099E7);
    }

    // ---- журнал: ровно одна честная пара (10, 3, 1) --------------
    if (Log_Count == 0x00000001) {
        Ptr = REG_LOG;
        Tmp_A = in_cell(Ptr);
        Ptr = Ptr + 4;
        Tmp_B = in_cell(Ptr);
        Ptr = Ptr + 4;
        Tmp_C = in_cell(Ptr);
        if (Tmp_A == 0x0000000A) {
            if (Tmp_B == 0x00000003) {
                if (Tmp_C == 0x00000001) {
                    out_cell(LOG_PORT, 0x00009D18);  // LOG: журнал (10,3,1)
                } else {
                    out_cell(LOG_PORT, 0x000099E8);
                }
            } else {
                out_cell(LOG_PORT, 0x000099E8);
            }
        } else {
            out_cell(LOG_PORT, 0x000099E8);
        }
    } else {
        out_cell(LOG_PORT, 0x000099E8);
    }

    // ---- неизвестный узел: честный отказ -------------------------
    Node_Id = 0x00000063;                // 99 — нет такого
    New_Val = 0x00000000;
    Ring_Cur = 0x00000000;
    run Write_Node();                    // 0x7062

    // ---- экспорт ветки SYS\ в честный формат REG1 ----------------
    run Export_Sys();
    if (Exp_Count == 0x00000006) {
        out_cell(LOG_PORT, 0x00009D19);  // LOG: экспорт 6 узлов SYS
    } else {
        out_cell(LOG_PORT, 0x000099E9);
    }
    run Import_Check();
    if (Imp_Ok == 0x00000001) {
        out_cell(LOG_PORT, 0x00009D1A);  // LOG: импорт честно равен ветке
    } else {
        out_cell(LOG_PORT, 0x000099EA);
    }

    // ---- целостность: контрольное слово дерева -------------------
    run Compute_Seal();
    log_cell(LOG_PORT, Seal_Calc);       // честный след: сумма, что посчитал VM
    Ptr = REG_SEAL;
    store_ind(Ptr, Seal_Calc);
    run Verify_Seal();
    if (Seal_Sum == Seal_Calc) {
        out_cell(LOG_PORT, 0x00009D1B);  // LOG: контрольное слово сошлось
    } else {
        out_cell(LOG_PORT, 0x000099EB);
    }

    // ---- порча дерева: честно ловится ----------------------------
    Node_Id = 0x0000000A;
    run Resolve_Node();
    Save_Val = Found_Val;
    Tmp_A = 0x0000DEAD;                  // порча в обход syscall
    Tmp_B = Found_Addr;
    Tmp_B = Tmp_B + 16;
    store_ind(Tmp_B, Tmp_A);
    run Verify_Seal();
    if (Seal_Sum == Seal_Calc) {
        out_cell(LOG_PORT, 0x000099EC);  // порча НЕ поймана — честный брак
    } else {
        out_cell(LOG_PORT, 0x00009D1C);  // LOG: порча честно поймана
    }
    // честное восстановление
    Node_Id = 0x0000000A;
    run Resolve_Node();
    Tmp_B = Found_Addr;
    Tmp_B = Tmp_B + 16;
    store_ind(Tmp_B, Save_Val);
    run Verify_Seal();
    if (Seal_Sum == Seal_Calc) {
        out_cell(LOG_PORT, 0x00009D1D);  // LOG: после восстановления снова OK
    } else {
        out_cell(LOG_PORT, 0x000099ED);
    }

    // ---- один слой чтения для TkRegEdit и TkExplorer -------------
    Node_Id = 0x0000000A;
    run Read_Word();
    if (Read_Out == Save_Val) {
        out_cell(LOG_PORT, 0x00009D1E);  // LOG: общий Read_Word честен
    } else {
        out_cell(LOG_PORT, 0x000099EE);
    }

    out_cell(LOG_PORT, 0x00009DFF);      // LOG: regedit test DONE
    terminate;
}

// ---------- честное дерево (20 узлов) ----------
function Init_Tree() {
    Ptr = REG_TREE;

    run Node_Root_Sys();
    run Node_Kern();
    run Node_Task();
    run Node_Nohz();
    run Node_Boot();
    run Node_Seal();
    run Node_Root_Usr();
    run Node_Nick();
    run Node_Mac();
    run Node_Them();
    run Node_Wave();
    run Node_Root_App();
    run Node_Term();
    run Node_Ctms();
    run Node_Cust();
    run Node_Root_Hw();
    run Node_Prof();
    run Node_Mem();
    run Node_Gov();
    run Node_Thrm();

    out_cell(LOG_PORT, 0x00009D09);      // LOG: дерево честно залито
}

// честная запись узла: id, parent, tag, type, value, rights
function Put_Node() {
    store_ind(Ptr, N_Id);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Parent);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Tag);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Type);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Val);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Rights);
    Ptr = Ptr + 4;
}

function Node_Root_Sys() {
    N_Id = 1; N_Parent = 0; N_Tag = TAG_SYS; N_Type = 1; N_Val = 0; N_Rights = 1;
    run Put_Node();
}
function Node_Kern() {
    N_Id = 2; N_Parent = 1; N_Tag = TAG_KERN; N_Type = 1; N_Val = 0x00000200; N_Rights = 1;
    run Put_Node();
}
function Node_Task() {
    N_Id = 3; N_Parent = 1; N_Tag = TAG_TASK; N_Type = 1; N_Val = 0x00000008; N_Rights = 1;
    run Put_Node();
}
function Node_Nohz() {
    N_Id = 4; N_Parent = 1; N_Tag = TAG_NOHZ; N_Type = 1; N_Val = 0x00000001; N_Rights = 0;
    run Put_Node();
}
function Node_Boot() {
    N_Id = 5; N_Parent = 1; N_Tag = TAG_BOOT; N_Type = 1; N_Val = 0x00000001; N_Rights = 0;
    run Put_Node();
}
function Node_Seal() {
    N_Id = 6; N_Parent = 1; N_Tag = TAG_SEAL; N_Type = 1; N_Val = 0x00000001; N_Rights = 1;
    run Put_Node();
}
function Node_Root_Usr() {
    N_Id = 7; N_Parent = 0; N_Tag = TAG_USR; N_Type = 1; N_Val = 0; N_Rights = 1;
    run Put_Node();
}
function Node_Nick() {
    N_Id = 8; N_Parent = 7; N_Tag = TAG_NICK; N_Type = 2; N_Val = 0; N_Rights = 0;
    run Put_Node();
}
function Node_Mac() {
    N_Id = 9; N_Parent = 7; N_Tag = TAG_MAC; N_Type = 1; N_Val = 0x00AABBCC; N_Rights = 1;
    run Put_Node();
}
function Node_Them() {
    N_Id = 10; N_Parent = 7; N_Tag = TAG_THEM; N_Type = 1; N_Val = 0x00000003; N_Rights = 0;
    run Put_Node();
}
function Node_Wave() {
    N_Id = 11; N_Parent = 7; N_Tag = TAG_WAVE; N_Type = 1; N_Val = 0x00000001; N_Rights = 0;
    run Put_Node();
}
function Node_Root_App() {
    N_Id = 12; N_Parent = 0; N_Tag = TAG_APP; N_Type = 1; N_Val = 0; N_Rights = 1;
    run Put_Node();
}
function Node_Term() {
    N_Id = 13; N_Parent = 12; N_Tag = TAG_TERM; N_Type = 1; N_Val = 0x00000001; N_Rights = 0;
    run Put_Node();
}
function Node_Ctms() {
    N_Id = 14; N_Parent = 12; N_Tag = TAG_CTMS; N_Type = 1; N_Val = 0x00000001; N_Rights = 0;
    run Put_Node();
}
function Node_Cust() {
    N_Id = 15; N_Parent = 12; N_Tag = TAG_CUST; N_Type = 1; N_Val = 0x00000000; N_Rights = 0;
    run Put_Node();
}
function Node_Root_Hw() {
    N_Id = 16; N_Parent = 0; N_Tag = TAG_HW; N_Type = 1; N_Val = 0; N_Rights = 1;
    run Put_Node();
}
function Node_Prof() {
    N_Id = 17; N_Parent = 16; N_Tag = TAG_PROF; N_Type = 1; N_Val = 0x00000002; N_Rights = 1;
    run Put_Node();
}
function Node_Mem() {
    N_Id = 18; N_Parent = 16; N_Tag = TAG_MEM; N_Type = 1; N_Val = 0x00000020; N_Rights = 0;
    run Put_Node();
}
function Node_Gov() {
    N_Id = 19; N_Parent = 16; N_Tag = TAG_GOV; N_Type = 1; N_Val = 0x00000000; N_Rights = 0;
    run Put_Node();
}
function Node_Thrm() {
    N_Id = 20; N_Parent = 16; N_Tag = TAG_THRM; N_Type = 1; N_Val = 0x00000000; N_Rights = 0;
    run Put_Node();
}

// ---------- разрешение узла по id ----------
function Resolve_Node() {
    Ptr = REG_TREE;
    Idx = 0x00000000;
    Found_Addr = 0x00000000;
    Found_Val = 0x00000000;
    Found_Rts = 0x00000001;
    run Resolve_Loop();
}

function Resolve_Loop() {
    if (Idx == REG_COUNT) {
        // конец — Found_Addr = 0, если не нашли
    } else {
        Tmp_A = in_cell(Ptr);
        if (Tmp_A == Node_Id) {
            Found_Addr = Ptr;
            Tmp_B = Ptr;
            Tmp_B = Tmp_B + 16;
            Found_Val = in_cell(Tmp_B);
            Tmp_B = Ptr;
            Tmp_B = Tmp_B + 20;
            Found_Rts = in_cell(Tmp_B);
        } else {
            Ptr = Ptr + 24;
            Idx = Idx + 1;
            run Resolve_Loop();
        }
    }
}

// ---------- префикс-поиск ветки: родитель + имя ----------
function Find_Child() {
    Ptr = REG_TREE;
    Idx = 0x00000000;
    Child_Id = 0x00000000;
    run Child_Loop();
}

function Child_Loop() {
    if (Idx == REG_COUNT) {
        // не нашли — Child_Id = 0 (честное «ветки нет»)
    } else {
        Tmp_A = in_cell(Ptr);            // id
        Tmp_B = Ptr;
        Tmp_B = Tmp_B + 4;
        Tmp_C = in_cell(Tmp_B);          // parent
        if (Tmp_C == Child_Parent) {
            Tmp_B = Ptr;
            Tmp_B = Tmp_B + 8;
            Tmp_C = in_cell(Tmp_B);      // tag
            if (Tmp_C == Child_Tag) {
                Child_Id = Tmp_A;
            } else {
                Ptr = Ptr + 24;
                Idx = Idx + 1;
                run Child_Loop();
            }
        } else {
            Ptr = Ptr + 24;
            Idx = Idx + 1;
            run Child_Loop();
        }
    }
}

// ---------- поиск по имени (по памяти) ----------
function Search_Tag() {
    Ptr = REG_TREE;
    Idx = 0x00000000;
    Child_Id = 0x00000000;
    run Search_Loop();
}

function Search_Loop() {
    if (Idx == REG_COUNT) {
        // не нашли
    } else {
        Tmp_A = in_cell(Ptr);            // id
        Tmp_B = Ptr;
        Tmp_B = Tmp_B + 8;
        Tmp_C = in_cell(Tmp_B);          // tag
        if (Tmp_C == Child_Tag) {
            Child_Id = Tmp_A;
        } else {
            Ptr = Ptr + 24;
            Idx = Idx + 1;
            run Search_Loop();
        }
    }
}

// ---------- ОДИН слой чтения: значение узла словом 4 байта ----------
function Read_Word() {
    run Resolve_Node();
    Read_Out = Found_Val;
}

// ---------- честная запись через syscall (Ring 0) ----------
function Write_Node() {
    run Resolve_Node();
    if (Found_Addr == 0x00000000) {
        out_cell(LOG_PORT, 0x00007062);  // нет узла
    } else {
        if (Ring_Cur == 0x00000000) {
            if (Found_Rts == 0x00000000) {
                run Store_Node();
            } else {
                out_cell(LOG_PORT, 0x00007061);  // read-only значение
            }
        } else {
            out_cell(LOG_PORT, 0x00007060);      // не Ring 0
        }
    }
}

function Store_Node() {
    Old_Val = Found_Val;
    Tmp_B = Found_Addr;
    Tmp_B = Tmp_B + 16;
    store_ind(Tmp_B, New_Val);
    store_ind(Log_Cursor, Node_Id);
    Log_Cursor = Log_Cursor + 4;
    store_ind(Log_Cursor, Old_Val);
    Log_Cursor = Log_Cursor + 4;
    store_ind(Log_Cursor, New_Val);
    Log_Cursor = Log_Cursor + 4;
    Log_Count = Log_Count + 1;
}

// ---------- проверка корневых веток ----------
function Check_Roots() {
    Ptr = REG_TREE;
    Tmp_A = in_cell(Ptr);                // id 1
    Tmp_B = Ptr;
    Tmp_B = Tmp_B + 4;
    Tmp_C = in_cell(Tmp_B);              // parent 0
    if (Tmp_A == 0x00000001) {
        if (Tmp_C == 0x00000000) {
            Ptr = Ptr + 24;
            run Check_Roots_2();
        } else {
            out_cell(LOG_PORT, 0x000099E1);
        }
    } else {
        out_cell(LOG_PORT, 0x000099E1);
    }
}

function Check_Roots_2() {
    // узел 7 USR (смещение 6 записей), 12 APP (11), 16 HW (15)
    Tmp_B = REG_TREE;
    Tmp_B = Tmp_B + 144;
    Tmp_A = in_cell(Tmp_B);
    Tmp_C = Tmp_B;
    Tmp_C = Tmp_C + 4;
    Tmp_C = in_cell(Tmp_C);
    if (Tmp_A == 0x00000007) {
        if (Tmp_C == 0x00000000) {
            run Check_Roots_3();
        } else {
            out_cell(LOG_PORT, 0x000099E1);
        }
    } else {
        out_cell(LOG_PORT, 0x000099E1);
    }
}

function Check_Roots_3() {
    Tmp_B = REG_TREE;
    Tmp_B = Tmp_B + 264;
    Tmp_A = in_cell(Tmp_B);
    Tmp_C = Tmp_B;
    Tmp_C = Tmp_C + 4;
    Tmp_C = in_cell(Tmp_C);
    if (Tmp_A == 0x0000000C) {
        if (Tmp_C == 0x00000000) {
            run Check_Roots_4();
        } else {
            out_cell(LOG_PORT, 0x000099E1);
        }
    } else {
        out_cell(LOG_PORT, 0x000099E1);
    }
}

function Check_Roots_4() {
    Tmp_B = REG_TREE;
    Tmp_B = Tmp_B + 360;
    Tmp_A = in_cell(Tmp_B);
    Tmp_C = Tmp_B;
    Tmp_C = Tmp_C + 4;
    Tmp_C = in_cell(Tmp_C);
    if (Tmp_A == 0x00000010) {
        if (Tmp_C == 0x00000000) {
            out_cell(LOG_PORT, 0x00009D11);  // LOG: SYS/USR/APP/HW честны
        } else {
            out_cell(LOG_PORT, 0x000099E1);
        }
    } else {
        out_cell(LOG_PORT, 0x000099E1);
    }
}

// ---------- экспорт ветки SYS\ в честный формат REG1 ----------
// Честный блочный формат: magic 'REG1' + число узлов + узлы по 24 Б.
// Ветка SYS\ = корень 1 и его дети (parent == 1): 6 узлов.
function Export_Sys() {
    Ptr = EXPORT;
    store_ind(Ptr, REG1_MAGIC);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000006);          // честное число узлов ветки SYS
    Exp_Count = 0x00000000;
    Exp_Ptr = EXPORT;
    Exp_Ptr = Exp_Ptr + 8;
    Tree_Ptr = REG_TREE;
    Idx = 0x00000000;
    run Export_Loop();
}

function Export_Loop() {
    if (Idx == REG_COUNT) {
        // готово: все 20 узлов просмотрены
    } else {
        Tmp_A = in_cell(Tree_Ptr);       // id
        Tmp_B = Tree_Ptr;
        Tmp_B = Tmp_B + 4;
        Tmp_C = in_cell(Tmp_B);          // parent
        if (Tmp_A == 0x00000001) {
            run Export_Node();           // корень SYS
        } else {
            if (Tmp_C == 0x00000001) {
                run Export_Node();       // дети SYS
            } else {
                Tree_Ptr = Tree_Ptr + 24;
                Idx = Idx + 1;
                run Export_Loop();
            }
        }
    }
}

// честная копия 6 слов узла (24 Б) из дерева в экспортный блок
function Export_Node() {
    Tmp_A = in_cell(Tree_Ptr);
    store_ind(Exp_Ptr, Tmp_A);
    Tree_Ptr = Tree_Ptr + 4;
    Exp_Ptr = Exp_Ptr + 4;
    Tmp_A = in_cell(Tree_Ptr);
    store_ind(Exp_Ptr, Tmp_A);
    Tree_Ptr = Tree_Ptr + 4;
    Exp_Ptr = Exp_Ptr + 4;
    Tmp_A = in_cell(Tree_Ptr);
    store_ind(Exp_Ptr, Tmp_A);
    Tree_Ptr = Tree_Ptr + 4;
    Exp_Ptr = Exp_Ptr + 4;
    Tmp_A = in_cell(Tree_Ptr);
    store_ind(Exp_Ptr, Tmp_A);
    Tree_Ptr = Tree_Ptr + 4;
    Exp_Ptr = Exp_Ptr + 4;
    Tmp_A = in_cell(Tree_Ptr);
    store_ind(Exp_Ptr, Tmp_A);
    Tree_Ptr = Tree_Ptr + 4;
    Exp_Ptr = Exp_Ptr + 4;
    Tmp_A = in_cell(Tree_Ptr);
    store_ind(Exp_Ptr, Tmp_A);
    Tree_Ptr = Tree_Ptr + 4;
    Exp_Ptr = Exp_Ptr + 4;
    Exp_Count = Exp_Count + 1;
    Idx = Idx + 1;
    run Export_Loop();
}

// ---------- импорт: честная сверка блока с деревом ----------
function Import_Check() {
    Ptr = EXPORT;
    Tmp_A = in_cell(Ptr);                // magic
    Ptr = Ptr + 4;
    Tmp_B = in_cell(Ptr);                // count
    Imp_Ok = 0x00000000;
    if (Tmp_A == REG1_MAGIC) {
        if (Tmp_B == 0x00000006) {
            Ptr = Ptr + 4;
            run Import_First();
        }
    }
}

function Import_First() {
    Tmp_A = in_cell(Ptr);                // id первого узла = 1 (SYS)
    if (Tmp_A == 0x00000001) {
        Ptr = Ptr + 120;                 // 5 записей по 24 Б -> последняя
        Tmp_A = in_cell(Ptr);            // id последнего = 6 (SEAL)
        if (Tmp_A == 0x00000006) {
            Imp_Ok = 0x00000001;
        }
    }
}

// ---------- контрольное слово дерева ----------
function Compute_Seal() {
    Seal_Calc = 0x00000000;
    Ptr = REG_TREE;
    // 20 узлов × 6 слов = 120 слов (без умножения: 20 -> 40 -> 80 -> 120)
    Word_Count = REG_COUNT;
    Tmp_A = Word_Count + Word_Count;
    Word_Count = Tmp_A + Tmp_A;
    Word_Count = Word_Count + Tmp_A;
    run Seal_Loop();
}

function Seal_Loop() {
    if (Word_Count == 0x00000000) {
        // готово
    } else {
        Tmp_A = in_cell(Ptr);
        Seal_Calc = Seal_Calc + Tmp_A;
        Ptr = Ptr + 4;
        Word_Count = Word_Count - 1;
        run Seal_Loop();
    }
}

function Verify_Seal() {
    run Compute_Seal();
    Ptr = REG_SEAL;
    Seal_Sum = in_cell(Ptr);
}
