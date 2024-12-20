# Домашнее задание №1
# Вариант №29

Запуск эмулятора:

**` python shell_emulator.py --vfs vfs.tar --log log.xml --script startup_script.txt `**

Запуск тестов:

**` python -m unittest test_shell_emulator.py `**

### **Команды, поддерживаемые в интерфейсе:**
- `ls` — выводит содержимое текущей директории.
- `cd <path>` — переходит в указанную директорию.
- `rmdir <dir_name>` — удаляет указанную директорию.
- `tree` — отображает содержимое текущей директории в виде дерева.
- `exit` — завершает работу, сохраняет лог и очищает временную директорию.

### **Класс ShellEmulator**
Эмулирует простую оболочку (shell) с поддержкой работы с виртуальной файловой системой (VFS) и логированием действий в XML.

1. **`__init__(self, vfs_path, log_path)`**  
   Инициализация объекта эмулятора.  
   - `vfs_path` — путь к TAR-архиву с виртуальной файловой системой.  
   - `log_path` — путь для сохранения XML-лога.  
   - Создает корневую директорию VFS и XML-древо для логирования.

2. **`setup_vfs(self)`**  
   Распаковывает архив TAR в виртуальную файловую систему (директория `/tmp/vfs`) и устанавливает начальный путь.

3. **`_clear_vfs(self)`**  
   Очищает временную директорию VFS, удаляя все файлы и папки.

4. **`log_action(self, action, result)`**  
   Добавляет запись о выполненном действии (команда + результат) в XML-лог.

5. **`save_log(self)`**  
   Сохраняет XML-лог в файл, указанный при инициализации.

6. **`ls(self)`**  
   Выводит содержимое текущей директории (аналог `ls`) и логирует действие.

7. **`cd(self, path)`**  
   Переходит в указанную директорию (аналог `cd`). Логирует успешный переход или ошибку.

8. **`rmdir(self, dir_name)`**  
   Удаляет указанную директорию (аналог `rmdir`). Логирует результат.

9. **`tree(self, path=None, level=0)`**  
   Рекурсивно отображает содержимое директории в виде дерева (аналог `tree`). Логирует результат.

10. **`exit(self)`**  
    Завершает работу: сохраняет лог и очищает виртуальную файловую систему.

### **Класс ShellGUI**
Графический интерфейс для работы с эмулятором оболочки на основе Tkinter.

1. **`__init__(self, emulator, script_path=None)`**  
   Инициализация графического интерфейса:  
   - Создает текстовое поле для вывода результатов и поле ввода команд.  
   - Запускает стартовый скрипт, если указан.

2. **`run_startup_script(self)`**  
   Выполняет команды из указанного файла скрипта при запуске.

3. **`execute_command(self, event)`**  
   Обрабатывает команду, введенную пользователем в поле ввода, и отображает результат в текстовом поле.

4. **`handle_command(self, command)`**  
   Выполняет указанную команду с использованием методов `ShellEmulator`. Поддерживает команды `ls`, `cd`, `rmdir`, `tree`, `exit`.

5. **`run(self)`**  
   Запускает главный цикл Tkinter для отображения интерфейса.

### **Функция `main()`**
1. Обрабатывает аргументы командной строки:
   - `--vfs` — путь к TAR-архиву виртуальной файловой системы (обязательно).
   - `--log` — путь для сохранения XML-лога (обязательно).
   - `--script` — путь к скрипту с командами для выполнения при запуске (опционально).

2. Создает объект `ShellEmulator`, настраивает виртуальную файловую систему и запускает графический интерфейс `ShellGUI`.
