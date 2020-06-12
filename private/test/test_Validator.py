import sys
sys.path.append('..')
import unittest
import lib.Validator
import test.testcfg as testcfg


class TestValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = lib.Validator

    def test_check_username_characters(self):
        for name in testcfg.Validator_Valid_Users_Chars_List:
            self.assertTrue(self.validator.checkUsernameCharacters(name))
        for name in testcfg.Validator_Invalid_Users_Chars_List:
            self.assertFalse(self.validator.checkUsernameCharacters(name), name)

    def test_check_username_length(self):
        for name in testcfg.Validator_Valid_Users_Length:
            self.assertTrue(self.validator.checkUsernameLength(name))
        for name in testcfg.Validator_Invalid_Users_Length:
            self.assertFalse(self.validator.checkUsernameLength(name), name)

    def test_check_email(self):
        for name in testcfg.Validator_Valid_Mail:
            self.assertTrue(self.validator.checkEmail(name))
        for name in testcfg.Validator_Invalid_Mail:
            self.assertFalse(self.validator.checkEmail(name))

    def test_check_user_exists(self):
        self.assertTrue(self.validator.checkUserExists("root"))
        self.assertTrue(self.validator.checkUserExists("nobody")) # remove in case there exists an actual system without
        self.assertFalse(self.validator.checkUserExists("blsjdkfl"))
        self.assertFalse(self.validator.checkUserExists("b90123ijk"))
        self.assertFalse(self.validator.checkUserExists("curArrSosss"))
        self.assertFalse(self.validator.checkUserExists("123WildPack123"))
        # are there any more users which are assertable?

    def test_check_user_in_db(self):
        for name in testcfg.Validator_db_user_exists:
            self.assertTrue(self.validator.checkUserInDB(name, testcfg.test_db))
        for name in testcfg.Validator_db_user_inexistent:
            self.assertFalse(self.validator.checkUserInDB(name, testcfg.test_db))

    def test_check_sshkey(self):
        for key in testcfg.Validator_valid_ssh:
            self.assertTrue(self.validator.checkSSHKey(key))
        for key in testcfg.Validator_invalid_ssh:
            self.assertFalse(self.validator.checkSSHKey(key))

    def test_check_datetime_format(self):
        for cur in testcfg.Validator_valid_datetime:
            self.assertTrue(self.validator.checkDatetimeFormat(cur))

    def test_check_name(self):
        for checkname in testcfg.Validator_valid_checkname_names:
            self.assertTrue(self.validator.checkName(checkname))
        for checkname in testcfg.Validator_invalid_checkname_names:
            self.assertFalse(self.validator.checkName(checkname))

    def test_check_import_file(self):
        self.assertTrue(self.validator.checkImportFile(testcfg.test_import_csv,
                                                       testcfg.test_db))
        if not self.validator.checkImportFile(testcfg.test_import_invalid_csv, testcfg.test_db):
            self.fail("Invalid import file should've failed the test")
