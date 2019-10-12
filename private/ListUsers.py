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
        print(self.usersFetch)


if __name__ == "__main__":
    try:
        L = ListUsers(CFG.args.unapproved)
        print("hi")
        exit(0)
    except KeyboardInterrupt:
        pass
