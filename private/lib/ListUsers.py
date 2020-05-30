from lib.sqlitedb import SQLiteDB
import sqlite3  # sqlite3.Row-Object
from typing import List  # Typing support!


class ListUsers:
    """
    List tilde users
    """

    db = None
    users_fetch = None

    def __init__(self, db: str, unapproved: bool = False, approved: bool = True, single_user: str = None):
        """Constructs list_users

        :param db: Database to access
        :type db: str
        :param unapproved: only List unapproved users
        :type unapproved: bool
        :param approved: only list approved users
        :type approved: bool
        """

        self.db = SQLiteDB(db)
        if unapproved:  # only unapproved users
            query = "SELECT * FROM `applications` WHERE `status` = '0'"
        elif approved:  # Approved users
            query = "SELECT * FROM `applications` WHERE `status` = '1'"
        else:  # All users
            query = "SELECT * FROM `applications`"
        self.users_fetch = self.db.query(query)
        if single_user is not None:
            query = "SELECT * FROM `applications` WHERE `username` = ?"
            self.users_fetch = self.db.safe_query(query, tuple([single_user]))

    def output_as_list(self) -> str:
        """Generates a string with one (approved) single_user per line and one newline at the end

        :rtype: str
        :return: String consisting with one(activated) single_user per line
        """

        list_str: str = ""
        query = "SELECT `username` FROM `applications` WHERE `status` = '1' ORDER BY timestamp ASC"
        self.users_fetch = self.db.query(query)
        for user in self.users_fetch:
            list_str += user["username"] + "\n"
        return list_str

    def pretty_print(self) -> None:
        """
        pretty-print users
        :return: None
        """
        pass  # see below why not implemented yet, texttable...

    def get_fetch(self) -> List[sqlite3.Row]:
        """ Returns a complete users done by the lib.sqlitedb-class

        :return: Complete fetchall(). A List[sqlite3.Row] with dict-emulation objects.
        :rtype: List[sqlite3.Row]
        """

        return self.users_fetch
