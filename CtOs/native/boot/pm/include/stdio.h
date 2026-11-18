#ifndef PM_STDIO_H
#define PM_STDIO_H

#include <stddef.h>

/* In-memory / COM1 FILE. Поля видимы shim'у; native_rt.c использует только
   FILE * и поэтому остаётся неизменным. */
typedef struct pm_file {
    unsigned char *buf;
    unsigned long len;
    unsigned long cap;
    unsigned long pos;
    int kind;      /* 0 = COM1, 1 = read-only memory, 2 = memory artifact */
    int writable;
} FILE;

extern FILE *stderr;
extern FILE *stdout;

#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
#define EOF (-1)

int fprintf(FILE *stream, const char *fmt, ...);
int snprintf(char *buf, size_t size, const char *fmt, ...);
FILE *fopen(const char *path, const char *mode);
int fclose(FILE *stream);
int fputc(int c, FILE *stream);
int fgetc(FILE *stream);
char *fgets(char *s, int size, FILE *stream);
size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream);
size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream);
int fseek(FILE *stream, long offset, int whence);
long ftell(FILE *stream);
void rewind(FILE *stream);
int fflush(FILE *stream);

#endif
