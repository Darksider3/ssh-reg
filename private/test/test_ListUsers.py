import unittest
import test.testcfg as testcfg
import sys
import os
from lib.ListUsers import ListUsers
sys.path.append('..')

f = open(os.devnull, 'w')
sys.stdout = f


class TestListUsers(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.list = ListUsers(testcfg.test_db, unapproved=False, approved=False)
        except IOError as fs_err:
            self.fail(fs_err)

    def test_output_as_list(self):
        # count newlines in string, everything under 3 is wrong, and above 20 too.
        out = self.list.output_as_list().splitlines()
        self.assertGreater(len(out), testcfg.ListUsers_output_newlines,
                           "Newlines in OUTPUT doesn't exceed minimum of at least "
                           f"{testcfg.ListUsers_output_newlines} "
                           "lines!")
        print(out)

    def test_pretty_print(self):
        # wont going to compare the stdout sorry very much
        return

    def test_get_fetch(self):
        fetch = self.list.get_fetch()
        self.assertIsInstance(fetch, list)
        self.assertGreater(len(fetch),
                           testcfg.ListUsers_fetch_size_min, "fetch is NOT greater than"
                                                             "the configured fetch minimum")
        try:
            print(fetch[0])
        except (KeyError, IOError) as suddenly_not_there:
            self.fail(f"Expected fetch to have at least one argument! {suddenly_not_there}")


if __name__ == '__main__':
    unittest.main()
