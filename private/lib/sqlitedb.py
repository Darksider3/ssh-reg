#!/usr/bin/env python3
import sqlite3
from sys import stderr as STDERR


# create dictionary out of sqlite results
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLitedb:
    db = ""
    cursor = None
    connection = None
    lastrow = None

    def __init__(self, dbpath: str):
        db = dbpath
        try:
            self.connection = sqlite3.connect(db)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print("Connection error: %s" % e, file=STDERR)

        self.cursor.row_factory = dict_factory # every result will be a dict now

    def __del__(self):
        try:
            self.connection.close()
        except sqlite3.Error as e:
            print("Couldn't gracefully close db: %s" % e, file=STDERR)

    def query(self, qq: str):
        try:
            self.cursor.execute(qq)
            self.lastrow = self.cursor.fetchall()
        except sqlite3.Error as e:
            print("Couldn't execute query %s, exception: %s" % (qq, e), file=STDERR)
            self.lastrow = []
        return self.lastrow

    # sometimes we need the cursor for safety reasons, for example does sqlite3 all the security related
    # escaoing in supplied strings for us, when we deliver it to con.execute in the second argument as a tuple
    def getCursor(self):
        return self.cursor

    # we could try to utilise that ourselfs in a function. Be c a r e f u l, these values in the tuple MUST HAVE
    # THE RIGHT TYPE
    def safequery(self, qq: str, deliver: tuple):
        try:
            self.cursor.execute(qq, deliver)
            self.lastrow = self.cursor.fetchall()
        except sqlite3.Error as e:
            print("Couldn't execute query %s, exception: %s" % (qq, e), file=STDERR)
            self.lastrow = []
        except TypeError as e:
            print("Types in given tuple doesnt match to execute query \"%s\": %s" % (qq, e), file=STDERR)
            self.lastrow = []
        return self.lastrow


if __name__ == "__main__":
    try:
        SQLitedb("bla.db")
        print("hi")
        exit(0)
    except KeyboardInterrupt:
        pass
