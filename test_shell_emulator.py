import unittest
import os
import tarfile
from shell_emulator import ShellEmulator


class TestShellEmulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_tar_path = "test_vfs.tar"
        cls.test_log_path = "test_log.xml"
        cls.vfs_root = "test_vfs"

        os.makedirs(f"{cls.vfs_root}/dir1", exist_ok=True)
        os.makedirs(f"{cls.vfs_root}/dir2", exist_ok=True)
        with open(f"{cls.vfs_root}/file1.txt", "w") as f:
            f.write("This is file1.")
        with open(f"{cls.vfs_root}/dir1/file2.txt", "w") as f:
            f.write("This is file2 in dir1.")

        with tarfile.open(cls.test_tar_path, "w") as tar:
            tar.add(cls.vfs_root, arcname=".")

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_tar_path)
        for root, dirs, files in os.walk(cls.vfs_root, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(cls.vfs_root)

    def setUp(self):
        self.emulator = ShellEmulator(self.test_tar_path, self.test_log_path)
        self.emulator.setup_vfs()

    def tearDown(self):
        self.emulator.exit()

    def test_ls(self):
        result = self.emulator.ls()
        self.assertIn("file1.txt", result)
        self.assertIn("dir1", result)
        self.assertIn("dir2", result)

    def test_cd(self):
        self.assertEqual(self.emulator.cd("dir1"), "")
        self.assertIn("file2.txt", self.emulator.ls())

        result = self.emulator.cd("nonexistent")
        self.assertEqual(result, "cd: nonexistent: No such directory")

    def test_rmdir(self):
        result = self.emulator.rmdir("dir2")
        self.assertEqual(result, "")
        self.assertNotIn("dir2", self.emulator.ls())

        result = self.emulator.rmdir("nonexistent")
        self.assertEqual(result, "rmdir: nonexistent: No such directory")

    def test_tree(self):
        result = self.emulator.tree()
        expected_structure = "dir1\nfile2.txt\ndir2\nfile1.txt"
        for line in expected_structure.split("\n"):
            self.assertIn(line, result)

    def test_exit(self):
        result = "Exiting..."
        self.assertEqual(result, "Exiting...")

    def test_log_file(self):
        self.emulator.ls()
        self.emulator.cd("dir1")
        self.emulator.save_log()

        self.assertTrue(os.path.exists(self.test_log_path))

        with open(self.test_log_path, "r") as log_file:
            log_content = log_file.read()
            self.assertIn("<action>ls</action>", log_content)
            self.assertIn("<action>cd dir1</action>", log_content)


if __name__ == "__main__":
    unittest.main()
