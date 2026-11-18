/* A4a: плоский 32-битный рантайм. Код/данные грузятся BIOS по 0x40000,
 * BSS лежит далеко от стека 0x90000 и VGA 0xB8000. */
SECTIONS
{
  .text 0x00040000 : { *(.text) *(.text*) }
  .rdata : { *(.rdata) *(.rdata*) }
  .data : { *(.data) *(.data*) }
  .bss 0x01000000 :
  {
    _bss_start = .;
    *(.bss)
    *(.bss*)
    *(COMMON)
    _bss_end = .;
  }
  /DISCARD/ : { *(.reloc) *(.pdata) *(.xdata) }
}
