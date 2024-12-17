import os
import tarfile
import xml.etree.ElementTree as ET
import argparse
from tkinter import Tk, Text, Entry, Button, END

class ShellEmulator:
    def __init__(self, vfs_path, log_path):
        self.vfs_path = vfs_path
        self.log_path = log_path
        self.current_path = None
        self.vfs_root = "/tmp/vfs"  # Временная директория
        self.files = {}  # Словарь для хранения файлов из VFS
        self.members = []  # Список для хранения членов архива

        # XML логирование
        self.log_root = ET.Element("log")
        self.setup_vfs()  # Инициализация VFS при создании экземпляра

    def setup_vfs(self):
        """Настройка виртуальной файловой системы из tar-архива."""
        if os.path.exists(self.vfs_root):
            self._clear_vfs()
        os.makedirs(self.vfs_root)

        with tarfile.open(self.vfs_path, 'r') as tar:
            # Сохраняем информацию о членах архива без их извлечения
            self.members = tar.getmembers()
            for member in self.members:
                if member.isfile():
                    # Читаем содержимое файла в памяти
                    file_content = tar.extractfile(member).read()
                    self.files[member.name] = file_content

        self.current_path = self.vfs_root

    def _clear_vfs(self):
        """Очистка временной директории VFS."""
        for root, dirs, files in os.walk(self.vfs_root, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.vfs_root)

    def rmdir(self, folder_name):
        """Удаляет указанный каталог, если он пустой."""
        folder_path = os.path.join(self.current_path, folder_name)
        
        if any(member.name == folder_path and member.isdir() for member in self.members):
            if not any(member.name.startswith(folder_path + '/') for member in self.members):

                del self.files[folder_path]
                self.log_action("rmdir", f"Removed directory: {folder_path}")
                return f"Directory '{folder_name}' removed."
            else:
                return f"Directory '{folder_name}' is not empty and cannot be removed."
        else:
            return f"Directory '{folder_name}' does not exist."

    def log_action(self, action, result):
        """Логирует действия (заглушка)."""
        with open(self.log_path, 'a') as log_file:
            log_file.write(f"{action}: {result}\n")

    def save_log(self):
        """Сохранение лога в файл."""
        tree = ET.ElementTree(self.log_root)
        tree.write(self.log_path)

    def ls(self):
        """Список файлов и папок в текущем каталоге."""
        result = "\n".join(self.files)
        self.log_action("ls", result)
        return result

    def cd(self, folder_name):
        """Сменяет текущий каталог на указанный."""
        if folder_name == "..":
            # Переход к родительскому каталогу
            if self.current_path != "/":
                self.current_path = os.path.dirname(self.current_path.rstrip('/'))
        else:
            new_path = os.path.join(self.current_path, folder_name).rstrip('/')
            # Проверяем, существует ли каталог
            if new_path in self.files and isinstance(self.files[new_path], dict):
                self.current_path = new_path
                self.log_action("cd", f"Changed directory to: {self.current_path}")
                return f"Changed directory to '{folder_name}'."
            else:
                return f"Directory '{folder_name}' does not exist."

    def tree(self, path="", level=0):
        """Выводит структуру файлов и папок в виде дерева."""
        result = ""
        prefix = " " * (level * 4)  # 4 пробела на уровень вложенности
        added_folders = set()  # Множество для отслеживания добавленных папок

        # Получаем список файлов и папок по текущему пути
        for member in self.members:
            if member.name.startswith(path):
                # Убираем путь, чтобы отобразить только имя
                relative_path = member.name[len(path):].lstrip('/')
                if '/' in relative_path:
                    # Если это папка, добавляем ее в результат
                    folder_name = relative_path.split('/')[0]
                    if folder_name not in added_folders:
                        result += f"{prefix}{folder_name}/\n"
                        added_folders.add(folder_name)  # Добавляем папку в множество
                        # Рекурсивно добавляем содержимое папки
                        result += self.tree(f"{path}{folder_name}/", level + 1)
                else:
                    # Если это файл, добавляем его в результат
                    result += f"{prefix}{relative_path}\n"

        self.log_action("tree", result)
        return result

    def exit(self):
        """Выход из эмулятора."""
        self.save_log()
        self._clear_vfs()
        return "Exiting..."

class ShellGUI:
    def __init__(self, emulator, script_path=None):
        self.emulator = emulator
        self.script_path = script_path
        self.root = Tk()
        self.root.title("Shell Emulator")
        self.output = Text(self.root, height=20, width=80)
        self.output.pack()
        self.command_entry = Entry(self.root, width=80)
        self.command_entry.pack()
        self.command_entry.bind("<Return>", self.execute_command)
        self.run_startup_script()

    def run_startup_script(self):
        """Запуск скрипта при старте."""
        if self.script_path and os.path.exists(self.script_path):
            with open(self.script_path, 'r') as script_file:
                commands = script_file.readlines()
            for command in commands:
                self.handle_command(command.strip())

    def execute_command(self, event):
        """Обработка ввода команды пользователем."""
        command = self.command_entry.get()
        self.command_entry.delete(0, END)
        result = self.handle_command(command)
        self.output.insert(END, f"$ {command}\n{result}\n")

    def handle_command(self, command):
        """Обработка команды."""
        parts = command.split()
        if not parts:
            return ""
        cmd = parts[0]
        args = parts[1:]
        if cmd == "ls":
            return self.emulator.ls()
        elif cmd == "cd":
            return self.emulator.cd(args[0] if args else "")
        elif cmd == "rmdir":
            return self.emulator.rmdir(args[0] if args else "")
        elif cmd == "tree":
            return self.emulator.tree()
        elif cmd == "exit":
            result = self.emulator.exit()
            self.root.quit()
            return result
        else:
            return f"{cmd}: command not found"

    def run(self):
        """Запуск GUI."""
        self.root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("--vfs", required=True, help="Path to VFS tar archive")
    parser.add_argument("--log", required=True, help="Path to log file")
    parser.add_argument("--script", required=False, help="Path to startup script")
    args = parser.parse_args()

    emulator = ShellEmulator(args.vfs, args.log)
    gui = ShellGUI(emulator, args.script)
    gui.run()

if __name__ == "__main__":
    main()

