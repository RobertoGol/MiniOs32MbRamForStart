// ===================================================================
// СТАДИЯ-1.5: честный артефакт-файл бинаря (sys_call -> файл-воркер VM)
// Файл: syscall_test.kt | Язык: KINII (подмножество стадии-0)
//
// Честный протокол файл-слоя (opcodes.core, OP_SYSCALL 0x13):
//   NID 0x00000130 FILE_BEGIN — открыть честный артефакт `<бинарь>.out`
//   NID 0x00000131 FILE_PUT   — слово Stream_Emit -> 4 байта BE
//   NID 0x00000132 FILE_U16   — младшие 16 бит Stream_Emit -> 2 байта BE
//   NID 0x00000135 FILE_SEAL  — честное контрольное слово CRC-32 (TKT-040 веха-1)
//   NID 0x00000133 FILE_END   — закрыть артефакт (не вызван -> честный брак)
//
// Аргумент syscall честно живёт в ячейке Stream_Emit (0x00F00FF0 — фиксированный
// хвост зоны переменных, вне бегунка; адреса обычных set static не сдвигаются):
//
// Честная проверка теста: заголовок 20 байт по контракту TKT-009 v1.1:
//   'CTOS'(4) + ver(2) + target(2) + entry(4) + 0xAAAAFFFF(4) + crc(4, LE)
//   = 43 54 4F 53 | 01 01 | 02 00 | 14 00 00 00 | FF FF AA AA | 00 00 00 00
//   (ноль силом FILE_SEAL запечатает честно).
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: FILE_BEGIN 0x00000130
#define: FILE_PUT   0x00000131
#define: FILE_U16   0x00000132
#define: FILE_SEAL  0x00000135
#define: FILE_END   0x00000133

set static Stream_Emit = 0x00000000;  // честная ячейка-аргумент syscall
set static Tmp_Read    = 0x00000000;

pub entry main(cell:raw args) {
    sys_call(FILE_BEGIN);                             // артефакт открыт

    Stream_Emit = 0x43544F53;                         // 'CTOS' BE
    sys_call(FILE_PUT);                               // +4 байта = 4
    Stream_Emit = 0x00000101;                         // v1.1 — с контролем целостности
    sys_call(FILE_U16);                               // +2 байта = 6
    Stream_Emit = 0x00000200;                         // байт-образ таргета 02 00
    sys_call(FILE_U16);                               // +2 байта = 8
    Stream_Emit = 0x14000000;                         // байт-образ entry 14 00 00 00 (0x14)
    sys_call(FILE_PUT);                               // +4 байта = 12
    Stream_Emit = 0xFFFFAAAA;                         // байт-образ магии FF FF AA AA
    sys_call(FILE_PUT);                               // +4 байта = 16
    Stream_Emit = 0x00000000;                         // контрольное слово: плейсхолдер
    sys_call(FILE_U16);                               // +2 байта = 18
    sys_call(FILE_U16);                               // +2 байта = 20

    sys_call(FILE_SEAL);                              // честная печать CRC-32 тела
    sys_call(FILE_END);                               // артефакт закрыт

    terminate;
}
