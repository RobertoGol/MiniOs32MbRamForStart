#ifndef PM_STDARG_H
#define PM_STDARG_H

/* Минимальный x86 cdecl va_list: аргументы выровнены по 4 байта. */
typedef char *va_list;

#define __pm_va_size(t) (((sizeof(t) + 3u) & ~3u))
#define va_start(ap, last) ((ap) = (va_list)((char *)&(last) + __pm_va_size(last)))
#define va_arg(ap, t) (*(t *)((ap += __pm_va_size(t)) - __pm_va_size(t)))
#define va_end(ap) ((void)0)

#endif
