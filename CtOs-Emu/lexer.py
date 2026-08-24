import re
import sys

# Системная спецификация токенов для движка токенизации KITII
СПЕЦИФИКАЦИЯ_ТОКЕНОВ = [
    # Системные директивы и теги конфигурации ядра
    ('TOKEN_SYS_CORE',     r'#core:'),
    ('TOKEN_SYS_TARGET',   r'#target:'),
    ('TOKEN_SYS_FIRMWARE', r'#firmware:'),
    
    # Низкоуровневые аппаратные операторы и хуки прерываний
    ('TOKEN_OP_HARDLINK',  r'&- import\b'),
    ('TOKEN_OP_SYSCALL',   r'sys_call\b'),
    
    # Токены распределения ячеек оперативной памяти
    ('TOKEN_TYPE_CELL',    r'cell:raw\b'),
    ('TOKEN_KEY_SET',      r'set\b'),
    ('TOKEN_MOD_STATIC',   r'static\b'),
    
    # Контекстные блоки и ключевые слова логики выполнения
    ('TOKEN_KEY_FUNCTION', r'function\b'),
    ('TOKEN_KEY_PUBENTRY', r'pub entry\b'),
    ('TOKEN_KEY_RUN',      r'run\b'),
    ('TOKEN_KEY_IF',       r'if\b'),
    ('TOKEN_KEY_ELSE',     r'else\b'),
    ('TOKEN_KEY_TERMINATE',r'terminate\b'),
    
    # Облегченные макросы пакетного менеджера и утилит сети
    ('TOKEN_LITE_NETALL',      r'net_all\b'),
    ('TOKEN_LITE_NETUP',       r'net_up\b'),
    ('TOKEN_LITE_NETDOWN',     r'net_down\b'),
    ('TOKEN_LITE_NETFLUSH',    r'net_flush\b'),
    ('TOKEN_LITE_NETARP',      r'net_arp\b'),
    ('TOKEN_LITE_PING',        r'go\b'),
    ('TOKEN_LITE_TRACERT',     r'trace\b'),
    ('TOKEN_LITE_MSFIND',      r'music_find\b'),
    ('TOKEN_LITE_MSGET',       r'music_get\b'),
    ('TOKEN_LITE_PININSTALL',  r'pinup_install\b'),
    ('TOKEN_LITE_PINDOWNLOAD', r'pinup_download\b'),
    ('TOKEN_LITE_PINWEB',      r'pinup_web\b'),
    ('TOKEN_LITE_PINDIR',      r'pinup_dir\b'),
    ('TOKEN_LITE_PINLIT',      r'pinup_lit\b'),
    ('TOKEN_LITE_PINFIN',      r'pinup_fin\b'),
    
    # Литералы, шестнадцатеричные адреса регистров и имена (идентификаторы)
    ('TOKEN_LIT_STRING',   r'"[^"]*"'),
    ('TOKEN_LIT_HEX',      r'0x[0-9a-fA-F]+'),
    ('TOKEN_LIT_NUMBER',   r'\b\d+\b'),
    ('TOKEN_IDENTIFIER',   r'\b[a-zA-Z_]\w*\b'),
    
    # Операторы, знаки разделения инструкций и скобки
    ('TOKEN_OP_ASSIGN',    r'='),
    ('TOKEN_SYM_LBRACE',   r'\{'),
    ('TOKEN_SYM_RBRACE',   r'\}'),
    ('TOKEN_SYM_LPAREN',   r'\('),
    ('TOKEN_SYM_RPAREN',   r'\)'),
    ('TOKEN_SYM_SEMICOLON',r';'),
    
    # Скрытые структурные разделители (пробелы и знаки табуляции)
    ('TOKEN_SYM_SKIP',     r'[ \t]+'),
]

class ЛексерKitii:
    def __init__(self):
        # Динамически собираем единое регулярное выражение для высокой скорости разбора
        self.регулярка = re.compile('|'.join(f'(?P<{имя}>{шаблон})' for имя, шаблон in SPECI_TOKENS if (SPECI_TOKENS := СПЕЦИФИКАЦИЯ_ТОКЕНОВ)))

    def разобрать_код(self, исходный_код):
        токены = []
        номер_строки = 1
        текущая_позиция = 0
        
        # Цикл посимвольного потокового анализа кода
        while текущая_позиция < len(исходный_код):
            # 1. Перехватываем и отсекаем однострочные системные комментарии
            if исходный_код[текущая_позиция:].startswith('//'):
                конец_строки = исходный_код.find('\n', текущая_позиция)
                if конец_строки == -1:
                    break
                текущая_позиция = конец_строки
                continue
                
            # 2. Считаем строки при обнаружении переноса кадра
            if исходный_код[текущая_позиция] == '\n':
                номер_строки += 1
                текущая_позиция += 1
                continue
                
            # 3. Сверяем символы с нашей мастер-матрицей токенов
            совпадение = self.регулярка.match(исходный_код, текущая_позиция)
            if совпадение:
                тип_токена = совпадение.lastgroup
                значение_токена = совпадение.group(тип_токена)
                
                # Пробелы пропускаем, чтобы не засорять системный стек
                if тип_токена != 'TOKEN_SYM_SKIP':
                    токены.append({
                        'type': тип_токена,
                        'value': значение_токена,
                        'line': номер_строки
                    })
                текущая_позиция = совпадение.end()
            else:
                # Фиксация аппаратного сбоя синтаксиса
                неизвестный_символ = исходный_код[текущая_позиция]
                print(f"[Ошибка лексера KITII]: Обнаружен недопустимый символ '{неизвестный_символ}' на строке {номер_строки}")
                sys.exit(1)
                
        return токены

# Блок внутренней верификации и имитации ранней загрузки ядра (Early Boot)
if __name__ == "__main__":
    import time

    # Симуляция текстовых логов Verbose Boot при старте CtOs
    print("\n" + "="*70)
    print("[0.000000] Развертывание ядра CtOs Core (Версия: 1.00_OldKernel)...")
    time.sleep(0.1)
    print("[0.004102] Проверка аппаратного профиля хоста... OK")
    print("[0.012541] Аллокатор памяти memory.ctos: Инициализация пула 32МБ... OK")
    time.sleep(0.1)
    print("[0.032190] Системная шина bridge.ctos: Поиск аппаратного моста M10_SM_M15...")
    print("[0.045091] Аппаратный мост: Межплатный шлейф MAIN <-> SUB обнаружен.")
    time.sleep(0.1)
    print("[0.061204] Загрузка модулей: Драйвер ввода-вывода (IC4502), Драйвер питания (IC7001)...")
    print("[0.078912] Слой Void: Загрузка грамматики и таблицы токенов из lexicon.core...")
    print("="*70 + "\n")
    
    # Тестовый сценарий, имитирующий запуск плеера CtMusic
    тестовый_скрипт = """
    #core: CtOs_Old
    #target: ARM32
    
    function ИнициализацияАудио() {
        net_flush;
        pinup_web "CtMusic аудио плеер";
        music_get "TennoConcert_2026";
        terminate;
    }
    """
    
    time.sleep(0.2)
    print("[Ядро CtOs]: Сборка исходного кода приложения CtMusic...")
    
    # Запуск нашего Лексера
    лексер = ЛексерKitii()
    поток_токенов = лексер.разобрать_код(тестовый_скрипт)
    
    print(f"[Ядро CtOs]: Лексический разбор завершен успешно. Сгенерирован поток токенов ({len(поток_токенов)} элементов):")
    print("-"*70)
    for пакет in поток_токенов:
        print(f"  Строка {пакет['line']}: {пакет['type']} -> {пакет['value']}")
    print("-"*70)
    print("[0.125043] Ядро CtOs: Передача управления рантайму void.run. Запуск оболочки VSH...")
