#!/usr/bin/env python3

from lib.sqlitedb import SQLitedb
import lib.CFG


class ListUsers:
    db = None
    usersFetch = None

    def __init__(self, uap: bool = lib.CFG.args.unapproved, app: bool = lib.CFG.args.approved):
        self.db = SQLitedb(lib.CFG.config['DEFAULT']['applications_db'])
        if uap:  # only unapproved users
            query = "SELECT * FROM `applications` WHERE status = '0'"
        elif app:  # Approved users
            query = "SELECT * FROM `applications` WHERE status = '1'"
        else:  # All users
            query = "SELECT * FROM `applications`"
        self.usersFetch = self.db.query(query)

    def prettyPrint(self) -> None:
        pass  # see below why not implemented yet, texttable...

    def getFetch(self) -> list:
        """ Returns a complete fetch done by the sqlitedb-class

        :return: Complete fetchall() in a dict-factory
        :rtype: list
        """
        return self.usersFetch


if __name__ == "__main__":
    try:
        ret = ""
        L = ListUsers()
        fetch = L.getFetch()
        # @TODO MAYBE best solution: https://pypi.org/project/texttable/
        # examle:
        """
from texttable import Texttable
t = Texttable()
t.add_rows([['Name', 'Age'], ['Alice', 24], ['Bob', 19]])
print(t.draw())
---------------> Results in:

+-------+-----+
| Name  | Age |
+=======+=====+
| Alice | 24  |
+-------+-----+
| Bob   | 19  |
+-------+-----+

              for user in fetch:
            print("ID: {}; Username: \"{}\"; Mail: {}; Name: \"{}\"; Registered: {}; Status: {}".format(
                user["id"], user["username"], user["email"], user["name"], user["timestamp"], user["status"]
            ))"""
        ret += "ID %-1s| Username %-5s| Mail %-20s| Name %-17s| Registered %-8s | State |\n" % (
            " ", " ", " ", " ", " "
        )
        ret += 102 * "-" + "\n"
        for user in fetch:
            ret += "%-4i| %-14s| %-25s| %-22s| %-8s | %-5i |\n" % (
                user["id"], user["username"], user["email"], user["name"], user["timestamp"], user["status"]
            )
        if lib.CFG.args.file != "stdout":
            with open(lib.CFG.args.file, 'w') as f:
                print(ret, file=f)
        else:
            print(ret)
        exit(0)
    except KeyboardInterrupt:
        pass
