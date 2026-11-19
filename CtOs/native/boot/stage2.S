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
.set image_sectors, 136
.set sentinel_lba, 136
.set autorun_off, 0x190      /* запасные байты MBR до таблицы разделов */
.set pm_flags_off, 0x7000    /* внутри 64-секторного слота PM, за бинарником */
.set data_marker_off, 0x180  /* A7: маркер роли «диск данных» в LBA0 */
.set data_cat_lba, 8
.set data_cat_sectors, 64    /* A7-каталог + A8-тела модулей (32 КиБ) */
.set data_load_seg, 0x5000   /* каталог данных, после возврата установщика */

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

    /* A5: установщик в LBA 5..7 вызывается ТОЛЬКО при маркере CTOS-INST-A5.
     * После самоудаления маркера LBA 5..7 затерты нулями, и зовём мы их
     * не будем — иначе выполнились бы нули как код. AL установщика:
     * 0 = нет установки, 1 = установлено, 2 = честный отказ. */
    mov $dap_mbr_chk, %si
    mov $0x42, %ah
    mov drive, %dl
    int $0x13
    jc a5_skip
    push %ds
    push %es
    mov $0x6000, %ax
    mov %ax, %ds
    mov $0x1000, %ax
    mov %ax, %es
    /* A6: маркер CTOS-AUTORUN-A6 в MBR+0x190 включает запуск всех модулей
     * CTMD в PM. Проверяем в том же прочитанном LBA0, отдельного чтения нет. */
    mov $(0x8000 + autorun_off), %si
    xor %bx, %bx
a6_mk_cmp:
    lodsb
    cmp %es:autorun_marker(%bx), %al
    jne a6_no_marker
    inc %bx
    cmp $12, %bx
    jb a6_mk_cmp
    movb $1, %es:autorun_all    /* DS здесь = 0x6000, метка stage2 в ES */
a6_no_marker:
    mov $0x8180, %si             /* 0x6000:0x8000 + 0x180 */
    xor %bx, %bx
a5_mk_cmp:
    lodsb
    cmp %es:a5_install_marker(%bx), %al
    jne a5_no_marker
    inc %bx
    cmp $12, %bx
    jb a5_mk_cmp
    pop %es
    pop %ds
    jmp a5_call_install
a5_no_marker:
    pop %es
    pop %ds
    jmp a5_skip
a5_call_install:
    mov $dap_install, %si
    mov $0x42, %ah
    mov drive, %dl
    int $0x13
    jc install_read_fail
    mov drive, %dl
    lcall $0x5000, $0x0000
    cmp $0, %al
    je a5_skip
    cmp $1, %al
    jne install_fail
    mov $msg_a5_install, %si
    call puts
    mov $msg_a5_autorun, %si
    call puts
a5_skip:

    /* A5b: закрепление загрузки проверяется САМИМ загрузчиком. Если в MBR
     * выставлен ACTIVE, sentinel в LBA136 обязан существовать и сходиться;
     * чистый установочный образ (ACTIVE=0) проверку пропускает. При успехе
     * печать не делается, чтобы лог A4a остался байт-в-байт прежним. */
    call verify_pin
    jc pin_fail_boot

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

    /* A7: если диск данных найден — проверить его машинный каталог.
     * Отсутствие диска молча игнорируется (лог A4a остаётся прежним),
     * а найденный, но повреждённый каталог — честный отказ rc=35. */
    call scan_data_disk
    jc a7_fail

    /* A4a: плоский PM-рантайм: LBA 72..135 -> 0x4000:0000. */
    mov $dap_pm, %si
    mov $0x42, %ah
    mov drive, %dl
    int $0x13
    jc pm_read_fail
    /* A6: передать флаг автозапуска в PM через запасные байты слота PM.
     * 0x4000:0x7000 внутри прочитанных 64 секторов и за концом бинарника. */
    push %es
    mov $0x4000, %ax
    mov %ax, %es
    mov autorun_all, %al
    mov %al, %es:pm_flags_off
    pop %es
    jmp pm_switch

a7_fail:
    /* scan_data_disk уже напечатал конкретную причину. */
    mov $0x0011, %ax         /* rc=35: честный отказ повреждённого каталога */
    jmp fail_exit

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
install_read_fail:
    mov $msg_a5_read_fail, %si
    call puts
    mov $0x0011, %ax
    jmp fail_exit
install_fail:
    mov $msg_a5_fail, %si
    call puts
    mov $0x0012, %ax          /* rc=37: установка честно refuse'на */
    jmp fail_exit
pin_fail_boot:
    /* verify_pin уже напечатал конкретную причину. */
    mov $0x0011, %ax          /* rc=35: честный отказ закреплённой системы */
    jmp fail_exit
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

/* ---- A5b: проверка закрепления загрузки ----
 * Читаем LBA0: если ACTIVE не выставлен — это чистая установочная система,
 * pin не ожидается, выходим молча. Иначе LBA136 обязан содержать валидный
 * sentinel, а сумма dword по LBA0..135 — совпасть с записанной установщиком.
 * Любое расхождение — честный отказ с диагностикой, без перехода в PM.
 */
.code16
verify_pin:
    push %ds
    push %es
    mov $dap_mbr_chk, %si
    mov $0x42, %ah
    mov drive, %dl
    int $0x13
    jc vp_absent
    mov $0x6000, %ax
    mov %ax, %es
    cmpb $0x80, %es:0x81BE     /* 0x6000:0x8000 + MBR+0x1BE */
    jne vp_absent

    mov $dap_sentinel, %si
    mov $0x42, %ah
    mov drive, %dl
    int $0x13
    jc vp_read_fail
    mov $0x7000, %ax
    mov %ax, %es
    /* DS:SI = эталон в stage2, ES:DI = прочитанный sentinel.
     * Перепутанные регистры сравнивали код stage2 с мусором за sentinel. */
    mov $lock_marker, %si
    xor %di, %di
    mov $12, %cx
    cld
    repe cmpsb
    jne vp_bad
    cmpl $1, %es:0x10
    jne vp_bad
    cmpl $image_sectors, %es:0x14
    jne vp_bad
    cmpl $0, %es:0x1C
    jne vp_bad

    xor %ebp, %ebp             /* накопитель на все 136 секторов */
    xor %bx, %bx
vp_chunk:
    cmp $3, %bx
    jae vp_compare
    mov %bx, %ax
    shl $6, %ax
    mov %ax, dap_verify + 8    /* LBA младшее слово */
    movw $0, dap_verify + 10   /* LBA старшее слово */
    mov $image_sectors, %cx
    sub %ax, %cx
    cmp $64, %cx
    jbe vp_count
    mov $64, %cx
vp_count:
    mov %cx, dap_verify + 2
    mov $dap_verify, %si
    mov $0x42, %ah
    mov drive, %dl
    int $0x13
    jc vp_read_fail
    mov dap_verify + 2, %ax
    mov $128, %cx              /* dword на сектор: 512/4 */
    mul %cx
    mov %ax, %cx
    mov $0x6000, %ax
    mov %ax, %ds
    xor %si, %si
vp_sum:
    addl (%si), %ebp
    add $4, %si
    loop vp_sum
    mov $0x1000, %ax
    mov %ax, %ds
    inc %bx
    jmp vp_chunk

vp_compare:
    cmpl %es:0x18, %ebp
    jne vp_bad
    clc
    jmp vp_done
vp_absent:
    clc
    jmp vp_done
vp_read_fail:
    mov $msg_pin_read, %si
    call puts
    stc
    jmp vp_done
vp_bad:
    mov $msg_pin_fail, %si
    call puts
    stc
vp_done:
    pop %es
    pop %ds
    ret

/* ---- A7: диск данных с папками (FAT) и машинным каталогом ----
 * Сканируем 0x80..0xEF через EDD. Маркер CTOS-DATA-A7! в LBA0+0x180
 * означает «это диск данных». Тогда читаем 8 секторов каталога с LBA8
 * в 0x5000:0000 и проверяем magic/version/count/CRC-32. Диск не найден —
 * тихо продолжаем загрузку; найден, но бит — честный отказ с печатью.
 */
.code16
scan_data_disk:
    push %es
    movb $0x80, data_disk
sdd_loop:
    cmpb $0xF0, data_disk
    jae sdd_none
    /* EDD здесь не спрашиваем: AH=42h на несуществующем диске просто
     * вернёт CF, и мы перейдём к следующему номеру. */
    mov data_disk, %dl
    mov $dap_data_mbr, %si
    mov $0x42, %ah
    int $0x13
    jc sdd_next

    mov $0x6000, %ax
    mov %ax, %es
    mov $data_marker, %si       /* DS:SI = эталон в stage2 */
    mov $(0x8000 + data_marker_off), %di
    mov $13, %cx
    repe cmpsb             /* DF сброшен в начале stage2 */
    jne sdd_next

    mov data_disk, %dl
    mov $dap_data_cat, %si
    mov $0x42, %ah
    int $0x13
    jc sdd_bad

    mov $data_load_seg, %ax
    mov %ax, %es
    cmpl $0x534F5443, %es:0     /* 'CTOS' */
    jne sdd_bad
    cmpl $0x31544143, %es:4     /* 'CAT1' */
    jne sdd_bad
    cmpl $1, %es:8
    jne sdd_bad
    mov %es:12, %cx             /* count */
    jcxz sdd_bad
    cmp $63, %cx                /* 24+64*63 < 8*512 */
    ja sdd_bad
    mov %cx, %ax
    shl $6, %ax
    add $24, %ax
    mov %ax, %cx                /* длина CRC, 16 бит достаточно */
    mov %es:20, %ebp            /* EBP не трогает crc32_body */
    movl $0, %es:20             /* поле CRC обнулено на время счёта */
    xor %si, %si
    call crc32_body
    cmp crc_result, %ebp
    jne sdd_bad

    mov $msg_a7_ok, %si
    call puts
    clc
    jmp sdd_done
sdd_bad:
    mov $msg_a7_bad, %si
    call puts
    stc
    jmp sdd_done
sdd_next:
    incb data_disk
    jmp sdd_loop
sdd_none:
    clc
sdd_done:
    pop %es
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
autorun_all:.byte 0
data_disk:  .byte 0
dap_data_mbr:
    .byte 0x10, 0x00
    .word 1
    .word 0x8000
    .word 0x6000
    .quad 0
dap_data_cat:
    .byte 0x10, 0x00
    .word data_cat_sectors
    .word 0x0000
    .word data_load_seg
    .quad data_cat_lba
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
/* A5: LBA0 -> 0x6000:0x8000 для проверки маркера, LBA5..7 -> 0x5000:0. */
dap_mbr_chk:
    .byte 0x10, 0x00
    .word 1
    .word 0x8000
    .word 0x6000
    .quad 0
dap_install:
    .byte 0x10, 0x00
    .word 3
    .word 0x0000
    .word 0x5000
    .quad 5
/* A5b: sentinel LBA136 -> 0x7000:0; образ LBA0..135 -> 0x6000:0 порциями. */
dap_sentinel:
    .byte 0x10, 0x00
    .word 1
    .word 0x0000
    .word 0x7000
    .quad sentinel_lba
dap_verify:
    .byte 0x10, 0x00
    .word 64
    .word 0x0000
    .word 0x6000
    .quad 0
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
msg_a5_install:   .asciz "CTOS A5 INSTALL OK\r\n"
msg_a5_autorun:   .asciz "CTOS A5 AUTORUN ALL\r\n"
msg_a5_read_fail: .asciz "CTOS A5 INSTALL READ FAIL\r\n"
msg_a5_fail:      .asciz "CTOS A5 REFUSED\r\n"
a5_install_marker:.ascii "CTOS-INST-A5"
autorun_marker:.ascii "CTOS-AUTORUN-A6"
data_marker:   .ascii "CTOS-DATA-A7!"
lock_marker:   .ascii "CTOS-LOCK-A5"
               .byte 0, 0, 0, 0
msg_pin_fail:  .asciz "CTOS A5 PIN FAIL\r\n"
msg_pin_read:  .asciz "CTOS A5 PIN READ FAIL\r\n"
msg_a7_ok:     .asciz "CTOS A7 DATA OK\r\n"
msg_a7_bad:    .asciz "CTOS A7 DATA BAD\r\n"
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
