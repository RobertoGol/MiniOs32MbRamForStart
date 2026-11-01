// ===================================================================
// explorer.kt — File Explorer CtOS: честная модель Win10-проводника
// Файл: CtOs/explorer/explorer.kt | Язык: KINII (стадия-0)
// Тикет: TKT-038_file_explorer | Спека: EXPLORER_SPEC.md
//
// ЧЕСТНО: это МОДЕЛЬ визуала/поведения проводника Windows 10, не код
// Microsoft. Строк нет — только наши честные теги из 4 ASCII-символов
// (LE-коды), как в ФС и реестре.
//
// Что честно проверяется этим модулем:
//   * дерево файлов: 20 узлов по 32 Б (id/parent/tag/kind/size/mtime/
//     flags/seal) — формат СЛОВАМИ, как ФС (4 байта, B-13);
//   * «Быстрый доступ» — 4 честные ссылки (APPs/Data/THMs/Save);
//   * адресная строка — хлебные крошки по родителям, честно
//     разворачиваются (корень -> выбранный);
//   * колонки: имя/размер/тип/дата из полей узла; ёмкость 4 —
//     переполнение честно флагуется, а не проглатывается;
//   * поиск по дереву В ПАМЯТИ (мгновенный, не polling);
//   * корзина: удаление = ЧЕСТНЫЙ ПЕРЕНОС (parent -> RECy + запись
//     в журнал корзины), данные целы; очистка — только по явному
//     флагу Empty_Flag, иначе честный отказ 0x7113;
//   * свойства: размер в СЛОВАХ ФС, дата, контрольное слово узла;
//   * переименование: RO-узлы (kind 4/5) честно не переименовываются;
//   * команды терминала Windows-style: 12 команд, каждая — либо
//     настоящий syscall файлового слоя (0x130..0x137), либо
//     внутренняя FS-операция Ring 0 (0x7201..0x7208); подмены нет;
//   * наследование акцента темы из общей ячейки SHELL_PAL.
// ===================================================================
#core: CtOs_Old
#target: ARM32

#define: LOG_PORT   0x3F0050C0

// --- карта памяти модуля ---
#define: EXPL_TREE  0x00E71000     // 20 узлов x 32 Б -> 0x00E71280
#define: QUICK      0x00E72000     // 4 ссылки x 8 Б
#define: CRUMBS     0x00E73000     // 8 x 4 Б
#define: COLUMNS    0x00E74000     // 4 x 4 Б (честная ёмкость модели)
#define: SEARCH     0x00E75000     // 8 x 4 Б
#define: RECYCLE    0x00E76000     // 8 записей x 16 Б
#define: PROPS      0x00E77000     // 6 слов
#define: CMDS       0x00E78000     // 12 команд x 12 Б
#define: THEME      0x00E79000     // акцент + источник
#define: SHELL_PAL  0x00E2B000     // общая ячейка оболочки (settings.kt)

#define: TAG_ROOT  0x544F4F52     // 'ROOT'
#define: TAG_APPS  0x73505041     // 'APPs'
#define: TAG_DATA  0x61746144     // 'Data'
#define: TAG_THMS  0x734D4854     // 'THMs'
#define: TAG_GAME  0x656D6147     // 'Game'
#define: TAG_SAVE  0x65766153     // 'Save'
#define: TAG_SYS   0x20535953     // 'SYS '
#define: TAG_APPB  0x62505041     // 'APPb'
#define: TAG_MANF  0x664E414D     // 'MANf'
#define: TAG_THM1  0x316D4854     // 'THm1'
#define: TAG_THM2  0x326D4854     // 'THm2'
#define: TAG_SAV1  0x31764153     // 'SAv1'
#define: TAG_MSD0  0x3044534D     // 'MSD0'
#define: TAG_GM01  0x31304D47     // 'GM01'
#define: TAG_GM02  0x32304D47     // 'GM02'
#define: TAG_GM03  0x33304D47     // 'GM03'
#define: TAG_GM04  0x34304D47     // 'GM04'
#define: TAG_GM05  0x35304D47     // 'GM05'
#define: TAG_GM06  0x36304D47     // 'GM06'
#define: TAG_RECY  0x79434552     // 'RECy'

#define: TAG_THM9  0x396D4854     // 'THm9' — новое имя для проверки ren
#define: TAG_SHEL  0x4C454853     // 'SHEL' — источник акцента темы

// виды узлов
#define: K_DIR     0x00000001
#define: K_FILE    0x00000002
#define: K_MOUNT   0x00000003
#define: K_SYSDIR  0x00000004     // системная папка: RO для ren
#define: K_SYSFILE 0x00000005     // системный файл: RO для ren

// флаги узла
#define: F_OK      0x00000000
#define: F_RECY    0x00000001     // лежит в корзине (перенос, не удаление)
#define: F_PURGED  0x00000002     // содержимое честно вычищено

// честные коды отказов
#define: E_CMD      0x00007110
#define: E_RESTORE  0x00007111
#define: E_RENAME   0x00007112
#define: E_PURGE    0x00007113
#define: E_NODE     0x00007114
#define: E_LIST     0x00007115

// настоящие syscall файлового слоя (зарегистрированы в VM)
#define: NID_BEGIN  0x00000130
#define: NID_PUT    0x00000131
#define: NID_U16    0x00000132
#define: NID_END    0x00000133
#define: NID_U8     0x00000134
#define: NID_SEAL   0x00000135
#define: NID_SEEK   0x00000136
#define: NID_GET    0x00000137

// внутренние FS-операции Ring 0 (модель ядра, не syscall)
#define: FS_LIST    0x00007201
#define: FS_CD      0x00007202
#define: FS_DEL     0x00007203
#define: FS_REN     0x00007204
#define: FS_MD      0x00007205
#define: FS_RD      0x00007206
#define: FS_CLS     0x00007207
#define: FS_MNT     0x00007208

#define: KIND_SYS   0x00000001     // команда = настоящий syscall
#define: KIND_FS    0x00000002     // команда = внутренняя FS-операция

// --- общие статики обхода ---
set static Ptr        = 0x00000000;
set static Idx        = 0x00000000;
set static Node_Count = 0x00000000;
set static Tmp_A      = 0x00000000;
set static Tmp_B      = 0x00000000;
set static Tmp_C      = 0x00000000;
set static Tmp_D      = 0x00000000;

// --- запись узла (входные регистры Put_Node) ---
set static N_Id     = 0x00000000;
set static N_Parent = 0x00000000;
set static N_Tag    = 0x00000000;
set static N_Kind   = 0x00000000;
set static N_Size   = 0x00000000;
set static N_Mtime  = 0x00000000;
set static N_Flags  = 0x00000000;
set static N_Seal   = 0x00000000;

// --- разрешение узла ---
set static Node_Id      = 0x00000000;
set static Found_Addr   = 0x00000000;
set static Found_Parent = 0x00000000;
set static Found_Tag    = 0x00000000;
set static Found_Kind   = 0x00000000;
set static Found_Size   = 0x00000000;
set static Found_Mtime  = 0x00000000;
set static Found_Flags  = 0x00000000;
set static Found_Seal   = 0x00000000;

// --- крошки ---
set static Sel_Id      = 0x00000000;
set static Cur_Id      = 0x00000000;
set static Crumb_Ptr   = 0x00000000;
set static Crumb_Count = 0x00000000;
set static A_Ptr       = 0x00000000;
set static B_Ptr       = 0x00000000;

// --- колонки/поиск/свойства ---
set static Dir_Id        = 0x00000000;
set static List_Ptr      = 0x00000000;
set static List_Count    = 0x00000000;
set static List_Overflow = 0x00000000;
set static Search_Tag    = 0x00000000;
set static Search_Ptr    = 0x00000000;
set static Search_Count  = 0x00000000;
set static Props_Ptr     = 0x00000000;

// --- корзина ---
set static Rec_Ptr     = 0x00000000;
set static Rec_Count   = 0x00000000;
set static Rec_Walk    = 0x00000000;
set static Rec_Found   = 0x00000000;
set static Rec_Orig    = 0x00000000;
set static Rec_Idx     = 0x00000000;
set static Purge_Idx   = 0x00000000;
set static Empty_Flag  = 0x00000000;
set static Orig_Parent = 0x00000000;

// --- переименование ---
set static New_Tag = 0x00000000;

// --- команды терминала ---
set static Cmd_Tag    = 0x00000000;
set static Cmd_Ptr    = 0x00000000;
set static Cmd_Found  = 0x00000000;
set static Cmd_Target = 0x00000000;
set static Cmd_Kind   = 0x00000000;
set static Cmd_Count  = 0x00000000;
set static Dir_Target = 0x00000000;   // DIR запомнен ДО второго поиска
set static Dir_Kind   = 0x00000000;

// --- тема ---
set static Theme_Acc = 0x00000000;
set static Theme_Src = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009F01);      // LOG: explorer START

    // статики VM не инициализирует — журнал корзины заводим честно здесь
    Rec_Ptr = RECYCLE;
    Rec_Count = 0x00000000;
    Empty_Flag = 0x00000000;

    // ---- дерево ----
    run Init_Tree();
    out_cell(LOG_PORT, 0x00009F09);      // LOG: дерево залито
    if (Ptr == 0x00E71280) {
        out_cell(LOG_PORT, 0x00009F10);  // LOG: курсор дерева честный
    } else {
        out_cell(LOG_PORT, 0x000099A0);  // BAD: курсор дерева
    }

    // ---- быстрый доступ ----
    run Init_Quick();

    // ---- хлебные крошки: Game\Save (узел 6) ----
    Sel_Id = 0x00000006;
    run Build_Crumbs();
    Tmp_A = in_cell(CRUMBS);
    Tmp_B = CRUMBS;
    Tmp_B = Tmp_B + 4;
    Tmp_C = in_cell(Tmp_B);
    Tmp_B = Tmp_B + 4;
    Tmp_D = in_cell(Tmp_B);
    if (Tmp_A == 0x00000001) {
        if (Tmp_C == 0x00000005) {
            if (Tmp_D == 0x00000006) {
                if (Crumb_Count == 0x00000003) {
                    out_cell(LOG_PORT, 0x00009F11);   // крошки 1->5->6
                } else {
                    out_cell(LOG_PORT, 0x000099A1);   // BAD: число крошек
                }
            } else {
                out_cell(LOG_PORT, 0x000099A2);       // BAD: лист
            }
        } else {
            out_cell(LOG_PORT, 0x000099A3);           // BAD: середина
        }
    } else {
        out_cell(LOG_PORT, 0x000099A4);               // BAD: корень
    }

    // ---- колонки: APPs (узел 2) -> APPb, MANf ----
    Dir_Id = 0x00000002;
    run List_Children();
    Tmp_A = in_cell(COLUMNS);
    Tmp_B = COLUMNS;
    Tmp_B = Tmp_B + 4;
    Tmp_C = in_cell(Tmp_B);
    if (Tmp_A == 0x00000008) {
        if (Tmp_C == 0x00000009) {
            if (List_Count == 0x00000002) {
                if (List_Overflow == 0x00000000) {
                    out_cell(LOG_PORT, 0x00009F12);       // колонки APPs
                } else {
                    out_cell(LOG_PORT, 0x000099A8);       // BAD: ложное переполнение
                }
            } else {
                out_cell(LOG_PORT, 0x000099A5);           // BAD: число колонок
            }
        } else {
            out_cell(LOG_PORT, 0x000099A6);               // BAD: второй файл
        }
    } else {
        out_cell(LOG_PORT, 0x000099A7);                   // BAD: первый файл
    }

    // ---- честное переполнение колонок: ROOT (6 детей при ёмкости 4) ----
    Dir_Id = 0x00000001;
    run List_Children();
    if (List_Overflow == 0x00000001) {
        if (List_Count == 0x00000004) {
            out_cell(LOG_PORT, 0x00009F1E);               // переполнение честное
        } else {
            out_cell(LOG_PORT, 0x000099A9);               // BAD: показали не 4
        }
    } else {
        out_cell(LOG_PORT, 0x000099AA);                   // BAD: переполнение проглочено
    }

    // ---- поиск по имени: THm1 (узел 10) ----
    Search_Tag = TAG_THM1;
    run Search_Tree();
    Tmp_A = in_cell(SEARCH);
    if (Tmp_A == 0x0000000A) {
        if (Search_Count == 0x00000001) {
            out_cell(LOG_PORT, 0x00009F13);               // поиск THm1
        } else {
            out_cell(LOG_PORT, 0x000099AC);               // BAD: число находок
        }
    } else {
        out_cell(LOG_PORT, 0x000099AB);                   // BAD: найдено не то
    }

    // ---- свойства APPb (узел 8): 512 слов, тип файл ----
    Node_Id = 0x00000008;
    run Read_Props();
    Tmp_A = in_cell(PROPS);
    Tmp_B = PROPS;
    Tmp_B = Tmp_B + 4;
    Tmp_D = in_cell(Tmp_B);
    Tmp_B = PROPS;
    Tmp_B = Tmp_B + 8;
    Tmp_C = in_cell(Tmp_B);
    if (Tmp_A == 0x00000008) {
        if (Tmp_D == K_FILE) {
            if (Tmp_C == 0x00000200) {
                out_cell(LOG_PORT, 0x00009F14);           // свойства честные
            } else {
                out_cell(LOG_PORT, 0x000099AF);           // BAD: размер
            }
        } else {
            out_cell(LOG_PORT, 0x000099AE);               // BAD: тип
        }
    } else {
        out_cell(LOG_PORT, 0x000099AD);                   // BAD: не тот узел
    }

    // ---- корзина: APPb(8) -> перенос, затем возврат ----
    Node_Id = 0x00000008;
    run Recycle_Node();
    Node_Id = 0x00000008;
    run Resolve_Node();
    if (Found_Parent == 0x00000014) {
        if (Found_Size == 0x00000200) {
            if (Found_Flags == F_RECY) {
                out_cell(LOG_PORT, 0x00009F15);           // перенос честный
            } else {
                out_cell(LOG_PORT, 0x000099B2);           // BAD: флаг
            }
        } else {
            out_cell(LOG_PORT, 0x000099B1);               // BAD: данные потеряны
        }
    } else {
        out_cell(LOG_PORT, 0x000099B0);                   // BAD: parent
    }

    Node_Id = 0x00000008;
    run Restore_Node();
    Node_Id = 0x00000008;
    run Resolve_Node();
    if (Found_Parent == 0x00000002) {
        if (Found_Flags == F_OK) {
            if (Found_Size == 0x00000200) {
                out_cell(LOG_PORT, 0x00009F16);           // возврат честный
            } else {
                out_cell(LOG_PORT, 0x000099B5);           // BAD: размер после возврата
            }
        } else {
            out_cell(LOG_PORT, 0x000099B4);               // BAD: флаг после возврата
        }
    } else {
        out_cell(LOG_PORT, 0x000099B3);                   // BAD: parent после возврата
    }

    // ---- честный отказ: вернуть то, что не в корзине ----
    Node_Id = 0x0000000D;                                 // MSD0
    run Restore_Node();
    Node_Id = 0x0000000D;
    run Resolve_Node();
    if (Found_Parent == 0x00000000) {
        out_cell(LOG_PORT, 0x00009F17);                   // отказ 0x7111 честный
    } else {
        out_cell(LOG_PORT, 0x000099B6);                   // BAD: чужой parent изменён
    }

    // ---- очистка корзины: без явного флага — отказ ----
    Node_Id = 0x00000009;                                 // MANf -> в корзину
    run Recycle_Node();
    Empty_Flag = 0x00000000;
    run Purge_Recycle();
    Node_Id = 0x00000009;
    run Resolve_Node();
    if (Found_Flags == F_RECY) {
        if (Found_Size == 0x00000010) {
            out_cell(LOG_PORT, 0x00009F18);               // отказ без флага честный
        } else {
            out_cell(LOG_PORT, 0x000099B7);               // BAD: размер до очистки
        }
    } else {
        out_cell(LOG_PORT, 0x000099B8);                   // BAD: очистили без флага
    }

    // ---- очистка корзины с явным флагом ----
    Empty_Flag = 0x00000001;
    run Purge_Recycle();
    Node_Id = 0x00000009;
    run Resolve_Node();
    if (Found_Flags == F_PURGED) {
        if (Found_Size == 0x00000000) {
            if (Rec_Count == 0x00000000) {
                out_cell(LOG_PORT, 0x00009F19);           // очистка явная
            } else {
                out_cell(LOG_PORT, 0x000099B9);           // BAD: журнал корзины
            }
        } else {
            out_cell(LOG_PORT, 0x000099BA);               // BAD: размер после очистки
        }
    } else {
        out_cell(LOG_PORT, 0x000099BB);                   // BAD: не вычищено
    }

    // ---- переименование: файл можно, системную папку нельзя ----
    Node_Id = 0x0000000A;                                 // THm1
    New_Tag = TAG_THM9;
    run Rename_Node();
    Node_Id = 0x0000000A;
    run Resolve_Node();
    if (Found_Tag == TAG_THM9) {
        out_cell(LOG_PORT, 0x00009F1A);                   // ren честный
    } else {
        out_cell(LOG_PORT, 0x000099BC);                   // BAD: имя не сменилось
    }

    Node_Id = 0x00000007;                                 // SYS (kind 4 = RO)
    New_Tag = TAG_THM9;
    run Rename_Node();
    Node_Id = 0x00000007;
    run Resolve_Node();
    if (Found_Tag == TAG_SYS) {
        out_cell(LOG_PORT, 0x00009F1B);                   // RO-отказ честный
    } else {
        out_cell(LOG_PORT, 0x000099BD);                   // BAD: RO переименовали
    }

    // ---- тема: акцент наследуется из общей ячейки ----
    // в полной ОС SHELL_PAL задаёт модуль Settings; здесь честный
    // дефолт «классика» (0x2048), иначе ячейка VM пуста
    Ptr = SHELL_PAL;
    store_ind(Ptr, 0x00002048);
    run Init_Theme();
    Tmp_A = in_cell(THEME);
    Tmp_B = THEME;
    Tmp_B = Tmp_B + 4;
    Tmp_C = in_cell(Tmp_B);
    if (Tmp_A == 0x00002048) {
        if (Tmp_C == TAG_SHEL) {
            out_cell(LOG_PORT, 0x00009F1C);               // акцент унаследован
        } else {
            out_cell(LOG_PORT, 0x000099BE);               // BAD: источник
        }
    } else {
        out_cell(LOG_PORT, 0x000099BF);                   // BAD: акцент
    }

    // ---- команды терминала: dir -> FS_LIST, type -> FILE_GET ----
    run Init_Cmds();
    if (Cmd_Count == 0x0000000C) {
        Cmd_Tag = 0x20524944;                             // 'DIR '
        run Find_Cmd();
        Dir_Target = Cmd_Target;
        Dir_Kind = Cmd_Kind;
        Cmd_Tag = 0x45505954;                             // 'TYPE'
        run Find_Cmd();
        Tmp_C = Cmd_Target;
        Tmp_D = Cmd_Kind;
        if (Dir_Target == FS_LIST) {
            if (Dir_Kind == KIND_FS) {
                if (Tmp_C == NID_GET) {
                    if (Tmp_D == KIND_SYS) {
                        out_cell(LOG_PORT, 0x00009F1D);   // таблица команд честная
                    } else {
                        out_cell(LOG_PORT, 0x000099C0);   // BAD: kind TYPE
                    }
                } else {
                    out_cell(LOG_PORT, 0x000099C1);       // BAD: TYPE не syscall
                }
            } else {
                out_cell(LOG_PORT, 0x000099C2);           // BAD: kind DIR
            }
        } else {
            out_cell(LOG_PORT, 0x000099C3);               // BAD: DIR не FS-операция
        }
    } else {
        out_cell(LOG_PORT, 0x000099C4);                   // BAD: число команд
    }

    // ---- неизвестная команда: честный отказ ----
    Cmd_Tag = 0x204F4843;                                 // 'CHO '
    run Find_Cmd();
    if (Cmd_Found == 0x00000000) {
        out_cell(LOG_PORT, 0x00009F1F);                   // отказ 0x7110 честный
    } else {
        out_cell(LOG_PORT, 0x000099C5);                   // BAD: чужая команда найдена
    }

    // ---- неизвестный узел: честный отказ ----
    Node_Id = 0x00000063;                                 // 99
    run Resolve_Node();
    run Read_Props();
    if (Found_Addr == 0x00000000) {
        out_cell(LOG_PORT, 0x00009FF0);                   // отказ по узлу честный
    } else {
        out_cell(LOG_PORT, 0x000099C6);                   // BAD: нашли несуществующий
    }

    out_cell(LOG_PORT, 0x00009FFF);      // LOG: explorer DONE
    terminate;
}

// ---------- дерево ----------
function Put_Node() {
    store_ind(Ptr, N_Id);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Parent);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Tag);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Kind);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Size);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Mtime);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Flags);
    Ptr = Ptr + 4;
    store_ind(Ptr, N_Seal);
    Ptr = Ptr + 4;
    Node_Count = Node_Count + 1;
}

function Init_Tree() {
    Ptr = EXPL_TREE;
    Node_Count = 0x00000000;

    // 1 ROOT (hd0, смонтирован)
    N_Id = 0x00000001;
    N_Parent = 0x00000000;
    N_Tag = TAG_ROOT;
    N_Kind = K_MOUNT;
    N_Size = 0x00000000;
    N_Mtime = 0x00010000;
    N_Flags = F_OK;
    N_Seal = 0x00000000;
    run Put_Node();

    // 2 APPs
    N_Id = 0x00000002;
    N_Parent = 0x00000001;
    N_Tag = TAG_APPS;
    N_Kind = K_DIR;
    N_Size = 0x00000000;
    N_Mtime = 0x00010001;
    N_Flags = F_OK;
    N_Seal = 0x00000000;
    run Put_Node();

    // 3 Data
    N_Id = 0x00000003;
    N_Parent = 0x00000001;
    N_Tag = TAG_DATA;
    N_Kind = K_DIR;
    N_Size = 0x00000000;
    N_Mtime = 0x00010002;
    N_Flags = F_OK;
    N_Seal = 0x00000000;
    run Put_Node();

    // 4 THMs
    N_Id = 0x00000004;
    N_Parent = 0x00000001;
    N_Tag = TAG_THMS;
    N_Kind = K_DIR;
    N_Size = 0x00000000;
    N_Mtime = 0x00010003;
    N_Flags = F_OK;
    N_Seal = 0x00000000;
    run Put_Node();

    // 5 Game
    N_Id = 0x00000005;
    N_Parent = 0x00000001;
    N_Tag = TAG_GAME;
    N_Kind = K_DIR;
    N_Size = 0x00000000;
    N_Mtime = 0x00010004;
    N_Flags = F_OK;
    N_Seal = 0x00000000;
    run Put_Node();

    // 6 Save
    N_Id = 0x00000006;
    N_Parent = 0x00000005;
    N_Tag = TAG_SAVE;
    N_Kind = K_DIR;
    N_Size = 0x00000000;
    N_Mtime = 0x00010005;
    N_Flags = F_OK;
    N_Seal = 0x00000000;
    run Put_Node();

    // 7 SYS (системная папка, RO для ren)
    N_Id = 0x00000007;
    N_Parent = 0x00000001;
    N_Tag = TAG_SYS;
    N_Kind = K_SYSDIR;
    N_Size = 0x00000000;
    N_Mtime = 0x00010006;
    N_Flags = F_OK;
    N_Seal = 0x00000000;
    run Put_Node();

    // 8 APPb — файл приложения, 512 слов
    N_Id = 0x00000008;
    N_Parent = 0x00000002;
    N_Tag = TAG_APPB;
    N_Kind = K_FILE;
    N_Size = 0x00000200;
    N_Mtime = 0x00010007;
    N_Flags = F_OK;
    N_Seal = 0x00000001;
    run Put_Node();

    // 9 MANf — манифест, 16 слов
    N_Id = 0x00000009;
    N_Parent = 0x00000002;
    N_Tag = TAG_MANF;
    N_Kind = K_FILE;
    N_Size = 0x00000010;
    N_Mtime = 0x00010008;
    N_Flags = F_OK;
    N_Seal = 0x00000002;
    run Put_Node();

    // 10 THm1 — тема, 32 слова
    N_Id = 0x0000000A;
    N_Parent = 0x00000004;
    N_Tag = TAG_THM1;
    N_Kind = K_FILE;
    N_Size = 0x00000020;
    N_Mtime = 0x00010009;
    N_Flags = F_OK;
    N_Seal = 0x00000003;
    run Put_Node();

    // 11 THm2 — тема, 40 слов
    N_Id = 0x0000000B;
    N_Parent = 0x00000004;
    N_Tag = TAG_THM2;
    N_Kind = K_FILE;
    N_Size = 0x00000028;
    N_Mtime = 0x0001000A;
    N_Flags = F_OK;
    N_Seal = 0x00000004;
    run Put_Node();

    // 12 SAv1 — сохранение, 4 слова
    N_Id = 0x0000000C;
    N_Parent = 0x00000006;
    N_Tag = TAG_SAV1;
    N_Kind = K_FILE;
    N_Size = 0x00000004;
    N_Mtime = 0x0001000B;
    N_Flags = F_OK;
    N_Seal = 0x00000005;
    run Put_Node();

    // 13 MSD0 — внешняя карта ms0 (смонтирована, TKT-019)
    N_Id = 0x0000000D;
    N_Parent = 0x00000000;
    N_Tag = TAG_MSD0;
    N_Kind = K_MOUNT;
    N_Size = 0x00000000;
    N_Mtime = 0x0001000C;
    N_Flags = F_OK;
    N_Seal = 0x00000000;
    run Put_Node();

    // 14..19 — шесть игр карты ms0
    N_Id = 0x0000000E;
    N_Parent = 0x0000000D;
    N_Tag = TAG_GM01;
    N_Kind = K_FILE;
    N_Size = 0x00000400;
    N_Mtime = 0x0001000D;
    N_Flags = F_OK;
    N_Seal = 0x00000006;
    run Put_Node();

    N_Id = 0x0000000F;
    N_Parent = 0x0000000D;
    N_Tag = TAG_GM02;
    N_Kind = K_FILE;
    N_Size = 0x00000800;
    N_Mtime = 0x0001000E;
    N_Flags = F_OK;
    N_Seal = 0x00000007;
    run Put_Node();

    N_Id = 0x00000010;
    N_Parent = 0x0000000D;
    N_Tag = TAG_GM03;
    N_Kind = K_FILE;
    N_Size = 0x00000200;
    N_Mtime = 0x0001000F;
    N_Flags = F_OK;
    N_Seal = 0x00000008;
    run Put_Node();

    N_Id = 0x00000011;
    N_Parent = 0x0000000D;
    N_Tag = TAG_GM04;
    N_Kind = K_FILE;
    N_Size = 0x00000100;
    N_Mtime = 0x00010010;
    N_Flags = F_OK;
    N_Seal = 0x00000009;
    run Put_Node();

    N_Id = 0x00000012;
    N_Parent = 0x0000000D;
    N_Tag = TAG_GM05;
    N_Kind = K_FILE;
    N_Size = 0x00000080;
    N_Mtime = 0x00010011;
    N_Flags = F_OK;
    N_Seal = 0x0000000A;
    run Put_Node();

    N_Id = 0x00000013;
    N_Parent = 0x0000000D;
    N_Tag = TAG_GM06;
    N_Kind = K_FILE;
    N_Size = 0x00000040;
    N_Mtime = 0x00010012;
    N_Flags = F_OK;
    N_Seal = 0x0000000B;
    run Put_Node();

    // 20 RECy — корзина (честная системная папка)
    N_Id = 0x00000014;
    N_Parent = 0x00000001;
    N_Tag = TAG_RECY;
    N_Kind = K_SYSDIR;
    N_Size = 0x00000000;
    N_Mtime = 0x00010013;
    N_Flags = F_OK;
    N_Seal = 0x00000000;
    run Put_Node();
}

// «Быстрый доступ»: 4 честные ссылки (id, exists)
function Init_Quick() {
    Ptr = QUICK;
    store_ind(Ptr, 0x00000002);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000003);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000004);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000006);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);
    Ptr = Ptr + 4;
}

// ---------- общий поиск узла по id ----------
function Resolve_Node() {
    Found_Addr = 0x00000000;
    Found_Parent = 0x00000000;
    Found_Tag = 0x00000000;
    Found_Kind = 0x00000000;
    Found_Size = 0x00000000;
    Found_Mtime = 0x00000000;
    Found_Flags = 0x00000000;
    Found_Seal = 0x00000000;
    Ptr = EXPL_TREE;
    Idx = 0x00000000;
    run Resolve_Loop();
}

function Resolve_Loop() {
    if (Idx == Node_Count) {
        // честный конец дерева
    } else {
        Tmp_A = in_cell(Ptr);
        if (Tmp_A == Node_Id) {
            Found_Addr = Ptr;
            Tmp_B = Ptr;
            Tmp_B = Tmp_B + 4;
            Found_Parent = in_cell(Tmp_B);
            Tmp_B = Tmp_B + 4;
            Found_Tag = in_cell(Tmp_B);
            Tmp_B = Tmp_B + 4;
            Found_Kind = in_cell(Tmp_B);
            Tmp_B = Tmp_B + 4;
            Found_Size = in_cell(Tmp_B);
            Tmp_B = Tmp_B + 4;
            Found_Mtime = in_cell(Tmp_B);
            Tmp_B = Tmp_B + 4;
            Found_Flags = in_cell(Tmp_B);
            Tmp_B = Tmp_B + 4;
            Found_Seal = in_cell(Tmp_B);
        } else {
            Ptr = Ptr + 32;
            Idx = Idx + 1;
            run Resolve_Loop();
        }
    }
}

// ---------- хлебные крошки: лист -> корень, затем честный разворот ----------
function Build_Crumbs() {
    Crumb_Ptr = CRUMBS;
    Crumb_Count = 0x00000000;
    Cur_Id = Sel_Id;
    run Crumb_Up();
    A_Ptr = CRUMBS;
    B_Ptr = CRUMBS;
    Idx = 0x00000001;
    run Crumb_Seek_End();
    run Crumb_Swap();
}

function Crumb_Up() {
    store_ind(Crumb_Ptr, Cur_Id);
    Crumb_Ptr = Crumb_Ptr + 4;
    Crumb_Count = Crumb_Count + 1;
    Node_Id = Cur_Id;
    run Resolve_Node();
    if (Found_Parent == 0x00000000) {
        // корень записан — готово
    } else {
        Cur_Id = Found_Parent;
        run Crumb_Up();
    }
}

function Crumb_Seek_End() {
    if (Idx == Crumb_Count) {
        // B_Ptr на последнем сегменте
    } else {
        B_Ptr = B_Ptr + 4;
        Idx = Idx + 1;
        run Crumb_Seek_End();
    }
}

function Crumb_Swap() {
    Tmp_A = B_Ptr;
    Tmp_A = Tmp_A + 4;
    if (A_Ptr == Tmp_A) {
        // чётное число: указатели разошлись
    } else {
        if (A_Ptr == B_Ptr) {
            // нечётный центр — готово
        } else {
            Tmp_B = in_cell(A_Ptr);
            Tmp_C = in_cell(B_Ptr);
            store_ind(A_Ptr, Tmp_C);
            store_ind(B_Ptr, Tmp_B);
            A_Ptr = A_Ptr + 4;
            B_Ptr = B_Ptr - 4;
            run Crumb_Swap();
        }
    }
}

// ---------- колонки папки ----------
function List_Children() {
    List_Ptr = COLUMNS;
    List_Count = 0x00000000;
    List_Overflow = 0x00000000;
    Ptr = EXPL_TREE;
    Idx = 0x00000000;
    run List_Loop();
}

function List_Loop() {
    if (Idx == Node_Count) {
        // обход закончен
    } else {
        Tmp_A = Ptr;
        Tmp_A = Tmp_A + 4;
        Tmp_B = in_cell(Tmp_A);
        if (Tmp_B == Dir_Id) {
            if (List_Count == 0x00000004) {
                if (List_Overflow == 0x00000000) {
                    out_cell(LOG_PORT, E_LIST);      // честный отказ ёмкости
                } else {
                    // уже сообщили — не дублируем
                }
                List_Overflow = 0x00000001;
                Ptr = Ptr + 32;
                Idx = Idx + 1;
                run List_Loop();
            } else {
                Tmp_B = in_cell(Ptr);
                store_ind(List_Ptr, Tmp_B);
                List_Ptr = List_Ptr + 4;
                List_Count = List_Count + 1;
                Ptr = Ptr + 32;
                Idx = Idx + 1;
                run List_Loop();
            }
        } else {
            Ptr = Ptr + 32;
            Idx = Idx + 1;
            run List_Loop();
        }
    }
}

// ---------- поиск по имени (по дереву в памяти) ----------
function Search_Tree() {
    Search_Ptr = SEARCH;
    Search_Count = 0x00000000;
    Ptr = EXPL_TREE;
    Idx = 0x00000000;
    run Search_Loop();
}

function Search_Loop() {
    if (Idx == Node_Count) {
        // готово
    } else {
        Tmp_A = Ptr;
        Tmp_A = Tmp_A + 8;
        Tmp_B = in_cell(Tmp_A);
        if (Tmp_B == Search_Tag) {
            Tmp_B = in_cell(Ptr);
            store_ind(Search_Ptr, Tmp_B);
            Search_Ptr = Search_Ptr + 4;
            Search_Count = Search_Count + 1;
        } else {
            // не совпало — честно идём дальше
        }
        Ptr = Ptr + 32;
        Idx = Idx + 1;
        run Search_Loop();
    }
}

// ---------- свойства ----------
function Read_Props() {
    Props_Ptr = PROPS;
    run Resolve_Node();
    if (Found_Addr == 0x00000000) {
        out_cell(LOG_PORT, E_NODE);
    } else {
        store_ind(Props_Ptr, Node_Id);
        Props_Ptr = Props_Ptr + 4;
        store_ind(Props_Ptr, Found_Kind);
        Props_Ptr = Props_Ptr + 4;
        store_ind(Props_Ptr, Found_Size);
        Props_Ptr = Props_Ptr + 4;
        store_ind(Props_Ptr, Found_Mtime);
        Props_Ptr = Props_Ptr + 4;
        store_ind(Props_Ptr, Found_Flags);
        Props_Ptr = Props_Ptr + 4;
        store_ind(Props_Ptr, Found_Seal);
    }
}

// ---------- корзина: перенос, возврат, явная очистка ----------
function Recycle_Node() {
    run Resolve_Node();
    if (Found_Addr == 0x00000000) {
        out_cell(LOG_PORT, E_NODE);
    } else {
        Orig_Parent = Found_Parent;
        Tmp_A = Found_Addr;
        Tmp_A = Tmp_A + 4;
        store_ind(Tmp_A, 0x00000014);
        Tmp_A = Found_Addr;
        Tmp_A = Tmp_A + 24;
        store_ind(Tmp_A, F_RECY);
        store_ind(Rec_Ptr, Node_Id);
        Rec_Ptr = Rec_Ptr + 4;
        store_ind(Rec_Ptr, Orig_Parent);
        Rec_Ptr = Rec_Ptr + 4;
        store_ind(Rec_Ptr, Found_Tag);
        Rec_Ptr = Rec_Ptr + 4;
        store_ind(Rec_Ptr, Found_Size);
        Rec_Ptr = Rec_Ptr + 4;
        Rec_Count = Rec_Count + 1;
    }
}

// найти запись корзины по Node_Id -> Rec_Found, Rec_Orig
function Find_Rec() {
    Rec_Found = 0x00000000;
    Rec_Orig = 0x00000000;
    Rec_Walk = RECYCLE;
    Rec_Idx = 0x00000000;
    run Find_Rec_Loop();
}

function Find_Rec_Loop() {
    if (Rec_Idx == Rec_Count) {
        // запись не найдена — честный отказ
    } else {
        Tmp_A = in_cell(Rec_Walk);
        if (Tmp_A == Node_Id) {
            Rec_Found = Rec_Walk;
            Tmp_B = Rec_Walk;
            Tmp_B = Tmp_B + 4;
            Rec_Orig = in_cell(Tmp_B);
        } else {
            Rec_Walk = Rec_Walk + 16;
            Rec_Idx = Rec_Idx + 1;
            run Find_Rec_Loop();
        }
    }
}

function Restore_Node() {
    run Find_Rec();
    if (Rec_Found == 0x00000000) {
        out_cell(LOG_PORT, E_RESTORE);
    } else {
        run Resolve_Node();
        Tmp_A = Found_Addr;
        Tmp_A = Tmp_A + 4;
        store_ind(Tmp_A, Rec_Orig);
        Tmp_A = Found_Addr;
        Tmp_A = Tmp_A + 24;
        store_ind(Tmp_A, F_OK);
        store_ind(Rec_Found, 0x00000000);
    }
}

function Purge_Recycle() {
    if (Empty_Flag == 0x00000000) {
        out_cell(LOG_PORT, E_PURGE);
    } else {
        Rec_Walk = RECYCLE;
        Purge_Idx = 0x00000000;
        run Purge_Loop();
        Rec_Count = 0x00000000;
        Rec_Ptr = RECYCLE;
    }
}

function Purge_Loop() {
    if (Purge_Idx == 0x00000008) {
        // максимум записей просмотрен
    } else {
        Tmp_A = in_cell(Rec_Walk);
        if (Tmp_A == 0x00000000) {
            Rec_Walk = Rec_Walk + 16;
            Purge_Idx = Purge_Idx + 1;
            run Purge_Loop();
        } else {
            Node_Id = Tmp_A;
            run Resolve_Node();
            if (Found_Addr == 0x00000000) {
                Rec_Walk = Rec_Walk + 16;
                Purge_Idx = Purge_Idx + 1;
                run Purge_Loop();
            } else {
                Tmp_B = Found_Addr;
                Tmp_B = Tmp_B + 4;
                store_ind(Tmp_B, 0xFFFFFFFF);     // честный признак: места нет
                Tmp_B = Found_Addr;
                Tmp_B = Tmp_B + 16;
                store_ind(Tmp_B, 0x00000000);
                Tmp_B = Found_Addr;
                Tmp_B = Tmp_B + 24;
                store_ind(Tmp_B, F_PURGED);
                store_ind(Rec_Walk, 0x00000000);
                Rec_Walk = Rec_Walk + 16;
                Purge_Idx = Purge_Idx + 1;
                run Purge_Loop();
            }
        }
    }
}

// ---------- переименование ----------
function Rename_Node() {
    run Resolve_Node();
    if (Found_Addr == 0x00000000) {
        out_cell(LOG_PORT, E_NODE);
    } else {
        if (Found_Kind == K_SYSDIR) {
            out_cell(LOG_PORT, E_RENAME);
        } else {
            if (Found_Kind == K_SYSFILE) {
                out_cell(LOG_PORT, E_RENAME);
            } else {
                Tmp_A = Found_Addr;
                Tmp_A = Tmp_A + 8;
                store_ind(Tmp_A, New_Tag);
            }
        }
    }
}

// ---------- тема: акцент из общей ячейки оболочки ----------
function Init_Theme() {
    Theme_Acc = in_cell(SHELL_PAL);
    Theme_Src = TAG_SHEL;
    Ptr = THEME;
    store_ind(Ptr, Theme_Acc);
    Ptr = Ptr + 4;
    store_ind(Ptr, Theme_Src);
}

// ---------- команды терминала Windows-style ----------
function Put_Cmd() {
    store_ind(Cmd_Ptr, Cmd_Tag);
    Cmd_Ptr = Cmd_Ptr + 4;
    store_ind(Cmd_Ptr, Cmd_Target);
    Cmd_Ptr = Cmd_Ptr + 4;
    store_ind(Cmd_Ptr, Cmd_Kind);
    Cmd_Ptr = Cmd_Ptr + 4;
    Cmd_Count = Cmd_Count + 1;
}

function Init_Cmds() {
    Cmd_Ptr = CMDS;
    Cmd_Count = 0x00000000;

    // dir — список папки в памяти (внутренняя FS-операция)
    Cmd_Tag = 0x20524944;
    Cmd_Target = FS_LIST;
    Cmd_Kind = KIND_FS;
    run Put_Cmd();

    // cd — переход (внутренняя)
    Cmd_Tag = 0x20204443;
    Cmd_Target = FS_CD;
    Cmd_Kind = KIND_FS;
    run Put_Cmd();

    // type — настоящее чтение слова исходника (FILE_GET)
    Cmd_Tag = 0x45505954;
    Cmd_Target = NID_GET;
    Cmd_Kind = KIND_SYS;
    run Put_Cmd();

    // copy — настоящая запись артефакта (FILE_BEGIN..FILE_END)
    Cmd_Tag = 0x59504F43;
    Cmd_Target = NID_BEGIN;
    Cmd_Kind = KIND_SYS;
    run Put_Cmd();

    // del — в корзину (внутренняя, перенос)
    Cmd_Tag = 0x204C4544;
    Cmd_Target = FS_DEL;
    Cmd_Kind = KIND_FS;
    run Put_Cmd();

    // ren — переименование (внутренняя)
    Cmd_Tag = 0x204E4552;
    Cmd_Target = FS_REN;
    Cmd_Kind = KIND_FS;
    run Put_Cmd();

    // md — создать папку (внутренняя)
    Cmd_Tag = 0x2020444D;
    Cmd_Target = FS_MD;
    Cmd_Kind = KIND_FS;
    run Put_Cmd();

    // rd — удалить папку (внутренняя)
    Cmd_Tag = 0x20204452;
    Cmd_Target = FS_RD;
    Cmd_Kind = KIND_FS;
    run Put_Cmd();

    // cls — очистить экран (внутренняя)
    Cmd_Tag = 0x20534C43;
    Cmd_Target = FS_CLS;
    Cmd_Kind = KIND_FS;
    run Put_Cmd();

    // mnt — перечитать монтирования (внутренняя)
    Cmd_Tag = 0x20544E4D;
    Cmd_Target = FS_MNT;
    Cmd_Kind = KIND_FS;
    run Put_Cmd();

    // ver — контрольное слово артефакта (FILE_SEAL)
    Cmd_Tag = 0x20524556;
    Cmd_Target = NID_SEAL;
    Cmd_Kind = KIND_SYS;
    run Put_Cmd();

    // seek — позиция записи (FILE_SEEK)
    Cmd_Tag = 0x4B454553;
    Cmd_Target = NID_SEEK;
    Cmd_Kind = KIND_SYS;
    run Put_Cmd();
}

function Find_Cmd() {
    Cmd_Found = 0x00000000;
    Cmd_Target = 0x00000000;
    Cmd_Kind = 0x00000000;
    Cmd_Ptr = CMDS;
    Idx = 0x00000000;
    run Find_Cmd_Loop();
}

function Find_Cmd_Loop() {
    if (Idx == Cmd_Count) {
        out_cell(LOG_PORT, E_CMD);           // честный отказ: нет такой команды
    } else {
        Tmp_A = in_cell(Cmd_Ptr);
        if (Tmp_A == Cmd_Tag) {
            Cmd_Found = Cmd_Ptr;
            Tmp_B = Cmd_Ptr;
            Tmp_B = Tmp_B + 4;
            Cmd_Target = in_cell(Tmp_B);
            Tmp_B = Tmp_B + 4;
            Cmd_Kind = in_cell(Tmp_B);
        } else {
            Cmd_Ptr = Cmd_Ptr + 12;
            Idx = Idx + 1;
            run Find_Cmd_Loop();
        }
    }
}
