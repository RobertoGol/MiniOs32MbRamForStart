/* A4a: точка входа плоского 32-битного рантайма.
 * Вызываем тот же main() из native_rt.c с argv:
 *   native_rt --module memmgr CTMD:image events:com1
 * Успех: isa-debug-exit AX=0x13 (rc=39), отказ main/AX: 0x14 (rc=41). */
.code32
.section .text
.global _start

.set PM_STACK, 0x00090000

_start:
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %ss
    mov $PM_STACK, %esp
    cld

    /* BSS не грузится BIOS: обнуляем явно, до первого обращения к main. */
    mov $_bss_start, %edi
    mov $_bss_end, %ecx
    sub %edi, %ecx
    xor %eax, %eax
    rep stosb

    /* cdecl: argc, argv[0..4], NULL — caller cleans the stack. */
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
    jz pm_ok

pm_fail:
    mov $0xF4, %dx
    mov $0x0014, %ax
    out %ax, %dx
1:
    hlt
    jmp 1b

pm_ok:
    mov $0xF4, %dx
    mov $0x0013, %ax
    out %ax, %dx
2:
    hlt
    jmp 2b

.section .data
argv:
    .long arg0, arg1, arg2, arg3, arg4, 0
arg0: .asciz "native_rt"
arg1: .asciz "--module"
arg2: .asciz "memmgr"
arg3: .asciz "CTMD:image"
arg4: .asciz "events:com1"
