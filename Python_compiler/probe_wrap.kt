// ===================================================================
// probe_wrap.kt — честная проба 32-битного слова стадии-0 (VM)
//
// Реальный честный баг, найденный 2026-11-01 на TKT-039: аккумулятор
// стадии-0 не обрезался до 32 бит, и в ячейку могло лечь 36-битное
// значение (0x4DD99B07D) — нарушение контракта слова (4 байта).
//
// Проба: 0xFFFFFFFF + 0xFFFFFFFF + 2 обязано честно дать 0 (перенос
// за 32 бита теряется, как на настоящем железе), а не 0x200000000.
// ===================================================================
#core: CtOs_Old
#target: ARM32

#define: LOG_PORT 0x3F0050C0
#define: BUF      0x00E70000

set static Ptr  = 0x00000000;
set static Sum  = 0x00000000;
set static Left = 0x00000000;
set static Tmp  = 0x00000000;

pub entry main(cell:raw args) {
    Ptr = BUF;
    Tmp = 0xFFFFFFFF;
    store_ind(Ptr, Tmp);
    Ptr = Ptr + 4;
    store_ind(Ptr, Tmp);
    Ptr = Ptr + 4;
    Tmp = 0x00000002;
    store_ind(Ptr, Tmp);
    Ptr = Ptr + 4;

    Ptr = BUF;
    Sum = 0x00000000;
    Left = 0x00000003;
    run Sum_Loop();

    if (Sum == 0x00000000) {
        out_cell(LOG_PORT, 0x00009E01);  // WRAP: перенос честно потерян
    } else {
        out_cell(LOG_PORT, 0x00009901);  // WRAP: слово шире 32 бит — брак
        log_cell(LOG_PORT, Sum);
    }
    terminate;
}

function Sum_Loop() {
    if (Left == 0x00000000) {
        // готово
    } else {
        Tmp = in_cell(Ptr);
        Sum = Sum + Tmp;
        Ptr = Ptr + 4;
        Left = Left - 1;
        run Sum_Loop();
    }
}
