// ЧЕСТНЫЙ ОТРИЦАТЕЛЬНЫЙ ТЕСТ: sys_call(переменная) — адрес ячейки нельзя
// подсовывать как честный NID драйвера. Ожидаем честный [CODEGEN ERROR], exit 1.
#core: CtOs_Old
#target: ARM32

#define: FILE_BEGIN 0x00000130

set static Stream_Emit = 0x00000000;
set static Bad_NID     = 0x00000130;

pub entry main(cell:raw args) {
    sys_call(Bad_NID);   // честный брак: это переменная, а не NID
    terminate;
}
