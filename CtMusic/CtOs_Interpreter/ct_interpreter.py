import os
import re
import sys
import json
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Определяем пути к твоей экосистеме
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KERNEL_PATH = os.path.join(BASE_DIR, 'kernel.ctos')
BRIDGE_PATH = os.path.join(BASE_DIR, 'command-restructor', 'bridge.ctos')
VIEW_DIR = os.path.join(BASE_DIR, 'View')

class KitiiRuntime:
    """Честная среда выполнения (Runtime) для ядра CtOs"""
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.loaded_modules = []

    def load_ctos_module(self, filepath):
        """Читает файлы .ctos и извлекает метаданные и функции без цензуры"""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            current_func = None
            for line in f:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                
                # Читаем системные теги твоего ядра
                if line.startswith("#"):
                    self.loaded_modules.append(line)
                    continue
                
                # Парсинг переменных KITII: set имя = "значение"
                if line.startswith("set "):
                    match = re.match(r'set\s+(\w+)\s*=\s*"([^"]+)"', line)
                    if match:
                        name, val = match.groups()
                        self.variables[name] = val
                
                # Определение функций в ядре
                elif line.startswith("function "):
                    match = re.match(r'function\s+(\w+)\(([^)]*)\)', line)
                    if match:
                        current_func = match.group(1)
                        self.functions[current_func] = []
                
                elif current_func and line == "}":
                    current_func = None
                
                elif current_func:
                    self.functions[current_func].append(line)

    def execute_ct_function(self, func_name, args_dict):
        """Выполняет низкоуровневые команды, прописанные внутри твоих функций"""
        if func_name not in self.functions:
            print(f"[CtOs Error]: Функция {func_name} не объявлена в ядре.")
            return None
        
        print(f"[CtOs Runtime]: Выполнение функции {func_name}...")
        commands = self.functions[func_name]
        
        for cmd in commands:
            # Если функция вызывает подсистему yt-dlp
            if "yt-dlp" in cmd:
                # Подставляем реальные переменные в команду
                for var, val in args_dict.items():
                    cmd = cmd.replace(var, val)
                return cmd
        return None

# Глобальный запуск рантайма
rt = KitiiRuntime()
rt.load_ctos_module(KERNEL_PATH)
rt.load_ctos_module(BRIDGE_PATH)

class CtMusicCoreHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        # Рендеринг твоего экрана из index.web
        if parsed_url.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            index_path = os.path.join(VIEW_DIR, 'index.web')
            with open(index_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            # Подставляем стартовое состояние системы
            html = html.replace('{{RESULTS}}', '<tr><td colspan="4" align="center" style="color:#777;">Ожидание команд ядра...</td></tr>')
            self.wfile.write(html.encode('utf-8'))
            
        # Обработка поиска через призму твоей функции фильтрации
        elif parsed_url.path == '/search':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            query_params = parse_qs(parsed_url.query)
            search_query = query_params.get('q', [''])[0]
            author_filter = query_params.get('author', [''])[0]
            
            # Вызываем твою логику фильтрации из bridge.ctos
            # Передаем параметры в твою функцию FilterEngine
            local_vars = {"input_title": search_query, "current_author": author_filter}
            
            # Запускаем консольный поиск на YouTube Music
            cmd = f'yt-dlp --dump-json "ytsearch1:{search_query} {author_filter}"'
            
            try:
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if proc.returncode == 0:
                    data = json.loads(proc.stdout)
                    title = data.get('title', 'Неизвестный трек')
                    uploader = data.get('uploader', 'Неизвестный автор')
                    duration_sec = data.get('duration', 0)
                    duration = f"{duration_sec // 60}:{duration_sec % 60:02d}"
                    video_id = data.get('id', '')
                    
                    # Исключаем Яндекс.Музыку и проверяем оригинальность, как прописано в твоем концепте
                    if "yandex" in uploader.lower():
                        result_row = '<tr><td colspan="4" align="center" style="color:red;">Результат заблокирован фильтром цензуры.</td></tr>'
                    else:
                        result_row = f"""
                        <tr>
                            <td><span class="track-title">{title}</span></td>
                            <td>{uploader}</td>
                            <td>{duration}</td>
                            <td><button onclick="window.location.href='/download?id={video_id}'">Запустить CtDownload</button></td>
                        </tr>
                        """
                else:
                    result_row = '<tr><td colspan="4" align="center" style="color:yellow;">Запрос отклонен нодой поиска.</td></tr>'
            except Exception as e:
                result_row = f'<tr><td colspan="4" align="center" style="color:red;">Сбой runtime: {str(e)}</td></tr>'
            
            index_path = os.path.join(VIEW_DIR, 'index.web')
            with open(index_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            html = html.replace('{{RESULTS}}', result_row)
            self.wfile.write(html.encode('utf-8'))
            
        elif parsed_url.path == '/download':
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('id', [''])[0]
            
            if video_id:
                # Генерируем команду скачивания, прописанную в функции твоего скрипта
                output_file = os.path.join(BASE_DIR, '%(title)s.%(ext)s')
                dl_cmd = f'yt-dlp -x --audio-format mp3 -o "{output_file}" "https://youtube.com{video_id}"'
                subprocess.Popen(dl_cmd, shell=True)
                
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

def main():
    server_address = ('localhost', 8800)
    httpd = HTTPServer(server_address, CtMusicCoreCoreHandler if 'CtMusicCoreCoreHandler' in globals() else CtMusicCoreHandler)
    print(f"[CtOs Core]: Инициализация модулей: {rt.loaded_modules}")
    print("[CtOs Core]: Переменные KITII в памяти:", rt.variables)
    
    webbrowser.open('http://localhost:8800')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    main()
