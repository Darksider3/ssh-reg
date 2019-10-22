#!/usr/bin/env python3

from lib.sqlitedb import SQLitedb
import configparser
import lib.uis.default as default_cmd  # Follows -u, -a, -f flags


class ListUsers:
    db = None
    usersFetch = None

    def __init__(self, db: str, unapproved: bool = False, approved: bool = True):
        self.db = SQLitedb(db)
        if unapproved:  # only unapproved users
            query = "SELECT * FROM `applications` WHERE `status` = '0'"
        elif approved:  # Approved users
            query = "SELECT * FROM `applications` WHERE `status` = '1'"
        else:  # All users
            query = "SELECT * FROM `applications`"
        self.usersFetch = self.db.query(query)

    def output_as_list(self) -> str:
        list_str: str = ""
        query = "SELECT `username` FROM `applications` WHERE `status` = '1' ORDER BY timestamp ASC"
        self.usersFetch = self.db.query(query)
        for users in self.usersFetch:
            list_str += users["username"]+"\n"
        return list_str

    def prettyPrint(self) -> None:
        pass  # see below why not implemented yet, texttable...

    def getFetch(self) -> list:
        """ Returns a complete fetch done by the sqlitedb-class

        :return: Complete fetchall() in a dict-factory
        :rtype: list
        """
        return self.usersFetch


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
            ))
"""
if __name__ == "__main__":
    default_cmd.argparser.description += " - Lists Users from the Tilde database."
    default_cmd.argparser.add_argument('--list', default=False, action="store_true",
                                       help='Output a newline seperated list of users', required=False)
    args = default_cmd.argparser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)

    try:
        ret = ""
        L = ListUsers(config['DEFAULT']['applications_db'], unapproved=args.unapproved, approved=args.approved)
        if args.list:
            ret = L.output_as_list()
        else:
            fetch = L.getFetch()
            ret += "ID %-1s| Username %-5s| Mail %-20s| Name %-17s| Registered %-8s | State |\n" % (
                " ", " ", " ", " ", " "
            )
            ret += 102 * "-" + "\n"
            for user in fetch:
                ret += "%-4i| %-14s| %-25s| %-22s| %-8s | %-5i |\n" % (
                    user["id"], user["username"], user["email"], user["name"], user["timestamp"], user["status"]
                )
        if args.file != "stdout":
            with open(args.file, 'w') as f:
                print(ret, file=f)
        else:
            print(ret)
        exit(0)
    except KeyboardInterrupt:
        pass
