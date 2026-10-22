// ЧЕСТНЫЙ ОТРИЦАТЕЛЬНЫЙ ТЕСТ 1.5: артефакт не закрыт (нет FILE_END) ->
// VM обязана честно забраковать в конце прогона, а не тихо оставить файл.
#core: CtOs_Old
#target: ARM32

#define: FILE_BEGIN 0x00000130
#define: FILE_PUT   0x00000131

set static Stream_Emit = 0x00000000;

pub entry main(cell:raw args) {
    sys_call(FILE_BEGIN);
    Stream_Emit = 0x000000AB;
    sys_call(FILE_PUT);

    // FILE_END честно НЕ вызван — это и есть проверяемый брак.
    terminate;
}
