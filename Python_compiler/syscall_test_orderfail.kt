// ЧЕСТНЫЙ ОТРИЦАТЕЛЬНЫЙ ТЕСТ 1.5: FILE_PUT до FILE_BEGIN ->
// VM обязана честно забраковать порядок syscall, не молча писать в никуда.
#core: CtOs_Old
#target: ARM32

#define: FILE_PUT 0x00000131

set static Stream_Emit = 0x000000CD;

pub entry main(cell:raw args) {
    sys_call(FILE_PUT);   // брак: BEGIN не был вызван
    terminate;
}
