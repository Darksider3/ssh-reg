#!/usr/bin/env python3
import sqlite3
from sys import stderr as stderr


# create dictionary out of sqlite results
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLiteDB:
    """SQLitedb handles EVERYTHING directly related to our Database."""

    db = ""
    cursor = None
    connection = None
    last_result = None

    def __init__(self, dbpath: str):
        """
        :param dbpath: Path to the database we want to open
        :type dbpath: str
        :returns: Object for the SQLitedb-Class.
        :rtype: object
        """

        db = dbpath
        try:
            self.connection = sqlite3.connect(db)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print("Connection error: %s" % e, file=stderr)

        self.cursor.row_factory = dict_factory  # every result will be a dict now

    def __del__(self):
        try:
            self.connection.commit()
            self.connection.close()
        except sqlite3.Error as e:
            print("Couldn't gracefully close db: %s" % e, file=stderr)

    def query(self, qq: str) -> list:
        """Do a query and automagically get the fetched results in a list
        :param qq: Query to execute
        :type qq: str
        :returns: A tuple(/list) consisting with any fetched results
        :rtype: list
        """

        try:
            self.cursor.execute(qq)
            self.last_result = self.cursor.fetchall()
            self.connection.commit()
        except sqlite3.OperationalError:
            self._createTable()
            return self.query(qq)
        except sqlite3.Error as e:
            print("Couldn't execute query %s, exception: %s" % (qq, e), file=stderr)
            self.last_result = []
        return self.last_result

    # sometimes we need the cursor for safety reasons, for example does sqlite3 all the security related
    # escaoing in supplied strings for us, when we deliver it to con.execute in the second argument as a tuple
    def getCursor(self) -> sqlite3:
        """Returns SQLite3 Cursor. Use with **c a u t i o n**... """
        return self.cursor

    # we could try to utilise that ourselfs in a function. Be c a r e f u l, these values in the tuple MUST HAVE
    # THE RIGHT TYPE
    def safequery(self, qq: str, deliver: tuple) -> list:
        """ Shall handle any query that has user input in it as an alternative to self.query
        :param qq: Query to execute
        :type qq: str
        :param deliver: User inputs marked with the placeholder(`?`) in the str
        :type deliver: tuple
        :returns: A tuple(/list) consisting with any fetched results
        :rtype: list
        """

        try:
            self.cursor.execute(qq, deliver)
            self.last_result = self.cursor.fetchall()
            self.connection.commit()
        except TypeError as e:
            print("Types in given tuple doesnt match to execute query \"%s\": %s" % (qq, e), file=stderr)
            self.last_result = []
        except sqlite3.OperationalError as e:
            self._createTable()
            return self.safequery(qq, deliver)
        except sqlite3.Error as e:
            print("Couldn't execute query %s, exception: %s" % (qq, e), file=stderr)
            print(deliver)
            print(type(e))
            self.last_result = []
        return self.last_result

    def removeApplicantFromDB(self, userid: int) -> bool:
        """Removes Applicants from the DB by ID. Use along System.removeUser()
        :param userid: User ID to remove from the Database
        :type userid: int
        :returns: True, if removal was successful(from the DB), False when not
        :rtype: bool
        """

        try:
            self.last_result = self.cursor.execute("DELETE FROM `applications` WHERE id = ? ", [userid])
            self.connection.commit()
        except sqlite3.OperationalError:
            print("The database has probably not yet seen any users, so it didnt create your table yet. Come back"
                  "when a user tried to register")
            return False
        except sqlite3.Error as e:
            print(f"Could not delete user with id: {userid}, exception in DB: {e}")  # @TODO LOGGING FFS
            return False
        return True

    def removeApplicantFromDBperUsername(self, username: str) -> bool:
        """Removes Applicants from the DB by Username. Use along System.removeUser()
        :param username: Username to remove from the database
        :type username: str
        :returns: True, if removal was successful(from the DB), False when not
        :rtype: bool
        """

        try:
            self.last_result = self.cursor.execute("DELETE FROM `applications` WHERE username = ?", [username])
            self.connection.commit()
        except sqlite3.OperationalError:
            print("The database has probably not yet seen any users, so it didnt create your table yet. Come back"
                  "when a user tried to register")
            return False
        except sqlite3.Error as e:
            print(f"Could not delete user {username}, exception in DB: {e}")  # @TODO LOGGING
            return False
        return True

    def _createTable(self):
        try:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS applications("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "username TEXT NOT NULL, email TEXT NOT NULL,"
                "name TEXT NOT NULL, pubkey TEXT NOT NULL,"
                "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP CONSTRAINT "
                "timestamp_valid CHECK( timestamp IS strftime('%Y-%m-%d %H:%M:%S', timestamp))"
                ",status INTEGER NOT NULL DEFAULT 0);")
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"The database probably doesn't exist yet, but read the message: {e}")
        print("The database table didn't exist yet; created it successfully!")


if __name__ == "__main__":
    try:
        SQLiteDB("bla.db")
        print("hi")
        exit(0)
    except KeyboardInterrupt:
        pass
