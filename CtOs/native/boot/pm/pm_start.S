/* A4a/A6/A8: точка входа плоского 32-битного рантайма.
 * Вызываем тот же main() из native_rt.c с argv:
 *   native_rt --module <module> CTMD:image events:com1
 * A4a (по умолчанию): один модуль memmgr — лог байт-в-байт прежний.
 * A6: по маркеру CTOS-AUTORUN-A6 в MBR stage2 пишет флаг по физическому
 * 0x47000; тогда main() вызывается четырежды, по одному разу на каждый
 * модуль CTMD, с полным сбросом BSS между вызовами. native_rt.c не меняется:
 * все его статики и bump-allocator shim'а лежат в BSS, а argv и таблица
 * имён — в .data и при перезапуске сохраняются.
 * A8: маркер CTOS-DISK-A8 в MBR+0x1A0 и байт индекса в MBR+0x1AC. Имеет
 * приоритет над A6: запускает ровно один модуль из CAT-области диска данных
 * (уже прочитанной stage2 по 0x50000) с argv[3]="DISK:image". Shim сам
 * собирает синтетический CTMD, поэтому INT 13h в PM по-прежнему не нужен.
 * Успех: isa-debug-exit AX=0x13 (rc=39), отказ main/AX: 0x14 (rc=41). */
.code32
.section .text
.global _start

.set PM_STACK, 0x00090000
.set AUTORUN_FLAG, 0x00047000
.set AUTORUN_MODULES, 4
/* A8: MBR загружен BIOS по 0x7C00; 0x7C00+0x1A0 = 0x7DA0. */
.set A8_SELECT_PHYS, 0x00007DA0
.set A8_NAME_PHYS, 0x00050019    /* CAT-база + 24 + 1 (имя записи) */
.set A8_MAX_INDEX, 8

_start:
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %ss
    mov $PM_STACK, %esp
    cld

    /* ---- A8: выбор одного модуля с диска данных. ----
     * MBR+0x1A0: 12 байт "CTOS-DISK-A8", затем индекс записи каталога.
     * A8 перекрывает A6 и запускает один модуль; имя берётся из уже
     * загруженной CAT-области, shim копирует его в a8_name. */
    mov $A8_SELECT_PHYS, %esi
    mov $a8_marker, %edi
    mov $12, %ecx
    repe cmpsb
    jne a6_check
    movzbl A8_SELECT_PHYS + 12, %eax
    cmp $A8_MAX_INDEX, %eax
    jae a6_check                 /* неверный индекс — честный A4a/A6-путь */
    shl $6, %eax                 /* запись каталога = 64 байта */
    add $A8_NAME_PHYS, %eax
    mov %eax, a8_name_ptr
    mov $a8_name_ptr, %ebx
    mov $1, %ebp
    movl $(disk_image), argv + 12
    jmp a6_loop

a6_check:
    /* A6: флаг передаётся из stage2 в запасных байтах слота PM. */
    cmpb $0, AUTORUN_FLAG
    jne a6_all
    mov $1, %ebp
    jmp a6_set
a6_all:
    mov $AUTORUN_MODULES, %ebp
a6_set:
    mov $module_names, %ebx

a6_loop:
    /* BSS не грузится BIOS и не должен наследоваться от предыдущего модуля. */
    mov $_bss_start, %edi
    mov $_bss_end, %ecx
    sub %edi, %ecx
    xor %eax, %eax
    rep stosb

    /* cdecl: argc, argv[0..4], NULL — caller cleans the stack. */
    mov (%ebx), %eax
    mov %eax, argv + 8          /* argv[2] = имя очередного модуля */
    pushl $0
    pushl $(argv + 16)
    pushl $(argv + 12)
    pushl $(argv + 8)
    pushl $(argv + 4)
    pushl $argv
    pushl $5
    call _main
    addl $24, %esp
    test %eax, %eax
    jnz pm_fail

    add $4, %ebx
    dec %ebp
    jnz a6_loop

pm_ok:
    mov $0xF4, %dx
    mov $0x0013, %ax
    out %ax, %dx
2:
    hlt
    jmp 2b

pm_fail:
    mov $0xF4, %dx
    mov $0x0014, %ax
    out %ax, %dx
1:
    hlt
    jmp 1b

.section .data
argv:
    .long arg0, arg1, arg2, arg3, arg4, 0
arg0: .asciz "native_rt"
arg1: .asciz "--module"
arg2: .asciz "memmgr"
arg3: .asciz "CTMD:image"
arg4: .asciz "events:com1"

/* A8: строки/указатели, используемые только при маркере CTOS-DISK-A8. */
a8_marker:   .ascii "CTOS-DISK-A8"
a8_name_ptr: .long name_memmgr
disk_image:  .asciz "DISK:image"

/* Порядок совпадает с каталогом CTMD из build_modules_image.py. */
module_names:
    .long name_memmgr, name_sched, name_syscall_test, name_stage1
name_memmgr:      .asciz "memmgr"
name_sched:       .asciz "sched"
name_syscall_test:.asciz "syscall_test"
name_stage1:      .asciz "stage1"
