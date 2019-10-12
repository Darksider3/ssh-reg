#!/usr/bin/env python3

from lib.sqlitedb import SQLitedb
import lib.CFG as CFG


class ListUsers:
    db = None
    usersFetch = None

    def __init__(self, ap: bool):
        self.db = SQLitedb(CFG.REG_FILE)
        if not ap:
            query = "SELECT * FROM `applications` WHERE status = '1'"
        else:
            query = "SELECT * FROM `applications` WHERE status = '0'"
        self.usersFetch = self.db.query(query)

    def prettyPrint(self):
        pass # see below why not implemented yet, texttable...

    def getFetch(self):
        return self.usersFetch


if __name__ == "__main__":
    try:
        L = ListUsers(CFG.args.unapproved)
        fetch = L.getFetch()
        # MAYBE best solution: https://pypi.org/project/texttable/
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
        print("ID %-1s| Username %-5s| Mail %-20s| Name %-17s| Registered %-8s| State |" % (
            " ", " ", " ", " ", " "
        ))
        print(101*"-")
        for user in fetch:
            print("%-4i| %-14s| %-25s| %-22s| %-8s| %-6i|" % (
                user["id"], user["username"], user["email"], user["name"], user["timestamp"], user["status"]
            ))
        exit(0)
    except KeyboardInterrupt:
        pass
