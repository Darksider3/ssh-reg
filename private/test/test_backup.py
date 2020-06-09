import os
import unittest
import sys
import csv
import backup
sys.path.append('..')
from lib.ListUsers import ListUsers
import test.testcfg as testcfg

class TestBackup(unittest.TestCase):

    def setUp(self):
        try:
            self.fetch = ListUsers(testcfg.test_db, unapproved=False, approved=False).get_fetch()
            self.Backup = backup.Backup(testcfg.test_backup_csv)
        except Exception as general_setup:
            self.fail(f"Failed setup already! {general_setup}")

    def test_set_dialect(self):
        self.Backup.set_dialect("excel")
        self.assertEqual(self.Backup.dialect, "excel")

    def test_set_quoting(self):
        self.Backup.set_quoting(csv.QUOTE_NONNUMERIC)
        self.assertEqual(self.Backup.quoting, csv.QUOTE_NONNUMERIC)

    def test_set_filename(self):
        self.Backup.set_filename(testcfg.test_backup_csv)
        self.assertEqual(self.Backup.filename, testcfg.test_backup_csv)
        self.Backup.set_field_names(self.fetch[0].keys())

    def test_set_field_names(self):
        # @TODO: Dynamic! Having a test scheme from which we setup our test is beneficial here, also values
        self.Backup.set_field_names(self.fetch[0].keys())
        keys_found = self.Backup.field_names
        self.assertEqual(keys_found, ['id', 'username', 'email', 'name', 'pubkey', 'timestamp', 'status'])

    def test_backup_to_file(self):
        try:
            self.Backup.set_field_names(self.fetch[0].keys())
            self.Backup.backup_to_file(self.fetch)
            self.assertTrue(os.path.exists(testcfg.test_backup_csv),
                            "Assert True that file exists and was written")
            os.unlink(os.path.realpath(testcfg.test_backup_csv))
        except IOError as io_error:
            self.fail(io_error)


if __name__ == '__main__':
    unittest.main()
