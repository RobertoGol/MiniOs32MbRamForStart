/* CtOS A3b/A4a — legacy-BIOS stage2 (LBA 1..4, 0x1000:0000).
 * Настоящий код, не псевдокод. Читает CTMD с LBA 8 (64 сектора в 0x2000:0000),
 * проверяет magic/каталог и CRC-32 каждого тела, затем грузит плоский PM-рантайм
 * с LBA 72 (0x4000:0000), переходит в защищённый режим и передаёт управление
 * main() нативного интерпретатора. isa-debug-exit — только контроль QEMU.
 */
/* stage2 исполняется по физическому 0x10000 = сегмент 0x1000:0 */
.set stage2_base, 0x10000
.set pm_lba, 72
.set pm_sectors, 64
.set pm_load_seg, 0x4000

.code16
.section .text
.global _start

_start:
    /* MBR положил номер диска по 0x7DB0; DS здесь ещё 0. */
    mov 0x7DB0, %dl
    /* Теперь все метки stage2 живут в 0x1000:... — включая DAP и строки. */
    mov $0x1000, %ax
    mov %ax, %ds
    mov %ax, %es
    mov $0xF000, %sp
    mov %dl, drive

    call com_init
    mov $msg_stage2, %si
    call puts

    /* EDD ещё раз; BIOS INT 10h мог заменить DL — берём его из переменной. */
    mov drive, %dl
    mov $0x41, %ah
    mov $0x55AA, %bx
    int $0x13
    jc edd_fail
    cmp $0xAA55, %bx
    jne edd_fail
    test $1, %cl
    jz edd_fail

    /* 64 сектора CTMD: LBA 8 -> 0x2000:0000 (32768 Б > 28425 Б образа). */
    mov $dap_ctmd, %si
    mov $0x42, %ah
    mov drive, %dl
    int $0x13
    jc read_fail

    /* DS уже указывает на данные stage2; ES переводим на CTMD. */
    mov $0x2000, %ax
    mov %ax, %es

    cmpl $0x444D5443, %es:0x0   /* 'CTMD' little-endian */
    jne magic_fail
    mov %es:0x8, %eax
    mov %eax, ctmd_count
    cmp $32, %eax
    ja count_fail

    mov $msg_count, %si
    call puts
    mov ctmd_count, %eax       /* puts мог испортить EAX */
    call print_hex32
    mov $msg_nl, %si
    call puts

    movw $0, entry_index
entry_loop:
    movzwl entry_index, %eax
    mov $48, %ebx
    mul %ebx                    /* EAX = i * 48 */
    add $12, %eax               /* каталог начинается с image+12 */
    mov %ax, entry_off

    /* Сначала берём смещение из данных stage2, затем печатаем имя с DS=0x2000. */
    movzwl entry_off, %esi
    push %ds
    mov $0x2000, %ax
    mov %ax, %ds
    call puts
    pop %ds
    mov $msg_space, %si
    call puts

    movzwl entry_off, %esi
    mov %es:0x20(%esi), %ax    /* LE32 offset, младшие 16 бит */
    mov %ax, body_off
    mov %es:0x24(%esi), %ax    /* LE32 length, младшие 16 бит */
    mov %ax, body_len
    mov %es:0x28(%esi), %edx   /* LE32 CRC-32 тела */
    mov %edx, want_crc

    movzwl body_off, %eax
    movzwl body_len, %ebx
    add %ebx, %eax
    cmp $0x10000, %eax         /* прочитали ровно 64 КБ */
    ja bounds_bad

    mov $0x2000, %ax
    mov %ax, %es
    movzwl body_off, %esi
    movzwl body_len, %ecx
    call crc32_body
    mov want_crc, %edx
    cmpl crc_result, %edx
    jne crc_bad
    mov $msg_crc_ok, %si
    call puts
    jmp next_entry

bounds_bad:
    mov $msg_bounds_bad, %si
    call puts
    movw $1, bad
    jmp next_entry
crc_bad:
    mov $msg_crc_bad, %si
    call puts
    movw $1, bad

next_entry:
    incw entry_index
    movzwl entry_index, %eax
    mov ctmd_count, %ebx
    cmp %ebx, %eax
    jb entry_loop

    cmpw $0, bad
    jne all_bad
    mov $msg_all_ok, %si
    call puts

    /* A4a: плоский PM-рантайм: LBA 72..135 -> 0x4000:0000. */
    mov $dap_pm, %si
    mov $0x42, %ah
    mov drive, %dl
    int $0x13
    jc pm_read_fail
    jmp pm_switch

all_bad:
    mov $msg_all_bad, %si
    call puts
    mov $0x0011, %ax
    jmp fail_exit

magic_fail:
    mov $msg_magic_bad, %si
    call puts
    jmp fail_11
count_fail:
    mov $msg_count_bad, %si
    call puts
    jmp fail_11
edd_fail:
    mov $msg_edd, %si
    call puts
    jmp fail_11
read_fail:
    mov $msg_read, %si
    call puts
    jmp fail_11
pm_read_fail:
    mov $msg_pm_read, %si
    call puts
    jmp fail_11
fail_11:
    mov $0x0011, %ax
fail_exit:
    mov $0xF4, %dx
    out %ax, %dx
halt16:
    hlt
    jmp halt16

/* ---- защищённый режим ---- */
pm_switch:
    lgdt gdtr
    cli
    mov %cr0, %eax
    or $1, %eax
    mov %eax, %cr0
    /* Код-сегмент плоский (base=0), поэтому EIP должен быть ЛИНЕЙНЫМ
     * адресом pm_entry = stage2_base + pm_entry (>64K). 16-битный far jump
     * оставил бы EIP=0x19A и ушёл в мусор по физическому 0x19A.
     * Явный 32-битный far jump: 66 EA <offset32> <selector16>. */
    .byte 0x66, 0xEA
    .long stage2_base + pm_entry
    .word 0x08

/* ---- VGA/COM1 и debug-exit ---- */
.code32
pm_entry:
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %ss
    mov $0x90000, %esp
    cld

    mov $0xB8000, %edi
    mov $stage2_base + pm_msg, %esi
    mov $0x1F, %ah             /* белый на синий */
pm_loop:
    lodsb
    test %al, %al
    jz pm_done
    mov %ax, (%edi)
    add $2, %edi
    jmp pm_loop
pm_done:
    /* Честный readback VGA text buffer: не «нарисовали», а проверили. */
    mov $0xB8000, %edi
    cmpb $0x43, (%edi)
    jne pm_vga_fail
    cmpb $0x1F, 1(%edi)
    jne pm_vga_fail

    mov $stage2_base + pm_com_msg, %esi
    call com_puts32
    mov $stage2_base + pm_exec_msg, %esi
    call com_puts32
    /* Явный 32-битный far jump: метки stage2 имеют VMA 0, а исполняются
     * по 0x10000, поэтому относительный jmp уехал бы в 0x50000. */
    /* В .code32 префикс 0x66 сделал бы 16-битный far jump — он не нужен. */
    .byte 0xEA
    .long 0x00040000
    .word 0x08
pm_halt:
    hlt
    jmp pm_halt

pm_vga_fail:
    mov $stage2_base + pm_vga_fail_msg, %esi
    call com_puts32
    mov $0xF4, %dx
    mov $0x0011, %ax
    out %ax, %dx
    jmp pm_halt

com_puts32:
    cld
1:
    lodsb
    test %al, %al
    jz 2f
    push %eax
    mov $0x3FD, %dx
3:
    in %dx, %al
    test $0x20, %al
    jz 3b
    mov $0x3F8, %dx
    pop %eax
    out %al, %dx
    jmp 1b
2:
    ret

/* ---- 16-битные помощники ---- */
.code16
puts:
    cld
1:
    lodsb
    test %al, %al
    jz 2f
    call putc
    jmp 1b
2:
    ret

putc:
    push %ax
    mov $0x0E, %ah
    mov $0x0007, %bx
    int $0x10
    mov $0x3FD, %dx
1:
    in %dx, %al
    test $0x20, %al
    jz 1b
    mov $0x3F8, %dx
    pop %ax
    out %al, %dx
    ret

com_init:
    mov $0x3F9, %dx
    mov $0x80, %al
    out %al, %dx             /* DLAB on */
    mov $0x3F8, %dx
    mov $0x03, %al
    out %al, %dx             /* divisor low = 115200 */
    inc %dx
    xor %al, %al
    out %al, %dx             /* divisor high */
    mov $0x3FB, %dx
    mov $0x03, %al
    out %al, %dx             /* 8N1 */
    mov $0x3F9, %dx
    xor %al, %al
    out %al, %dx             /* DLAB off, IRQ выключен */
    mov $0x3FC, %dx
    mov $0x03, %al
    out %al, %dx             /* DTR/RTS */
    ret

print_hex32:
    push %eax
    shr $16, %eax
    call print_hex16
    pop %eax
    push %eax
    and $0xFFFF, %eax
    call print_hex16
    pop %eax
    ret

print_hex16:
    push %ax
    push %cx
    mov %ax, hex_val
    mov $4, %cx
1:
    mov hex_val, %dx    /* putc портит DX — берём значение из памяти */
    rol $4, %dx
    mov %dx, hex_val
    mov %dx, %bx
    and $0xF, %bx
    mov hexdigits(%bx), %al
    push %cx            /* BIOS/COM тоже могут тронуть CX */
    call putc
    pop %cx
    loop 1b
    pop %cx
    pop %ax
    ret

/* CRC-32 IEEE, tableless: ES:SI, CX = длина, результат в crc_result. */
crc32_body:
    mov $0xFFFFFFFF, %edi
crc_byte:
    xor %eax, %eax
    mov %es:(%si), %al
    xor %edi, %eax
    mov %eax, %edi
    mov $8, %edx
crc_bit:
    shr $1, %edi
    jnc crc_skip
    xor $0xEDB88320, %edi
crc_skip:
    dec %edx
    jnz crc_bit
    inc %si
    loop crc_byte
    not %edi
    mov %edi, crc_result
    ret

/* ---- данные ---- */
drive:      .byte 0
dap_ctmd:
    .byte 0x10, 0x00
    .word 64
    .word 0x0000
    .word 0x2000
    .quad 8
dap_pm:
    .byte 0x10, 0x00
    .word pm_sectors
    .word 0x0000
    .word pm_load_seg
    .quad pm_lba
ctmd_count: .long 0
entry_index:.word 0
entry_off:  .word 0
body_off:   .word 0
body_len:   .word 0
want_crc:   .long 0
crc_result: .long 0
bad:        .word 0
hex_val:    .word 0

hexdigits:  .ascii "0123456789ABCDEF"

msg_stage2:    .asciz "CTOS A3b STAGE2\r\n"
msg_count:     .asciz "CTMD count="
msg_crc_ok:    .asciz "CRC OK\r\n"
msg_crc_bad:   .asciz "CRC FAIL\r\n"
msg_bounds_bad:.asciz "BOUNDS FAIL\r\n"
msg_all_ok:    .asciz "CTMD ALL OK\r\n"
msg_all_bad:   .asciz "CTMD FAIL\r\n"
msg_magic_bad: .asciz "CTMD magic FAIL\r\n"
msg_count_bad: .asciz "CTMD count FAIL\r\n"
msg_edd:       .asciz "CTOS A3b STAGE2: NO EDD\r\n"
msg_read:      .asciz "CTOS A3b STAGE2: READ FAIL\r\n"
msg_pm_read:   .asciz "CTOS A4a PM READ FAIL\r\n"
msg_nl:        .asciz "\r\n"
msg_space:     .asciz " "

/* 32-битные строки должны лежать в .code32-часть не попадают в 16-битный поток. */
.code32
pm_msg:          .asciz "CTOS A3b PM OK"
pm_com_msg:      .asciz "CTOS A3b PM OK\r\n"
pm_exec_msg:     .asciz "CTOS A4a EXEC\r\n"
pm_vga_fail_msg: .asciz "CTOS A3b VGA FAIL\r\n"
.code16

.align 8
gdt:
    .quad 0
    .word 0xFFFF, 0x0000, 0x9A00, 0x00CF   /* code, flat 4 ГБ */
    .word 0xFFFF, 0x0000, 0x9200, 0x00CF   /* data, flat 4 ГБ */
gdt_end:
gdtr:
    .word gdt_end - gdt - 1
    .long stage2_base + gdt
