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
    last_result = None

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
            self.connection.commit()
            self.connection.close()
        except sqlite3.Error as e:
            print("Couldn't gracefully close db: %s" % e, file=STDERR)

    def query(self, qq: str) -> list:
        try:
            self.cursor.execute(qq)
            self.last_result = self.cursor.fetchall()
        except sqlite3.Error as e:
            print("Couldn't execute query %s, exception: %s" % (qq, e), file=STDERR)
            self.last_result = []
        return self.last_result

    # sometimes we need the cursor for safety reasons, for example does sqlite3 all the security related
    # escaoing in supplied strings for us, when we deliver it to con.execute in the second argument as a tuple
    def getCursor(self) -> sqlite3:
        return self.cursor

    # we could try to utilise that ourselfs in a function. Be c a r e f u l, these values in the tuple MUST HAVE
    # THE RIGHT TYPE
    def safequery(self, qq: str, deliver: tuple) -> list:
        try:
            self.cursor.execute(qq, deliver)
            self.last_result = self.cursor.fetchall()
        except sqlite3.Error as e:
            print("Couldn't execute query %s, exception: %s" % (qq, e), file=STDERR)
            self.last_result = []
        except TypeError as e:
            print("Types in given tuple doesnt match to execute query \"%s\": %s" % (qq, e), file=STDERR)
            self.last_result = []
        return self.last_result

    def removeApplicantFromDB(self, userid: int) -> bool:
        try:
            self.last_result = self.cursor.execute("DELETE FROM `applications` WHERE id = ? ", [userid])
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Could not delete user with id: {userid}, exception in DB: {e}")  # @TODO LOGGING FFS
            return False
        return True

    def removeApplicantFromDBperUsername(self, username: str) -> bool:
        try:
            self.last_result = self.cursor.execute("DELETE FROM `applications` WHERE username = ?", [username])
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Could not delete user {username}, exception in DB: {e}")  # @TODO LOGGING
            return False
        return True


if __name__ == "__main__":
    try:
        SQLitedb("bla.db")
        print("hi")
        exit(0)
    except KeyboardInterrupt:
        pass
