import sys

sys.path.append('..')

import unittest
from ListUsers import ListUsers
import backup


class TestBackup(unittest.TestCase):
    test_csv: str = "test/testbackup.csv"
    test_db: str = "./test/applications.sqlite"

    def setUp(self):
        try:
            self.fetch = ListUsers(self.test_db, unapproved=False, approved=False).get_fetch()
            self.Backup = backup.Backup(self.test_csv)
        except Exception as general_setup:
            self.fail(f"Failed setup already! {general_setup}")

    def test_set_dialect(self):
        pass

    def test_set_quoting(self):
        pass

    def test_set_filename(self):
        self.Backup.set_filename(self.test_csv)
        self.assertEqual(self.Backup.filename, self.test_csv)

    def test_set_field_names(self):
        # @TODO: Dynamic! Having a test scheme from which we setup our test is beneficial here, also values
        self.Backup.set_field_names(self.fetch[0].keys())
        keys_found = self.Backup.field_names
        self.assertEqual(keys_found, ['id', 'username', 'email', 'name', 'pubkey', 'timestamp', 'status'])

    def test_backup_to_file(self):
        try:
            self.Backup.backup_to_file(self.fetch)
        except IOError as io_error:
            self.fail(io_error)


if __name__ == '__main__':
    unittest.main()
