/*
 * native_rt.c — Этап 3 / bring-up Ф2: нативный интерпретатор CtOs v1.1.
 *
 * A1 (принято): подмножество опкодов ядра memmgr/kernel_sched.
 * A2 (принято): честный NID-слой
 *   - файлы   0x130 FILE_BEGIN, 0x131 FILE_PUT, 0x132 FILE_U16,
 *             0x133 FILE_END, 0x134 FILE_U8, 0x135 FILE_SEAL,
 *             0x136 FILE_SEEK, 0x137 FILE_GET;
 *   - контекст 0x150 WORK_CTX_SAVE, 0x151 WORK_CTX_RESTORE,
 *              0x152 WORK_CTX_YIELD;
 *   - таймер   0x153 TIMER_ARM, 0x154 TIMER_RET.
 * A3 (принято): загрузка .ctos-модулей из контейнера CTMD v1 (описание
 *   в CtOs/native/build_modules_image.py): --module <name> <image> ...
 *   Каталог проверяется по границам, тело модуля — по CRC-32, затем
 *   модуль исполняется с чистой VM-семантикой и тем же набором NID.
 * Плюс опкоды, реально исполняемые полной самосборкой stage1:
 *   0x11 STORE (адрес = смещение опкода), 0x20..0x26 NET_OPS (1-байтные
 *   маркеры etalon VM), 0x60 ASMBLOCK.
 *
 * Всё, чего нет в контракте (неизвестный NID/опкод) — честный FATAL,
 * никогда тихое пропускание. Заголовок v1.1 проверяется CRC-32
 * тела (zlib-совместимый). Ячейки строго 32-битные (B-13 / TKT-009).
 *
 * Выход — events-файл с детерминированными строками:
 *   PORT <port:08X> <value:08X>
 *   SYSCALL <nid:03X>
 *   TICK <pc:08X>
 *   OPS <count> CELLS <count>
 * что позволяет побайтово сверять поведение с ctos_vm.py --trace.
 *
 * Сборка: gcc -O2 -std=c11 -Wall -Wextra -o native_rt.exe native_rt.c
 * Запуск: native_rt.exe <binary.ctos> <events.txt> [source.words]
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

/* etalon VM держит rts без лимита; кольцевой компилятор при чтении потока
   исходника делает глубокие вложенные CALL, поэтому запас честно широкий. */
#define RTS_MAX 65536

#define STREAM_CELL 0x00F00FF0u
#define EOF_CELL    0x00F00FF2u
#define STATIC_ZONE 0x00F00000u
#define STATICS_MAX 0x50u

#define CTX_MAGIC 0x43545831u  /* 'CTX1' */
#define TCK_MAGIC 0x54434B31u  /* 'TCK1' */
#define TMR_MAGIC 0x544D5231u  /* 'TMR1' */

#define SRC_MAX 65536u

/* CTMD — контейнер модулей ядра (A3): 12-байтовый заголовок, 48-байтовые
   каталожные записи и тела модулей, выровненные по 16 байт. Все числа LE. */
#define CTMD_MAGIC    "CTMD"
#define CTMD_VERSION  1u
#define CTMD_ENTSZ    48u
#define CTMD_NAMESZ   32u

/* сетевые опкоды etalon VM: 1-байтные маркеры (NET_OPS в ctos_vm.py) */
#define NET_FIRST 0x20u
#define NET_LAST  0x26u

static uint8_t *code;
static uint32_t code_len;
static uint32_t entry_point;
static const char *binary_path;

/* A3: сведения о загруженном модуле (для events и честного лога) */
static char module_name[CTMD_NAMESZ];
static uint32_t module_len;
static uint32_t module_crc;
static int module_mode;

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

/* файловый слой */
static FILE *artifact;
static uint32_t artifact_n;
static uint32_t src_words[SRC_MAX];
static uint32_t src_count;
static uint32_t src_pos;

/* контекст/таймер */
typedef struct {
    uint32_t pc;
    uint32_t acc;
    uint32_t len;
    uint32_t rts[RTS_MAX];
} Ctx;

static Ctx kernel_ctx;
static int have_kernel_ctx;
static int tick_armed;
static int tick_pending;
static uint32_t tick_quantum;
static uint32_t tick_next;
static uint32_t tick_trap_block;
static uint32_t tick_trap_entry;
static uint32_t tick_st_base;
static uint32_t tick_st_count;

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

/* ---- поток опкодов ---- */
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

static uint32_t jump_to(uint32_t target) {
    if (target <= entry_point || target >= code_len)
        fatal("переход вне потока опкодов", target);
    return target;
}

static void emit_port(uint32_t port, uint32_t val) {
    cell_set(port, val);
    fprintf(events, "PORT %08X %08X\n", port, val);
}

static void le32(FILE *f, uint32_t v) {
    fputc((int)(v & 0xFFu), f);
    fputc((int)((v >> 8) & 0xFFu), f);
    fputc((int)((v >> 16) & 0xFFu), f);
    fputc((int)((v >> 24) & 0xFFu), f);
}

/* ---- контекстные блоки 'CTX1'/'TCK1' (TKT-055) ---- */
static void ctx_write(uint32_t ptr, uint32_t save_pc, uint32_t magic) {
    uint32_t i;
    if (rts_len > 0x80u)
        fatal("WORK_CTX: глубина стека сверх лимита 0x80", rts_len);
    if (save_pc < entry_point || save_pc >= code_len)
        fatal("WORK_CTX: pc снимка вне потока опкодов", save_pc);
    cell_set(ptr, magic);
    cell_set(ptr + 1u, save_pc);
    cell_set(ptr + 2u, acc);
    cell_set(ptr + 3u, rts_len);
    for (i = 0; i < rts_len; i++)
        cell_set(ptr + 4u + i, rts[i]);
}

static void ctx_read(uint32_t ptr, uint32_t magic, Ctx *out) {
    uint32_t i;
    uint32_t found = cell_get(ptr);
    if (found != magic)
        fatal("WORK_CTX: не та магия блока (контекст не инициализирован)", found);
    out->pc = cell_get(ptr + 1u);
    out->acc = cell_get(ptr + 2u);
    out->len = cell_get(ptr + 3u);
    if (out->len > 0x80u)
        fatal("WORK_CTX: rts_len сверх лимита 0x80", out->len);
    if (out->pc < entry_point || out->pc >= code_len)
        fatal("WORK_CTX: pc блока вне потока опкодов", out->pc);
    for (i = 0; i < out->len; i++)
        out->rts[i] = cell_get(ptr + 4u + i);
}

static void statics_save(uint32_t ptr, uint32_t off) {
    uint32_t i;
    if (!tick_st_count)
        return;
    cell_set(ptr + off, tick_st_count);
    cell_set(ptr + off + 1u, tick_st_base);
    for (i = 0; i < tick_st_count; i++)
        cell_set(ptr + off + 4u + i, cell_get(tick_st_base + i * 4u));
}

static void statics_load(uint32_t ptr, uint32_t off) {
    uint32_t i;
    uint32_t n = cell_get(ptr + off);
    uint32_t base;
    if (!n)
        return;
    if (n > STATICS_MAX)
        fatal("статик-окно: count сверх лимита 0x50 (блок испорчен)", n);
    base = cell_get(ptr + off + 1u);
    if (!base)
        fatal("статик-окно: count без базы (блок испорчен)", n);
    for (i = 0; i < n; i++)
        cell_set(base + i * 4u, cell_get(ptr + off + 4u + i));
}

/* ---- NID-слой ---- */
static int do_syscall(uint32_t nid) {
    uint32_t ptr, val;
    fprintf(events, "SYSCALL %03X\n", nid);
    switch (nid) {
    case 0x130u: /* FILE_BEGIN */
        if (artifact)
            fatal("FILE_BEGIN: артефакт уже открыт", 0);
        {
            char path[4096];
            if (strlen(binary_path) + 5 > sizeof(path))
                fatal("FILE_BEGIN: слишком длинный путь", 0);
            snprintf(path, sizeof(path), "%s.out", binary_path);
            artifact = fopen(path, "w+b");
        }
        if (!artifact)
            fatal("FILE_BEGIN: не могу открыть артефакт", 0);
        artifact_n = 0;
        return 0;
    case 0x131u: /* FILE_PUT — 4 байта BE */
        if (!artifact)
            fatal("FILE_PUT до FILE_BEGIN — брак порядка syscall", 0);
        val = cell_get(STREAM_CELL);
        fputc((int)((val >> 24) & 0xFFu), artifact);
        fputc((int)((val >> 16) & 0xFFu), artifact);
        fputc((int)((val >> 8) & 0xFFu), artifact);
        fputc((int)(val & 0xFFu), artifact);
        artifact_n += 4;
        return 0;
    case 0x132u: /* FILE_U16 — 2 байта BE */
        if (!artifact)
            fatal("FILE_U16 до FILE_BEGIN — брак порядка syscall", 0);
        val = cell_get(STREAM_CELL) & 0xFFFFu;
        fputc((int)((val >> 8) & 0xFFu), artifact);
        fputc((int)(val & 0xFFu), artifact);
        artifact_n += 2;
        return 0;
    case 0x133u: /* FILE_END */
        if (!artifact)
            fatal("FILE_END без FILE_BEGIN — брак порядка syscall", 0);
        fclose(artifact);
        artifact = NULL;
        return 0;
    case 0x134u: /* FILE_U8 — 1 байт */
        if (!artifact)
            fatal("FILE_U8 до FILE_BEGIN — брак порядка syscall", 0);
        fputc((int)(cell_get(STREAM_CELL) & 0xFFu), artifact);
        artifact_n += 1;
        return 0;
    case 0x135u: { /* FILE_SEAL — CRC-32 тела артефакта */
        uint8_t *blob;
        long n;
        uint32_t crc;
        if (!artifact)
            fatal("FILE_SEAL до FILE_BEGIN — брак порядка syscall", 0);
        fflush(artifact);
        /* etalon VM читает ВЕСЬ файл (seek(0); read()), а не до текущей
           позиции записи: после FILE_SEEK позиция может быть меньше хвоста. */
        if (fseek(artifact, 0, SEEK_END) != 0)
            fatal("FILE_SEAL: fseek END", 0);
        n = ftell(artifact);
        if (n < (long)HEADER_V11)
            fatal("FILE_SEAL: в артефакте меньше 20 байт", 0);
        blob = (uint8_t *)malloc((size_t)n);
        if (!blob)
            fatal("FILE_SEAL: malloc", 0);
        rewind(artifact);
        if (fread(blob, 1, (size_t)n, artifact) != (size_t)n)
            fatal("FILE_SEAL: чтение артефакта", 0);
        crc = crc32_body(blob + HEADER_V11, (uint32_t)n - HEADER_V11);
        free(blob);
        if (fseek(artifact, 16, SEEK_SET) != 0)
            fatal("FILE_SEAL: fseek 16", 0);
        le32(artifact, crc);
        if (fseek(artifact, 0, SEEK_END) != 0)
            fatal("FILE_SEAL: fseek END", 0);
        return 0;
    }
    case 0x136u: /* FILE_SEEK */
        if (!artifact)
            fatal("FILE_SEEK до FILE_BEGIN — брак порядка syscall", 0);
        val = cell_get(STREAM_CELL);
        fflush(artifact);
        if (fseek(artifact, (long)val, SEEK_SET) != 0)
            fatal("FILE_SEEK: честная позиция вне артефакта", val);
        return 0;
    case 0x137u: /* FILE_GET — слово исходника */
        if (src_pos < src_count) {
            cell_set(STREAM_CELL, src_words[src_pos++]);
            cell_set(EOF_CELL, 0);
        } else {
            cell_set(EOF_CELL, 1);
        }
        return 0;
    case 0x150u: /* WORK_CTX_SAVE */
        ptr = cell_get(STREAM_CELL);
        if (!ptr)
            fatal("WORK_CTX_SAVE: нет протокола аргумента (Stream_Emit пуст)", 0);
        ctx_write(ptr, pc + 5u, CTX_MAGIC);
        statics_save(ptr, 166);
        return 0;
    case 0x151u: { /* WORK_CTX_RESTORE */
        Ctx c;
        ptr = cell_get(STREAM_CELL);
        if (!ptr)
            fatal("WORK_CTX_RESTORE: нет протокола аргумента", 0);
        ctx_read(ptr, CTX_MAGIC, &c);
        /* per-epoch контракт: ядерный контекст переустанавливается каждый раз */
        kernel_ctx.pc = pc + 5u;
        kernel_ctx.acc = acc;
        kernel_ctx.len = rts_len;
        memcpy(kernel_ctx.rts, rts, rts_len * sizeof(uint32_t));
        have_kernel_ctx = 1;
        if (c.len > RTS_MAX)
            fatal("WORK_CTX_RESTORE: rts сверх ёмкости рантайма", c.len);
        memcpy(rts, c.rts, c.len * sizeof(uint32_t));
        rts_len = c.len;
        acc = c.acc;
        pc = jump_to(c.pc);
        statics_load(ptr, 166);
        return 1;
    }
    case 0x152u: { /* WORK_CTX_YIELD */
        Ctx c;
        ptr = cell_get(STREAM_CELL);
        if (!ptr)
            fatal("WORK_CTX_YIELD: нет протокола аргумента", 0);
        if (!have_kernel_ctx) {
            uint32_t ret_pc;
            /* свежий вход задачи: снимаем один кадр OP_CALL */
            if (!rts_len)
                fatal("WORK_CTX_YIELD: свежая задача без кадра вызова", 0);
            ctx_write(ptr, pc + 5u, CTX_MAGIC);
            statics_save(ptr, 166);
            ret_pc = rts[--rts_len];
            acc = 0;
            pc = jump_to(ret_pc);
            return 1;
        }
        c = kernel_ctx;
        have_kernel_ctx = 0;
        ctx_write(ptr, pc + 5u, CTX_MAGIC);
        statics_save(ptr, 166);
        if (c.len > RTS_MAX)
            fatal("WORK_CTX_YIELD: rts ядра сверх ёмкости", c.len);
        memcpy(rts, c.rts, c.len * sizeof(uint32_t));
        rts_len = c.len;
        acc = c.acc;
        pc = jump_to(c.pc);
        return 1;
    }
    case 0x153u: { /* TIMER_ARM */
        uint32_t quant, trap_block, trap_entry, st_hi, tb_hi;
        ptr = cell_get(STREAM_CELL);
        if (!ptr)
            fatal("TIMER_ARM: нет протокола аргумента", 0);
        if (cell_get(ptr) != TMR_MAGIC)
            fatal("TIMER_ARM: блок не имеет магии 'TMR1'", ptr);
        quant = cell_get(ptr + 1u);
        trap_block = cell_get(ptr + 2u);
        trap_entry = cell_get(ptr + 3u);
        tick_st_base = cell_get(ptr + 4u);
        tick_st_count = cell_get(ptr + 5u);
        if (!quant)
            fatal("TIMER_ARM: квант 0 — таймер без интервала", 0);
        if (!trap_block)
            fatal("TIMER_ARM: trap-блок не указан", 0);
        if (tick_st_count && tick_st_base != STATIC_ZONE)
            fatal("TIMER_ARM: база статик-окна вне STATIC_ZONE", tick_st_base);
        if (tick_st_count > STATICS_MAX)
            fatal("TIMER_ARM: окно статиков сверх лимита", tick_st_count);
        st_hi = tick_st_base + tick_st_count * 4u;
        tb_hi = trap_block + 136u + tick_st_count;
        if (tick_st_count && tick_st_base < tb_hi && trap_block < st_hi)
            fatal("TIMER_ARM: статик-окно перекрывает trap-блок", trap_block);
        jump_to(trap_entry);
        if (tick_pending)
            fatal("TIMER_ARM: тик ещё не завершён (нет TIMER_RET)", 0);
        tick_armed = 1;
        tick_quantum = quant;
        tick_next = (uint32_t)ops + quant;
        tick_trap_block = trap_block;
        tick_trap_entry = trap_entry;
        return 0;
    }
    case 0x154u: { /* TIMER_RET */
        Ctx c;
        if (!tick_pending)
            fatal("TIMER_RET: открытого тика нет (IRET без IRQ)", 0);
        ptr = cell_get(STREAM_CELL);
        if (!ptr)
            fatal("TIMER_RET: нет протокола аргумента", 0);
        ctx_read(ptr, TCK_MAGIC, &c);
        if (c.len > RTS_MAX)
            fatal("TIMER_RET: rts кадра сверх ёмкости", c.len);
        memcpy(rts, c.rts, c.len * sizeof(uint32_t));
        rts_len = c.len;
        acc = c.acc;
        pc = jump_to(c.pc);
        statics_load(ptr, 132);
        tick_pending = 0;
        return 1;
    }
    default:
        fprintf(stderr,
                "FATAL: OP_SYSCALL: NID 0x%08X — драйвер не зарегистрирован "
                "(файл 0x130..0x137, контекст 0x150..0x152, таймер 0x153/0x154)\n",
                nid);
        exit(1);
    }
}

/* ---- загрузка ---- */
/* Проверка одного .ctos-образа и установка точки входа. Используется и
   прямым запуском файла, и загрузчиком модулей из контейнера CTMD. */
static void verify_code(uint8_t *data, uint32_t len) {
    code = data;
    code_len = len;
    if (len < HEADER_V10)
        fatal("файл меньше 16 байт — не CTOS-бинарник", 0);
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

static void load_binary(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f)
        fatal("не могу открыть бинарь", 0);
    if (fseek(f, 0, SEEK_END) != 0)
        fatal("fseek END", 0);
    long n = ftell(f);
    if (n < (long)HEADER_V10 || fseek(f, 0, SEEK_SET) != 0)
        fatal("файл меньше 16 байт — не CTOS-бинарник", 0);
    uint8_t *buf = (uint8_t *)malloc((size_t)n);
    if (!buf || fread(buf, 1, (size_t)n, f) != (size_t)n)
        fatal("чтение файла", 0);
    fclose(f);
    verify_code(buf, (uint32_t)n);
}

/* A3: загрузка .ctos-модуля из контейнера CTMD.
   Каталожная запись (48 Б): name[32] ASCIIZ, offset LE32, length LE32,
   crc32 LE32 (тела модуля), reserved LE32.
   Честные отказы: неизвестное имя, выход за файл, несовпадение CRC. */
static uint32_t rd_le32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void load_module(const char *image_path, const char *want) {
    FILE *f = fopen(image_path, "rb");
    if (!f)
        fatal("CTMD: не могу открыть контейнер модулей", 0);
    if (fseek(f, 0, SEEK_END) != 0)
        fatal("CTMD: fseek END", 0);
    long flen = ftell(f);
    if (flen < (long)(12u + CTMD_ENTSZ) || fseek(f, 0, SEEK_SET) != 0)
        fatal("CTMD: контейнер короче заголовка и одной записи", 0);
    uint8_t *img = (uint8_t *)malloc((size_t)flen);
    if (!img || fread(img, 1, (size_t)flen, f) != (size_t)flen)
        fatal("CTMD: чтение контейнера", 0);
    fclose(f);

    if (memcmp(img, CTMD_MAGIC, 4) != 0)
        fatal("CTMD: нет магии 'CTMD'", 0);
    if (rd_le32(img + 4) != CTMD_VERSION)
        fatal("CTMD: неизвестная версия контейнера", rd_le32(img + 4));
    uint32_t count = rd_le32(img + 8);
    if (!count || count > 4096u ||
        (uint64_t)12u + (uint64_t)count * CTMD_ENTSZ > (uint64_t)flen)
        fatal("CTMD: каталог выходит за контейнер", count);

    uint32_t i;
    for (i = 0; i < count; i++) {
        const uint8_t *e = img + 12u + (size_t)i * CTMD_ENTSZ;
        char name[CTMD_NAMESZ];
        memcpy(name, e, CTMD_NAMESZ);
        name[CTMD_NAMESZ - 1u] = '\0';
        if (strcmp(name, want) != 0)
            continue;

        uint32_t off = rd_le32(e + CTMD_NAMESZ);
        uint32_t len = rd_le32(e + CTMD_NAMESZ + 4u);
        uint32_t crc = rd_le32(e + CTMD_NAMESZ + 8u);
        if ((uint64_t)off + (uint64_t)len > (uint64_t)flen)
            fatal("CTMD: тело модуля выходит за контейнер", off);
        if (len < HEADER_V10)
            fatal("CTMD: тело модуля короче CTOS-заголовка", len);
        uint32_t real = crc32_body(img + off, len);
        if (real != crc) {
            fprintf(stderr,
                    "FATAL: CTMD: честный брак целостности модуля '%s': "
                    "в каталоге 0x%08X, CRC тела 0x%08X\n", name, crc, real);
            exit(1);
        }

        uint8_t *body = (uint8_t *)malloc(len);
        if (!body)
            fatal("CTMD: malloc тела модуля", len);
        memcpy(body, img + off, len);
        free(img);

        memset(module_name, 0, sizeof(module_name));
        memcpy(module_name, name, strlen(name));
        module_len = len;
        module_crc = crc;
        module_mode = 1;

        /* артефакт FILE_* модуля пишется рядом с контейнером: <img>.<name>.out */
        size_t need_len = strlen(image_path) + 1u + strlen(name) + 1u;
        char *bp = (char *)malloc(need_len);
        if (!bp)
            fatal("CTMD: malloc пути артефакта", 0);
        snprintf(bp, need_len, "%s.%s", image_path, name);
        binary_path = bp;
        verify_code(body, len);
        return;
    }
    fatal("CTMD: модуль с таким именем не найден", 0);
}

static void load_source(const char *path) {
    FILE *f = fopen(path, "r");
    char line[8192];
    char *tok;
    if (!f)
        fatal("не могу открыть исходник FILE_GET", 0);
    while (src_count < SRC_MAX && fgets(line, sizeof(line), f)) {
        tok = strtok(line, " \t\r\n");
        while (tok && src_count < SRC_MAX) {
            size_t n = strlen(tok);
            if (n == 0 || n > 2)
                fatal("иходник: токен длиннее 2 символов (слово-язык стадии-1)", 0);
            if ((unsigned char)tok[0] > 0x7Fu ||
                (n == 2 && (unsigned char)tok[1] > 0x7Fu))
                fatal("иходник: токен не ASCII", 0);
            src_words[src_count++] = (uint32_t)(unsigned char)tok[0] |
                (n == 2 ? ((uint32_t)(unsigned char)tok[1] << 8) : 0u);
            tok = strtok(NULL, " \t\r\n");
        }
    }
    fclose(f);
    if (!src_count)
        fatal("иходник пуст — компилировать нечего", 0);
    src_words[src_count++] = 0x2Eu; /* CH_WORD_END '.' */
}

int main(int argc, char **argv) {
    const char *events_path;
    const char *src_path = NULL;

    if (argc >= 2 && strcmp(argv[1], "--module") == 0) {
        /* <exe> --module <name> <image.ctmd> <events.txt> [source.words] */
        if (argc < 5 || argc > 6) {
            fprintf(stderr,
                    "Использование: %s --module <name> <image.ctmd> "
                    "<events.txt> [source.words]\n", argv[0]);
            return 1;
        }
        load_module(argv[3], argv[2]);
        events_path = argv[4];
        if (argc == 6)
            src_path = argv[5];
    } else {
        /* <exe> <binary.ctos> <events.txt> [source.words] */
        if (argc < 3 || argc > 4) {
            fprintf(stderr,
                    "Использование: %s <binary.ctos> <events.txt> "
                    "[source.words]\n"
                    "           или: %s --module <name> <image.ctmd> "
                    "<events.txt> [source.words]\n", argv[0], argv[0]);
            return 1;
        }
        binary_path = argv[1];
        load_binary(argv[1]);
        events_path = argv[2];
        if (argc == 4)
            src_path = argv[3];
    }

    if (src_path)
        load_source(src_path);
    events = fopen(events_path, "wb");
    if (!events)
        fatal("не могу открыть events-файл", 0);
    if (module_mode)
        fprintf(events, "MODULE %s %u %08X\n",
                module_name, module_len, module_crc);

    for (;;) {
        uint8_t op;

        /* честный IRQ-тик между инструкциями (TKT-055 спринт Б).
           VM в этой ветке НЕ увеличивает op_count — и мы не увеличиваем. */
        if (tick_armed && have_kernel_ctx && ops >= tick_next && !tick_pending) {
            uint32_t at_pc = pc;
            ctx_write(tick_trap_block, at_pc, TCK_MAGIC);
            statics_save(tick_trap_block, 132);
            pc = jump_to(tick_trap_entry);
            tick_next = (uint32_t)ops + tick_quantum;
            tick_pending = 1;
            fprintf(events, "TICK %08X\n", at_pc);
            continue;
        }

        if (pc >= code_len)
            fatal("поток опкодов кончился без OP_TERM", pc);
        op = code[pc];
        ops++;

        switch (op) {
        case 0x00: /* NOP */
        case 0x01: /* INIT */
        case 0x10: /* ALLOC_ST */
            pc++;
            break;
        case 0x11: /* STORE: ячейка адресуется смещением опкода (стадия-0) */
            cell_set(pc, acc);
            pc++;
            break;
        case NET_FIRST: case 0x21: case 0x22: case 0x23:
        case 0x24: case 0x25: case NET_LAST: /* NET_OPS: 1-байтные маркеры */
            fprintf(events, "NET %02X\n", op);
            pc++;
            break;
        case 0x03: { /* CALL */
            uint32_t addr;
            need(pc, 5);
            addr = be32(pc + 1u);
            if (addr == 0) {
                pc += 5;
            } else {
                if (rts_len == RTS_MAX)
                    fatal("стек возвратов переполнен", rts_len);
                rts[rts_len++] = pc + 5u;
                pc = jump_to(addr);
            }
            break;
        }
        case 0x04: /* RET */
            if (!rts_len)
                fatal("RET вне вызова — стек возвратов пуст", pc);
            pc = rts[--rts_len];
            break;
        case 0x05: /* TERM */
            if (artifact)
                fatal("честный артефакт не закрыт — FILE_END не вызван", 0);
            fprintf(events, "OPS %llu CELLS %u\n",
                    (unsigned long long)ops, cell_count);
            fclose(events);
            free(code);
            return 0;
        case 0x06: /* JZ */
        case 0x07: /* JMP */ {
            uint32_t target;
            need(pc, 5);
            target = be32(pc + 1u);
            if (op == 0x06u && acc != 0)
                pc += 5;
            else
                pc = jump_to(target);
            break;
        }
        case 0x12: { /* LOAD + режим */
            uint8_t mode;
            uint32_t arg;
            need(pc, 6);
            mode = code[pc + 1u];
            arg = be32(pc + 2u);
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
        case 0x13: { /* SYSCALL */
            uint32_t nid;
            need(pc, 5);
            nid = be32(pc + 1u);
            if (!do_syscall(nid))
                pc += 5;
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
            if (!addr)
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
        case 0x60: { /* ASMBLOCK: +LE u32 длина + байты */
            uint32_t n;
            need(pc, 5);
            n = (uint32_t)code[pc + 1u] | ((uint32_t)code[pc + 2u] << 8) |
                ((uint32_t)code[pc + 3u] << 16) | ((uint32_t)code[pc + 4u] << 24);
            need(pc, 5u + n);
            pc += 5u + n;
            break;
        }
        default:
            fatal("опкод не в подмножестве A1/A2 — честный отказ", op);
        }
    }
}
