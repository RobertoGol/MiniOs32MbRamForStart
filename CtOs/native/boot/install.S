/* CtOS A5 — самоустанавливающийся загрузчик (LBA 5..7, 0x5000:0000).
 * Честная схема: работает только когда на исходном диске стоит маркер CTOS-INST,
 * и пишет только на диск с маркером CTOS-TGT. Без маркеров — молча возвращается.
 * Никакой сети, никакого шифрования: закрепление загрузки через MBR/ACTIVE,
 * sentinel и снятие флага установки. isa-debug-exit в этом коде не используется.
 */
.code16
.section .text
.global _start

.set buf_seg,        0x6000
.set chunk_off,      0x0000
.set scratch_off,    0x8000
.set marker_off,     0x0180      /* свободные байты MBR до таблицы разделов */
.set active_off,     0x01BE
.set image_sectors,  136
.set install_lba,    5
.set install_sectors,3
.set sentinel_lba,   136

_start:
    push %ds
    push %es
    /* Сначала свои сегменты, только потом запись в src_drive: иначе
     * сохранение уйдёт по DS=0x1000 stage2, а чтение — по DS=0x5000. */
    mov $0x5000, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %dl, src_drive
    cld

    /* Маркер установки на исходном диске? Без маркера установщик МОЛЧА
     * возвращается: это уже рабочая система, печать ей не нужна. */
    mov src_drive, %dl
    mov $0, %ax
    call read_scratch_lba
    jc src_read_fail
    call check_src_marker
    test %al, %al
    jnz no_install

    call puts_start
    call find_target
    jc no_target
    call copy_image
    jc write_fail
    call pin_target
    jc write_fail
    call self_delete
    jc write_fail

    call puts_pin
    mov $1, %al             /* установлено */
    jmp inst_done

src_read_fail:
    mov $2, %al             /* LBA0 исходника не читается — честный отказ */
    jmp inst_done
no_install:
    xor %al, %al            /* маркера нет — рабочая система */
    jmp inst_done
no_target:
    call puts_no_target
    mov $2, %al             /* честный отказ */
    jmp inst_done
write_fail:
    call puts_write_fail
    mov $2, %al

inst_done:
    pop %es
    pop %ds
    retf

/* ---- поиск целевого диска: только EDD + явный маркер ---- */
find_target:
    mov $0x80, %dl
ft_loop:
    cmp $0xF0, %dl
    jae ft_none
    mov %dl, cand_drive
    cmp src_drive, %dl
    je ft_next

    push %dx
    mov $0x41, %ah
    mov $0x55AA, %bx
    int $0x13
    pop %dx
    jc ft_next
    cmp $0xAA55, %bx
    jne ft_next
    test $1, %cl               /* бит0 = extended read/write (AH=42h/43h) */
    jz ft_next

    mov $0, %ax
    call read_scratch_lba       /* DL всё ещё кандидат */
    jc ft_next
    call check_tgt_marker
    test %al, %al
    jnz ft_next

    mov cand_drive, %dl
    mov %dl, tgt_drive
    call puts_found
    clc
    ret
ft_next:
    mov cand_drive, %dl
    inc %dl
    jmp ft_loop
ft_none:
    stc
    ret

/* ---- копирование всех 136 секторов с перечиткой ---- */
copy_image:
    xor %bx, %bx
ci_loop:
    cmp $3, %bx
    jae ci_done
    mov %bx, %ax
    shl $6, %ax                 /* 64 сектора на шаг */
    mov %ax, dap_lba_lo
    movl $0, dap_lba_hi
    mov $image_sectors, %cx
    sub %ax, %cx
    cmp $64, %cx
    jbe ci_count
    mov $64, %cx
ci_count:
    mov %cx, dap_count
    movw $chunk_off, dap_off
    movw $buf_seg, dap_seg
    mov $dap, %si
    mov $0x42, %ah
    mov src_drive, %dl
    int $0x13
    jc ci_fail

    mov $0x43, %ah
    mov tgt_drive, %dl
    int $0x13
    jc ci_fail

    movw $scratch_off, dap_off
    mov $0x42, %ah
    int $0x13
    jc ci_fail

    mov dap_count, %ax          /* DS ещё 0x5000 */
    mov $512, %cx
    mul %cx                     /* CX = число байт в порции */
    mov %ax, %cx
    mov $buf_seg, %ax
    mov %ax, %ds
    mov %ax, %es
    xor %si, %si
    mov $scratch_off, %di
    cld
    repe cmpsb
    jne ci_fail
    mov $0x5000, %ax
    mov %ax, %ds
    mov %ax, %es

    inc %bx
    jmp ci_loop
ci_done:
    call puts_write
    clc
    ret
ci_fail:
    mov $0x5000, %ax
    mov %ax, %ds
    mov %ax, %es
    stc
    ret

/* ---- закрепление цели ---- */
pin_target:
    /* LBA0: снять маркер установки и поставить ACTIVE. */
    mov tgt_drive, %dl
    mov $0, %ax
    call read_scratch_lba
    jc pin_fail
    call clear_scratch_marker
    call set_scratch_active
    mov tgt_drive, %dl
    mov $0, %ax
    call write_scratch_lba
    jc pin_fail

    /* Удалить установщик из цели: LBA5..7 = нули. */
    call zero_scratch
    mov $install_lba, %bx
pin_zero:
    cmp $install_lba + install_sectors, %bx
    jae pin_zero_done
    mov %bx, %ax
    mov tgt_drive, %dl
    call write_scratch_lba
    jc pin_fail
    inc %bx
    jmp pin_zero
pin_zero_done:

    call compute_checksum
    jc pin_fail

    /* Sentinel в LBA136: магия, версия, размер, контрольная сумма, флаги. */
    call zero_scratch
    mov $buf_seg, %ax
    mov %ax, %es
    mov $scratch_off, %di
    mov $lock_marker, %si       /* DS = 0x5000 */
    mov $16, %cx
    cld
    rep movsb
    mov $1, %eax
    stosl
    mov $image_sectors, %eax
    stosl
    mov checksum, %eax
    stosl
    xor %eax, %eax
    stosl
    mov $sentinel_lba, %ax
    mov tgt_drive, %dl
    call write_scratch_lba
    jc pin_fail
    clc
    ret
pin_fail:
    mov $0x5000, %ax
    mov %ax, %ds
    mov %ax, %es
    stc
    ret

/* ---- самоудаление установщика с источника ---- */
self_delete:
    mov src_drive, %dl
    mov $0, %ax
    call read_scratch_lba
    jc sd_fail
    call clear_scratch_marker
    mov src_drive, %dl
    mov $0, %ax
    call write_scratch_lba
    jc sd_fail

    call zero_scratch
    mov $install_lba, %bx
sd_zero:
    cmp $install_lba + install_sectors, %bx
    jae sd_done
    mov %bx, %ax
    mov src_drive, %dl
    call write_scratch_lba
    jc sd_fail
    inc %bx
    jmp sd_zero
sd_done:
    call puts_selfdel
    clc
    ret
sd_fail:
    mov $0x5000, %ax
    mov %ax, %ds
    mov %ax, %es
    stc
    ret

/* ---- контрольная сумма закреплённого образа (32-битная сумма dword) ---- */
compute_checksum:
    xor %ebp, %ebp              /* накопитель — ОДИН на все 136 секторов */
    xor %bx, %bx
cch_loop:
    cmp $3, %bx
    jae cch_done
    mov %bx, %ax
    shl $6, %ax
    mov %ax, dap_lba_lo
    movl $0, dap_lba_hi
    mov $image_sectors, %cx
    sub %ax, %cx
    cmp $64, %cx
    jbe cch_count
    mov $64, %cx
cch_count:
    mov %cx, dap_count
    movw $chunk_off, dap_off
    movw $buf_seg, dap_seg
    mov $dap, %si
    mov $0x42, %ah
    mov tgt_drive, %dl
    int $0x13
    jc cch_fail

    mov dap_count, %ax
    mov $512, %cx
    mul %cx
    shr $2, %ax                 /* число dword */
    mov %ax, %cx
    mov $buf_seg, %ax
    mov %ax, %ds
    xor %si, %si
cch_sum:
    addl (%si), %ebp
    add $4, %si
    loop cch_sum
    mov $0x5000, %ax
    mov %ax, %ds
    inc %bx
    jmp cch_loop
cch_done:
    mov $0x5000, %ax
    mov %ax, %es
    mov %ebp, %es:checksum
    clc
    ret
cch_fail:
    mov $0x5000, %ax
    mov %ax, %ds
    stc
    ret

/* ---- примитивы EDD ---- */
read_scratch_lba:              /* AX=LBA, DL=диск; буфер 0x6000:0x8000 */
    movw $1, dap_count
    movw $scratch_off, dap_off
    movw $buf_seg, dap_seg
    mov %ax, dap_lba_lo
    movl $0, dap_lba_hi
    mov $dap, %si
    mov $0x42, %ah
    int $0x13
    jc rw_fail
    clc
    ret
write_scratch_lba:             /* AX=LBA, DL=диск; буфер 0x6000:0x8000 */
    movw $1, dap_count
    movw $scratch_off, dap_off
    movw $buf_seg, dap_seg
    mov %ax, dap_lba_lo
    movl $0, dap_lba_hi
    mov $dap, %si
    mov $0x43, %ah
    int $0x13
    jc rw_fail
    clc
    ret
rw_fail:
    stc
    ret

clear_scratch_marker:
    mov $buf_seg, %ax
    mov %ax, %es
    mov $(scratch_off + marker_off), %di
    mov $16, %cx
    xor %al, %al
    cld
    rep stosb
    ret
set_scratch_active:
    mov $buf_seg, %ax
    mov %ax, %es
    mov $(scratch_off + active_off), %di
    mov $0x80, %al
    mov %al, %es:(%di)
    ret
zero_scratch:
    mov $buf_seg, %ax
    mov %ax, %es
    mov $scratch_off, %di
    mov $512, %cx
    xor %al, %al
    cld
    rep stosb
    ret

/* ---- сравнение маркера: DS:SI = образец, ES:DI = ожидание ---- */
check_src_marker:
    mov $buf_seg, %ax
    mov %ax, %ds
    mov $(scratch_off + marker_off), %si
    mov $0x5000, %ax
    mov %ax, %es
    mov $src_marker, %di
    mov $16, %cx
    cld
ck1:
    lodsb
    scasb
    jne ck1_bad
    loop ck1
    xor %ax, %ax
    jmp ck1_done
ck1_bad:
    mov $1, %ax
ck1_done:
    mov $0x5000, %dx
    mov %dx, %ds
    ret
check_tgt_marker:
    mov $buf_seg, %ax
    mov %ax, %ds
    mov $(scratch_off + marker_off), %si
    mov $0x5000, %ax
    mov %ax, %es
    mov $tgt_marker, %di
    mov $16, %cx
    cld
ck2:
    lodsb
    scasb
    jne ck2_bad
    loop ck2
    xor %ax, %ax
    jmp ck2_done
ck2_bad:
    mov $1, %ax
ck2_done:
    mov $0x5000, %dx
    mov %dx, %ds
    ret

/* ---- COM1 ---- */
com_puts:
    cld
cp1:
    lodsb
    test %al, %al
    jz cp2
    push %ax
    mov $0x3FD, %dx
cp3:
    in %dx, %al
    test $0x20, %al
    jz cp3
    mov $0x3F8, %dx
    pop %ax
    out %al, %dx
    jmp cp1
cp2:
    ret
puts_start:  mov $msg_start, %si;   jmp com_puts
puts_found:  mov $msg_found, %si;   call com_puts; call print_drive; jmp com_puts_nl
puts_write:  mov $msg_write, %si;   jmp com_puts
puts_pin:    mov $msg_pin, %si;     jmp com_puts
puts_selfdel:mov $msg_selfdel, %si; jmp com_puts
puts_no_target: mov $msg_no_target, %si; jmp com_puts
puts_write_fail: mov $msg_write_fail, %si; jmp com_puts
com_puts_nl: mov $msg_nl, %si; jmp com_puts
print_drive:
    mov $msg_drive, %si
    call com_puts
    mov tgt_drive, %al
    shr $4, %al
    call print_nibble
    mov tgt_drive, %al
    and $0xF, %al
    call print_nibble
    ret
print_nibble:
    push %bx
    and $0xF, %al
    mov $hexdigits, %bx
    xlatb                   /* AL = ASCII-код шестнадцатеричной цифры */
    pop %bx
    push %ax
    mov $0x3FD, %dx
pn1:
    in %dx, %al
    test $0x20, %al
    jz pn1
    mov $0x3F8, %dx
    pop %ax
    out %al, %dx
    ret

/* ---- данные ---- */
src_drive:   .byte 0
tgt_drive:   .byte 0
cand_drive:  .byte 0
a5_done:     .byte 0
a5_error:    .byte 0
dap:
    .byte 0x10, 0x00
dap_count:   .word 0
dap_off:     .word 0
dap_seg:     .word 0
dap_lba_lo:  .long 0
dap_lba_hi:  .long 0
checksum:    .long 0
src_marker:  .ascii "CTOS-INST-A5\0\0\0\0"
tgt_marker:  .ascii "CTOS-TGT-A5!\0\0\0\0"
lock_marker: .ascii "CTOS-LOCK-A5\0\0\0\0"
hexdigits:   .ascii "0123456789ABCDEF"

msg_start:      .asciz "CTOS A5 INSTALL: START\r\n"
msg_found:      .asciz "CTOS A5 TARGET 0x"
msg_drive:      .asciz ""
msg_nl:         .asciz "\r\n"
msg_write:      .asciz "CTOS A5 WRITE OK\r\n"
msg_pin:        .asciz "CTOS A5 PIN OK\r\n"
msg_selfdel:    .asciz "CTOS A5 SELF-DELETE OK\r\n"
msg_no_target:  .asciz "CTOS A5 NO TARGET\r\n"
msg_write_fail: .asciz "CTOS A5 WRITE FAIL\r\n"
