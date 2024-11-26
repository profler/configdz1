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

        # XML логирование
        self.log_root = ET.Element("log")

    def setup_vfs(self):
        # Распаковка архива TAR в виртуальную файловую систему
        if os.path.exists(self.vfs_root):
            self._clear_vfs()
        os.makedirs(self.vfs_root)
        with tarfile.open(self.vfs_path, 'r') as tar:
            tar.extractall(self.vfs_root)
        self.current_path = self.vfs_root

    def _clear_vfs(self):
        for root, dirs, files in os.walk(self.vfs_root, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.vfs_root)

    def log_action(self, action, result):
        entry = ET.SubElement(self.log_root, "entry")
        ET.SubElement(entry, "action").text = action
        ET.SubElement(entry, "result").text = result

    def save_log(self):
        tree = ET.ElementTree(self.log_root)
        tree.write(self.log_path)

    def ls(self):
        result = "\n".join(os.listdir(self.current_path))
        self.log_action("ls", result)
        return result

    def cd(self, path):
        target_path = os.path.join(self.current_path, path)
        if os.path.isdir(target_path):
            self.current_path = target_path
            result = ""
        else:
            result = f"cd: {path}: No such directory"
        self.log_action(f"cd {path}", result)
        return result

    def rmdir(self, dir_name):
        target_path = os.path.join(self.current_path, dir_name)
        if os.path.isdir(target_path):
            os.rmdir(target_path)
            result = ""
        else:
            result = f"rmdir: {dir_name}: No such directory"
        self.log_action(f"rmdir {dir_name}", result)
        return result

    def tree(self, path=None, level=0):
        if path is None:
            path = self.current_path
        tree_structure = ""
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            tree_structure += "  " * level + entry + "\n"
            if os.path.isdir(entry_path):
                tree_structure += self.tree(entry_path, level + 1)
        self.log_action("tree", tree_structure.strip())
        return tree_structure.strip()

    def exit(self):
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
        if self.script_path and os.path.exists(self.script_path):
            with open(self.script_path, 'r') as script_file:
                commands = script_file.readlines()
            for command in commands:
                self.handle_command(command.strip())

    def execute_command(self, event):
        command = self.command_entry.get()
        self.command_entry.delete(0, END)
        result = self.handle_command(command)
        self.output.insert(END, f"$ {command}\n{result}\n")

    def handle_command(self, command):
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
        self.root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("--vfs", required=True, help="Path to VFS tar archive")
    parser.add_argument("--log", required=True, help="Path to log file")
    parser.add_argument("--script", required=False, help="Path to startup script")
    args = parser.parse_args()

    emulator = ShellEmulator(args.vfs, args.log)
    emulator.setup_vfs()

    gui = ShellGUI(emulator, args.script)
    gui.run()

if __name__ == "__main__":
    main()
