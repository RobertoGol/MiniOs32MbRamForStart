// ===================================================================
// Честный негатив Ф3: TIMER_RET (0x154) без открытого тика.
// Оба исполнителя обязаны отказать: это IRET без IRQ.
//   native_rt.c: "TIMER_RET: открытого тика нет (IRET без IRQ)"
//   ctos_vm.py : "TIMER_RET: честный брак — открытого тика нет ..."
// Общий needle в гейте: "TIMER_RET".
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: STREAM_CELL 0x00F00FF0
#define: NID_TRET    0x00000154
#define: TRAP_BLOCK  0x00A12900

set static A = 0x00000000;

pub entry main(cell:raw args) {
    A = TRAP_BLOCK;
    log_cell(STREAM_CELL, A);
    sys_call(NID_TRET);              // честный брак: тик не открыт
    terminate;
}
