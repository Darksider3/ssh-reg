#!/usr/bin/env python3
"""
SQLite wrapper which does just some simple wraps, to ease our experience a little.
"""

import sqlite3
from sys import stderr as stderr
from typing import List  # Typing support!


# create dictionary out of sqlite results
def dict_factory(cursor, row):
    d: dict = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLiteDB:
    """SQLitedb handles EVERYTHING directly related to our Database."""

    db = ""
    cursor = None
    connection = None
    last_result = None

    def __init__(self, db_path: str):
        """
        :param db_path: Path to the database we want to open
        :type db_path: str
        :returns: Object for the SQLitedb-Class.
        :rtype: object
        """
        try:
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as sql_con:
            print("Connection error: %s" % sql_con, file=stderr)

        self.cursor.row_factory = sqlite3.Row  # every result will be a dict now

    def __del__(self):
        try:
            self.connection.commit()
            self.connection.close()
        except sqlite3.Error as e:
            print("Couldn't gracefully close db: %s" % e, file=stderr)

    def query(self, q_str: str) -> List[sqlite3.Row]:
        """Do a query and automagically get the fetched results in a list
        :param q_str: Query to execute
        :type q_str: str
        :returns: A tuple(/list) consisting with any fetched results
        :rtype: list
        """

        try:
            self.cursor.execute(q_str)
            self.last_result = self.cursor.fetchall()
            self.connection.commit()
        except sqlite3.OperationalError:
            self._createTable()
            return self.query(q_str)
        except sqlite3.Error as sql_query_except:
            print("Couldn't execute query %s, exception: %s" % (q_str, sql_query_except),
                  file=stderr)
            self.last_result = []
        return self.last_result

    # sometimes we need the cursor for safety reasons, for example does sqlite3 all the security related
    # escaoing in supplied strings for us, when we deliver it to con.execute in the second argument as a tuple
    def get_cursor(self) -> sqlite3:
        """Returns SQLite3 Cursor. Use with **c a u t i o n**... """
        return self.cursor

    # we could try to utilise that ourselfs in a function. Be c a r e f u l, these values in the tuple MUST HAVE
    # THE RIGHT TYPE
    def safe_query(self, q_str: str, deliver: tuple) -> List[sqlite3.Row]:
        """ Shall handle any query that has user input in it as an alternative to self.query
        :param q_str: Query to execute
        :type q_str: str
        :param deliver: User inputs marked with the placeholder(`?`) in the str
        :type deliver: tuple
        :returns: A tuple(/list) consisting with any fetched results
        :rtype: List[sqlite3.Row]
        """

        try:
            self.cursor.execute(q_str, deliver)
            self.last_result = self.cursor.fetchall()
            self.connection.commit()
        except TypeError as type_err:
            print("Types in given tuple doesnt match to execute query \"%s\": %s" % (q_str, type_err), file=stderr)
            self.last_result = []
        except sqlite3.OperationalError:
            self._createTable()
            return self.safe_query(q_str, deliver)
        except sqlite3.Error as sql_query_error:
            print("Couldn't execute query %s, exception: %s" % (q_str, sql_query_error), file=stderr)
            print(deliver)
            print(type(sql_query_error))
            self.last_result = []
        return self.last_result

    def removeApplicantFromDB(self, user_id: int) -> bool:
        """Removes Applicants from the DB by ID. Use along System.removeUser()
        :param user_id: User ID to remove from the Database
        :type user_id: int
        :returns: True, if removal was successful(from the DB), False when not
        :rtype: bool
        """

        try:
            self.last_result = self.cursor.execute("DELETE FROM `applications` WHERE id = ? ",
                                                   [user_id])
            self.connection.commit()
        except sqlite3.OperationalError:
            print("The database has probably not yet seen any users, so it didnt create your table yet. Come back"
                  "when a user tried to register")
            return False
        except sqlite3.Error as query_error:
            print(f"Could not delete user with id: {user_id}, exception in DB: {query_error}")  # @TODO LOGGING FFS
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
        except sqlite3.Error as sql_error:
            print(f"Could not delete user {username}, exception in DB: {sql_error}")  # @TODO LOGGING
            return False
        return True

    def _createTable(self) -> None:
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
        except sqlite3.Error as sql_error:
            print(f"The database probably doesn't exist yet, but read the message: {sql_error}")
        print("The database table didn't exist yet; created it successfully!")


if __name__ == "__main__":
    try:
        SQLiteDB("bla.db")
        print("hi")
        exit(0)
    except KeyboardInterrupt:
        pass
