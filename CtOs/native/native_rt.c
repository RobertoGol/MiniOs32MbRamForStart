/*
 * native_rt.c — Этап 3 / bring-up Ф2, шаг A1: нативный интерпретатор
 * подмножества опкодов CtOs v1.1 (TKT-056, BRINGUP_SPEC.md).
 *
 * ЧЕСТНЫЕ ГРАНИЦЫ A1:
 *   - поддерживаются только опкоды, реально исполняемые ядром
 *     memmgr.ctos / kernel_sched.ctos:
 *       NOP INIT ALLOC_ST CALL RET TERM JZ JMP
 *       CONST LOAD(0x14/0x15/0x16/0x17/0x18/0x19/0x1A/0x1B)
 *       STORE_A INCELL INCELL_IND STORE_IND OUTCELL OUTCELL_V
 *   - syscall/NID, таймер, контекстные NID 0x150..0x154, файловый слой,
 *     ASMBLOCK и сеть НЕ поддерживаются: при исполнении — честный FATAL,
 *     а не тихое пропускание.
 *   - заголовок v1.1 проверяется по CRC-32 тела (zlib-совместимый),
 *     как в CtOs-Emu/ctos_vm.py. v1.0 принимается с явным предупреждением.
 *   - все ячейки — строго 32 бита; арифметика маскируется & 0xFFFFFFFF
 *     (B-13, контракт TKT-009).
 *
 * Выход: events-файл с детерминированными строками
 *   PORT <port:08X> <value:08X>
 * для каждого OUTCELL/OUTCELL_V и строка
 *   OPS <count> CELLS <count>
 * в конце. Формат пригоден для побайтовой сверки с трассой ctos_vm.py
 * (Python_compiler/verify_native_rt.py).
 *
 * Сборка: gcc -O2 -std=c11 -Wall -Wextra -o native_rt.exe native_rt.c
 * Запуск: native_rt.exe <binary.ctos> <events.txt>
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HEADER_V10 16u
#define HEADER_V11 20u
#define VER_CHECK  0x0101u
#define TAIL_MAGIC 0xAAAAFFFFu

#define CELL_BITS 20
#define CELL_CAP  (1u << CELL_BITS)
#define CELL_MASK (CELL_CAP - 1u)

#define RTS_MAX 4096

static uint8_t *code;
static uint32_t code_len;
static uint32_t entry_point;

static uint32_t ckey[CELL_CAP];
static uint32_t cval[CELL_CAP];
static uint8_t cused[CELL_CAP];
static uint32_t cell_count;

static uint32_t rts[RTS_MAX];
static uint32_t rts_len;

static uint32_t acc;
static uint32_t pc;
static uint64_t ops;
static FILE *events;

static void fatal(const char *msg, uint32_t arg) {
    fprintf(stderr, "FATAL: %s", msg);
    if (arg)
        fprintf(stderr, " 0x%08X", arg);
    fprintf(stderr, "\n");
    exit(1);
}

/* ---- CRC-32 (zlib/crc32 совместимый, отражённый полином 0xEDB88320) ---- */
static uint32_t crc32_body(const uint8_t *buf, uint32_t len) {
    static uint32_t table[256];
    static int ready = 0;
    if (!ready) {
        uint32_t i, j;
        for (i = 0; i < 256; i++) {
            uint32_t c = i;
            for (j = 0; j < 8; j++)
                c = (c & 1u) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
            table[i] = c;
        }
        ready = 1;
    }
    uint32_t c = 0xFFFFFFFFu;
    uint32_t i;
    for (i = 0; i < len; i++)
        c = table[(c ^ buf[i]) & 0xFFu] ^ (c >> 8);
    return c ^ 0xFFFFFFFFu;
}

/* ---- разреженные ячейки cell:raw ---- */
static uint32_t hash32(uint32_t x) {
    x ^= x >> 16;
    x *= 0x7FEB352Du;
    x ^= x >> 15;
    x *= 0x846CA68Bu;
    x ^= x >> 16;
    return x;
}

static uint32_t cell_get(uint32_t key) {
    uint32_t i = hash32(key) & CELL_MASK;
    while (cused[i]) {
        if (ckey[i] == key)
            return cval[i];
        i = (i + 1u) & CELL_MASK;
    }
    return 0;
}

static void cell_set(uint32_t key, uint32_t val) {
    uint32_t i = hash32(key) & CELL_MASK;
    while (cused[i]) {
        if (ckey[i] == key) {
            cval[i] = val;
            return;
        }
        i = (i + 1u) & CELL_MASK;
    }
    if (cell_count == CELL_CAP)
        fatal("cell: хеш-таблица ячеек исчерпана", key);
    cused[i] = 1;
    ckey[i] = key;
    cval[i] = val;
    cell_count++;
}

/* ---- чтение BE32 потока опкодов ---- */
static uint32_t be32(uint32_t at) {
    if (at + 4u > code_len)
        fatal("BE32 обрезан в конце файла", at);
    return ((uint32_t)code[at] << 24) | ((uint32_t)code[at + 1u] << 16) |
           ((uint32_t)code[at + 2u] << 8) | (uint32_t)code[at + 3u];
}

static void need(uint32_t at, uint32_t n) {
    if (at + n > code_len)
        fatal("опкод обрезан в конце файла", at);
}

static void jump_to(uint32_t target) {
    /* ровно контракт ctos_vm.jump_target: строго внутрь потока опкодов */
    if (target <= entry_point || target >= code_len)
        fatal("переход вне потока опкодов", target);
    pc = target;
}

static void emit_port(uint32_t port, uint32_t val) {
    cell_set(port, val);
    fprintf(events, "PORT %08X %08X\n", port, val);
}

static void load_binary(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f)
        fatal("не могу открыть бинарь", 0);
    if (fseek(f, 0, SEEK_END) != 0)
        fatal("fseek END", 0);
    long n = ftell(f);
    if (n < (long)HEADER_V10 || fseek(f, 0, SEEK_SET) != 0)
        fatal("файл меньше 16 байт — не CTOS-бинарник", 0);
    code_len = (uint32_t)n;
    code = (uint8_t *)malloc(code_len);
    if (!code || fread(code, 1, code_len, f) != code_len)
        fatal(" чтение файла", 0);
    fclose(f);

    if (memcmp(code, "CTOS", 4) != 0)
        fatal("нет магии 'CTOS' в начале файла", 0);
    uint32_t ver = (uint32_t)code[4] | ((uint32_t)code[5] << 8);
    uint32_t tail = (uint32_t)code[12] | ((uint32_t)code[13] << 8) |
                    ((uint32_t)code[14] << 16) | ((uint32_t)code[15] << 24);
    if (tail != TAIL_MAGIC)
        fatal("хвостовая магия заголовка испорчена", tail);

    if (ver == VER_CHECK) {
        if (code_len < HEADER_V11)
            fatal("v1.1 заявлен, но файл меньше 20 байт", 0);
        uint32_t stored = (uint32_t)code[16] | ((uint32_t)code[17] << 8) |
                          ((uint32_t)code[18] << 16) | ((uint32_t)code[19] << 24);
        uint32_t real = crc32_body(code + HEADER_V11, code_len - HEADER_V11);
        if (stored != real) {
            fprintf(stderr,
                    "FATAL: [TKT-040] честный брак целостности: в файле 0x%08X, "
                    "CRC-32 тела 0x%08X\n", stored, real);
            exit(1);
        }
    } else if (ver == 0x0100u) {
        fprintf(stderr, "WARN: заголовок v1.0 legacy — контроля целостности нет\n");
    } else {
        fatal("неизвестная версия заголовка", ver);
    }

    entry_point = (uint32_t)code[8] | ((uint32_t)code[9] << 8) |
                  ((uint32_t)code[10] << 16) | ((uint32_t)code[11] << 24);
    if (entry_point < HEADER_V10 || entry_point >= code_len)
        fatal("точка входа вне файла", entry_point);
    pc = entry_point;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Использование: %s <binary.ctos> <events.txt>\n", argv[0]);
        return 1;
    }
    load_binary(argv[1]);
    events = fopen(argv[2], "wb");
    if (!events)
        fatal("не могу открыть events-файл", 0);

    for (;;) {
        if (pc >= code_len)
            fatal("поток опкодов кончился без OP_TERM", pc);
        uint8_t op = code[pc];
        ops++;

        switch (op) {
        case 0x00: /* NOP */
        case 0x01: /* INIT */
        case 0x10: /* ALLOC_ST — маркер объявления статики */
            pc++;
            break;
        case 0x03: { /* CALL */
            need(pc, 5);
            uint32_t addr = be32(pc + 1u);
            if (addr == 0) {
                pc += 5;
            } else {
                if (rts_len == RTS_MAX)
                    fatal("стек возвратов переполнен", rts_len);
                rts[rts_len++] = pc + 5u;
                jump_to(addr);
            }
            break;
        }
        case 0x04: /* RET */
            if (!rts_len)
                fatal("RET вне вызова — стек возвратов пуст", pc);
            pc = rts[--rts_len];
            break;
        case 0x05: /* TERM */
            fprintf(events, "OPS %llu CELLS %u\n",
                    (unsigned long long)ops, cell_count);
            fclose(events);
            free(code);
            return 0;
        case 0x06: /* JZ */
        case 0x07: /* JMP */ {
            need(pc, 5);
            uint32_t target = be32(pc + 1u);
            if (op == 0x06 && acc != 0)
                pc += 5;
            else
                jump_to(target);
            break;
        }
        case 0x12: { /* LOAD + режим */
            need(pc, 6);
            uint8_t mode = code[pc + 1u];
            uint32_t arg = be32(pc + 2u);
            switch (mode) {
            case 0x14: acc = (acc + arg) & 0xFFFFFFFFu; break;
            case 0x15: acc = (acc + cell_get(arg)) & 0xFFFFFFFFu; break;
            case 0x16: acc = (acc == arg) ? 1u : 0u; break;
            case 0x17: acc = (acc - arg) & 0xFFFFFFFFu; break;
            case 0x18: acc = (acc == cell_get(arg)) ? 1u : 0u; break;
            case 0x19: acc = cell_get(arg); break;
            case 0x1A: acc = (acc > arg) ? 1u : 0u; break;
            case 0x1B: acc = (acc < arg) ? 1u : 0u; break;
            default: fatal("OP_LOAD: недокументированный режим", mode);
            }
            pc += 6;
            break;
        }
        case 0x14: /* STORE_A */
            need(pc, 5);
            cell_set(be32(pc + 1u), acc);
            pc += 5;
            break;
        case 0x15: /* CONST */
            need(pc, 5);
            acc = be32(pc + 1u);
            pc += 5;
            break;
        case 0x50: /* INCELL */
            need(pc, 5);
            acc = cell_get(be32(pc + 1u));
            pc += 5;
            break;
        case 0x51: /* OUTCELL: порт <- литерал */
            need(pc, 9);
            emit_port(be32(pc + 1u), be32(pc + 5u));
            pc += 9;
            break;
        case 0x52: /* INCELL_IND */
            need(pc, 5);
            acc = cell_get(cell_get(be32(pc + 1u)));
            pc += 5;
            break;
        case 0x53: /* STORE_IND — честный отказ на нулевом указателе */
            need(pc, 5);
            uint32_t holder = be32(pc + 1u);
            uint32_t addr = cell_get(holder);
            if (addr == 0)
                fatal("STORE_IND: запись по адресу 0 — указатель не инициализирован",
                      holder);
            cell_set(addr, acc);
            pc += 5;
            break;
        case 0x54: /* OUTCELL_V: порт <- cell[var_addr] */
            need(pc, 9);
            emit_port(be32(pc + 1u), cell_get(be32(pc + 5u)));
            pc += 9;
            break;
        case 0x55: /* STORE_AT */
            need(pc, 5);
            cell_set(be32(pc + 1u), acc);
            pc += 5;
            break;
        default:
            fatal("опкод не в подмножестве A1 — честный отказ", op);
        }
    }
}
