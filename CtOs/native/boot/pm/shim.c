/* A4a: минимальный freestanding-shim для того же CtOs/native/native_rt.c.
 *Semantika interpretera ne izmenyaetsya: menjayutsya tolko libc-vyzovy.
 * FILE: COM1 dlya sobytii/stderr, in-memory dlya CTMD i artefaktov. */
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef PM_CTMD_PHYS
#define PM_CTMD_PHYS 0x00020000u
#endif

#define PMF_COM1      0
#define PMF_MEM_READ  1
#define PMF_MEM_WRITE 2

static void com_putc(unsigned char c) {
    unsigned long v = (unsigned long)c;
    __asm__ __volatile__(
        "movw $0x3FD, %%dx\n\t"
        "1:\n\t"
        "inb %%dx, %%al\n\t"
        "testb $0x20, %%al\n\t"
        "jz 1b\n\t"
        "movw $0x3F8, %%dx\n\t"
        "movl %%ecx, %%eax\n\t"
        "outb %%al, %%dx"
        :
        : "c"(v)
        : "ax", "dx", "memory");
}

/* ---- tiny libc ---- */
void *memcpy(void *dst, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dst;
    const unsigned char *s = (const unsigned char *)src;
    size_t i;
    for (i = 0; i < n; i++)
        d[i] = s[i];
    return dst;
}

void *memset(void *dst, int c, size_t n) {
    unsigned char *d = (unsigned char *)dst;
    size_t i;
    for (i = 0; i < n; i++)
        d[i] = (unsigned char)c;
    return dst;
}

int memcmp(const void *a, const void *b, size_t n) {
    const unsigned char *x = (const unsigned char *)a;
    const unsigned char *y = (const unsigned char *)b;
    size_t i;
    for (i = 0; i < n; i++) {
        if (x[i] != y[i])
            return (int)x[i] - (int)y[i];
    }
    return 0;
}

size_t strlen(const char *s) {
    size_t n = 0;
    while (s[n])
        n++;
    return n;
}

int strcmp(const char *a, const char *b) {
    while (*a && *a == *b) {
        a++;
        b++;
    }
    return (int)(unsigned char)*a - (int)(unsigned char)*b;
}

static int is_delim(char c, const char *d) {
    while (*d) {
        if (c == *d++)
            return 1;
    }
    return 0;
}

char *strtok(char *s, const char *delim) {
    static char *save;
    char *start;
    if (s)
        save = s;
    if (!save)
        return NULL;
    while (*save && is_delim(*save, delim))
        save++;
    if (!*save) {
        save = NULL;
        return NULL;
    }
    start = save;
    while (*save && !is_delim(*save, delim))
        save++;
    if (*save) {
        *save++ = '\0';
    } else {
        save = NULL;
    }
    return start;
}

#define PM_HEAP_SIZE (256u * 1024u)
static unsigned char pm_heap[PM_HEAP_SIZE];
static unsigned long heap_pos;

void *malloc(size_t size) {
    unsigned long need = (unsigned long)size + 3u;
    unsigned long at;
    need &= ~3u;
    if (!need || need > PM_HEAP_SIZE - heap_pos)
        return NULL;
    at = heap_pos;
    heap_pos += need;
    return (void *)(pm_heap + at);
}

void free(void *ptr) {
    (void)ptr; /* bump-allocator: osvobozhdenie ne vozvrashchaet pamjat */
}

/* ---- streamy ---- */
static FILE com_stream = {NULL, 0, 0, 0, PMF_COM1, 1};
static FILE ctmd_stream = {NULL, 0, 0, 0, PMF_MEM_READ, 0};
static unsigned char artifact_mem[64u * 1024u];
static FILE artifact_stream = {artifact_mem, 0, sizeof(artifact_mem), 0,
                               PMF_MEM_WRITE, 1};

FILE *stderr = &com_stream;
FILE *stdout = &com_stream;

static unsigned long pm_le32(const unsigned char *p) {
    return (unsigned long)p[0] | ((unsigned long)p[1] << 8) |
           ((unsigned long)p[2] << 16) | ((unsigned long)p[3] << 24);
}

static unsigned long ctmd_body_len(const unsigned char *p) {
    unsigned long count, i, end;
    if (!p || memcmp(p, "CTMD", 4) != 0)
        return 0;
    count = pm_le32(p + 8);
    if (!count || count > 4096u)
        return 0;
    end = 12u + count * 48u;
    for (i = 0; i < count; i++) {
        const unsigned char *e = p + 12u + i * 48u;
        unsigned long off = pm_le32(e + 32u);
        unsigned long len = pm_le32(e + 36u);
        if (off + len > end)
            end = off + len;
    }
    return end;
}

static int ends_with(const char *s, const char *suffix) {
    size_t n = strlen(s), k = strlen(suffix);
    return (n >= k && strcmp(s + n - k, suffix) == 0);
}

FILE *fopen(const char *path, const char *mode) {
    if (!path || !mode)
        return NULL;
    if (strcmp(path, "events:com1") == 0 ||
        strcmp(path, "stderr:com1") == 0)
        return &com_stream;
    if (strcmp(path, "CTMD:image") == 0) {
        unsigned char *p = (unsigned char *)PM_CTMD_PHYS;
        ctmd_stream.buf = p;
        ctmd_stream.len = ctmd_body_len(p);
        ctmd_stream.pos = 0;
        return ctmd_stream.len ? &ctmd_stream : NULL;
    }
    if (mode[0] == 'w' && ends_with(path, ".out")) {
        artifact_stream.len = 0;
        artifact_stream.pos = 0;
        return &artifact_stream;
    }
    return NULL;
}

int fclose(FILE *stream) {
    (void)stream; /* vse streamy staticheskie */
    return 0;
}

static void stream_putc(FILE *f, unsigned char c) {
    if (f->kind == PMF_COM1) {
        com_putc(c);
    } else if (f->writable && f->pos < f->cap) {
        f->buf[f->pos++] = c;
        if (f->pos > f->len)
            f->len = f->pos;
    }
}

int fputc(int c, FILE *stream) {
    stream_putc(stream, (unsigned char)c);
    return c;
}

int fgetc(FILE *stream) {
    if (stream->pos < stream->len && stream->kind != PMF_COM1)
        return (int)stream->buf[stream->pos++];
    return EOF;
}

char *fgets(char *s, int size, FILE *stream) {
    int i = 0;
    int c;
    if (!s || size <= 0)
        return NULL;
    while (i < size - 1) {
        c = fgetc(stream);
        if (c == EOF)
            break;
        s[i++] = (char)c;
        if (c == '\n')
            break;
    }
    if (!i)
        return NULL;
    s[i] = '\0';
    return s;
}

size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream) {
    size_t want, have, got;
    if (!size || !nmemb || stream->kind == PMF_COM1)
        return 0;
    want = size * nmemb;
    have = (stream->pos < stream->len) ? (size_t)(stream->len - stream->pos) : 0u;
    got = (want < have) ? want : have;
    if (got)
        memcpy(ptr, stream->buf + stream->pos, got);
    stream->pos += got;
    return got / size;
}

size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream) {
    size_t i, j;
    const unsigned char *p = (const unsigned char *)ptr;
    for (i = 0; i < nmemb; i++) {
        for (j = 0; j < size; j++)
            stream_putc(stream, p[i * size + j]);
    }
    return nmemb;
}

int fseek(FILE *stream, long offset, int whence) {
    unsigned long base;
    long at;
    if (stream->kind == PMF_COM1)
        return 0;
    if (whence == SEEK_SET)
        base = 0;
    else if (whence == SEEK_CUR)
        base = stream->pos;
    else if (whence == SEEK_END)
        base = stream->len;
    else
        return -1;
    at = (long)base + offset;
    if (at < 0)
        return -1;
    if (stream->writable && (unsigned long)at > stream->cap)
        return -1;
    stream->pos = (unsigned long)at;
    return 0;
}

long ftell(FILE *stream) {
    return (long)stream->pos;
}

void rewind(FILE *stream) {
    stream->pos = 0;
}

int fflush(FILE *stream) {
    (void)stream;
    return 0;
}

/* ---- formirovanie vyvoda ---- */
/* long division: bez libgcc __udivmoddi4 */
static uint64_t udiv10(uint64_t v, unsigned *rem) {
    uint64_t q = 0;
    unsigned r = 0;
    int i;
    for (i = 63; i >= 0; i--) {
        r = (r << 1) | (unsigned)((v >> i) & 1u);
        if (r >= 10u) {
            r -= 10u;
            q |= ((uint64_t)1u << i);
        }
    }
    *rem = r;
    return q;
}

static void emit_uint(FILE *f, uint64_t v, int width, int zero, int upper,
                      int *count) {
    char digits[24];
    int n = 0;
    const char *map = upper ? "0123456789ABCDEF" : "0123456789abcdef";
    do {
        unsigned rem;
        if (upper) {
            rem = (unsigned)(v & 15u);
            v >>= 4;
        } else {
            v = udiv10(v, &rem);
        }
        digits[n++] = map[rem];
    } while (v && n < (int)sizeof(digits));
    {
        /* Паддинг не трогает n: n — число знаков числа, digits[] читается
           только в пределах n, иначе в %08X попадают остатки прошлого вызова. */
        int pad = n;
        while (pad < width) {
            stream_putc(f, (unsigned char)(zero ? '0' : ' '));
            (*count)++;
            pad++;
        }
    }
    while (n) {
        stream_putc(f, (unsigned char)digits[--n]);
        (*count)++;
    }
}

static int format(FILE *f, const char *fmt, va_list ap) {
    const char *p = fmt;
    int count = 0;
    while (*p) {
        if (*p != '%') {
            stream_putc(f, (unsigned char)*p++);
            count++;
            continue;
        }
        p++;
        if (!*p)
            break;
        if (*p == '%') {
            stream_putc(f, '%');
            count++;
            p++;
            continue;
        }
        {
            int zero = 0, width = 0, longlong = 0;
            if (*p == '0') {
                zero = 1;
                p++;
            }
            while (*p >= '0' && *p <= '9') {
                width = width * 10 + (*p - '0');
                p++;
            }
            if (*p == 'l') {
                if (*(p + 1) == 'l') {
                    longlong = 1;
                    p += 2;
                } else {
                    p++;
                }
            }
            {
                char c = *p++;
                switch (c) {
                case 's': {
                    char *s = va_arg(ap, char *);
                    if (!s)
                        s = "(null)";
                    while (*s) {
                        stream_putc(f, (unsigned char)*s++);
                        count++;
                    }
                    break;
                }
                case 'c':
                    stream_putc(f, (unsigned char)va_arg(ap, int));
                    count++;
                    break;
                case 'u':
                    emit_uint(f, longlong ? va_arg(ap, uint64_t)
                                          : (uint64_t)va_arg(ap, uint32_t),
                              width, zero, 0, &count);
                    break;
                case 'X':
                case 'x':
                    emit_uint(f, longlong ? va_arg(ap, uint64_t)
                                          : (uint64_t)va_arg(ap, uint32_t),
                              width, zero, (c == 'X'), &count);
                    break;
                case 'd':
                case 'i': {
                    int v = va_arg(ap, int);
                    if (v < 0) {
                        stream_putc(f, '-');
                        count++;
                        emit_uint(f, (uint64_t)(-(int64_t)v), width, zero,
                                  0, &count);
                    } else {
                        emit_uint(f, (uint64_t)v, width, zero, 0, &count);
                    }
                    break;
                }
                default:
                    stream_putc(f, '?');
                    count++;
                }
            }
        }
    }
    return count;
}

int fprintf(FILE *stream, const char *fmt, ...) {
    va_list ap;
    int n;
    va_start(ap, fmt);
    n = format(stream, fmt, ap);
    va_end(ap);
    return n;
}

int snprintf(char *buf, size_t size, const char *fmt, ...) {
    FILE tmp;
    va_list ap;
    int n;
    tmp.buf = (unsigned char *)buf;
    tmp.cap = size ? (unsigned long)(size - 1u) : 0u;
    tmp.len = 0;
    tmp.pos = 0;
    tmp.kind = PMF_MEM_WRITE;
    tmp.writable = 1;
    va_start(ap, fmt);
    n = format(&tmp, fmt, ap);
    va_end(ap);
    if (size)
        buf[tmp.len] = '\0';
    return n;
}

/* ---- chestnyi otkaz i init mingw ---- */
void exit(int status) {
    (void)status;
    __asm__ __volatile__(
        "movw $0xF4, %%dx\n\t"
        "movw $0x0014, %%ax\n\t"
        "outw %%ax, %%dx\n\t"
        "1:\n\t"
        "hlt\n\t"
        "jmp 1b"
        :
        :
        : "ax", "dx", "memory");
}

void __main(void) {
}

void __chkstk_ms(void) {
}
