/* CtOS A3b — legacy-BIOS MBR (512 Б, entry 0x7C00).
 * Настоящий код, не псевдокод: проверяет INT 13h AH=41h (EDD), читает
 * 4 сектора stage2 с LBA 1 в 0x1000:0000 и передаёт управление far jump.
 * При отказе честно пишет диагностику в VGA и выдаёт QEMU debug-exit.
 */
.code16
.section .text
.global _start

_start:
    xor %ax, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %ss
    mov $0x7B00, %sp
    mov %dl, drive
    mov %dl, 0x7DB0          /* честная передача номера диска в stage2 */

    /* EDD: INT 13h AH=41h, BX=55AAh; возврат BX=AA55h, CX bit0 = read */
    mov $0x41, %ah
    mov $0x55AA, %bx
    int $0x13
    jc edd_fail
    cmp $0xAA55, %bx
    jne edd_fail
    test $1, %cl
    jz edd_fail

    /* EDD read: 4 сектора LBA 1 -> 0x1000:0000 */
    mov $dap, %si
    mov $0x42, %ah
    mov drive, %dl
    int $0x13
    jc read_fail

    mov $msg_ok, %si
    call puts_bios
    ljmp $0x1000, $0x0000

puts_bios:
    mov $0x0E, %ah
    mov $0x0007, %bx
1:
    lodsb
    test %al, %al
    jz 2f
    int $0x10
    jmp 1b
2:
    ret

edd_fail:
    mov $msg_edd, %si
    call puts_bios
    jmp fail_exit
read_fail:
    mov $msg_read, %si
    call puts_bios
fail_exit:
    mov $0xF4, %dx           /* isa-debug-exit только в QEMU; rc = (AX<<1)|1 */
    mov $0x0012, %ax
    out %ax, %dx
halt:
    hlt
    jmp halt

drive:  .byte 0
dap:
    .byte 0x10, 0x00         /* размер DAP, зарезервировано */
    .word 4                  /* число секторов */
    .word 0x0000             /* смещение буфера */
    .word 0x1000             /* сегмент буфера */
    .quad 1                  /* LBA */

msg_ok:   .asciz "CTOS A3b MBR OK\r\n"
msg_edd:  .asciz "CTOS A3b MBR: NO EDD\r\n"
msg_read: .asciz "CTOS A3b MBR: READ FAIL\r\n"
