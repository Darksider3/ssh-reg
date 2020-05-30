#!/usr/bin/env python3
""" This module is thought to be the main point to export and import users.
It's actually not really a module but a script ought to be run from the command line

@TODO: Wording of module header...
"""

import configparser
import csv
import io

from lib.ListUsers import ListUsers
import lib.uis.default as default_cmd  # Follows -u, -a, -f flags


class Backup:
    """Backups a Tilde database to an CSV file
    @TODO: Move class into own file

    :Example:
    >>> from backup import Backup
    >>> from ListUsers import ListUsers
    >>> L = ListUsers.list_users("/path/to/sqlite").get_fetch()
    >>> backup_db = Backup("stdout")
    >>> backup_db.backup_to_file(L)
    CSV-Separated list with headers in first row

    """

    filename: str
    quoting: int
    dialect: str
    field_names: tuple

    def __init__(self, output: str, quoting: int = csv.QUOTE_NONNUMERIC, dialect: str = "excel"):
        """ Constructs the Backup object

        :param output: File name to backup to(set to stdout for stdout)
        :type output: str
        :param quoting: Set quoting for CSV Module
        :type quoting: int
        :param dialect: Set the CSV-Dialect. Defaults to excel, which is the classic CSV
        :type dialect: str
        """

        self.set_filename(output)
        self.set_quoting(quoting)
        self.set_dialect(dialect)
        self.set_field_names(tuple(['id', 'username', 'email', 'name',
                                    'pubkey', 'timestamp', 'status']))

    def set_dialect(self, dialect: str) -> None:
        """ Set dialect for Object

        :param dialect: Dialect to set for Object
        :type dialect: str
        :return: None
        :rtype: None
        """

        self.dialect = dialect

    def set_quoting(self, quoting: int) -> None:
        """ Set quoting in the CSV(must be supported by the CSV Module!)

        :param quoting: Quoting Integer given by csv.QUOTE_* constants
        :type quoting: int
        :return: None
        :rtype: None
        """

        self.quoting = quoting

    def set_filename(self, filename: str) -> None:
        """ Sets Filename to OUTPUT to

        :param filename: Filename to OUTPUT to(set stdout for stdout)
        :type filename: str
        :return: None
        :rtype: None
        """

        self.filename = filename

    def set_field_names(self, f_names: tuple) -> None:
        """ Set field name to process

        :param f_names: Fieldnames-Tuple
        :type f_names: tuple
        :return: None
        :rtype: None
        """

        self.field_names = f_names

    def backup_to_file(self, fetched: list) -> bool:
        """Backup Userlist to File(or stdout)

        :param fetched: List of values to write out CSV-formatted
        :return: True, if success, None when not.
        :rtype: bool
        """

        returner = io.StringIO()
        write_csv = csv.DictWriter(returner, fieldnames=self.field_names,
                                   quoting=self.quoting, dialect=self.dialect)
        write_csv.writeheader()
        for row in fetched:
            write_csv.writerow(dict(row))
            # sqlite3.Row doesn't "easily" convert to a dict itself sadly,
            # so just a quick help from us here
            # it actually even delivers a list(sqlite3.Row) also,
            # which doesnt make the life a whole lot easier

        if self.filename == "stdout":
            print(returner.getvalue())
        else:
            with open(self.filename, "w") as f:
                print(returner.getvalue(), file=f)
        return True


if __name__ == "__main__":
    default_cmd.argparser.description += " - Backups Tilde Users to stdout or a file."
    args = default_cmd.argparser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    L = ListUsers(config['DEFAULT']['applications_db'],
                  unapproved=args.unapproved, approved=args.approved)
    fetch = L.get_fetch()
    if fetch:
        B = Backup(args.file)
        B.set_field_names(fetch[0].keys())  # sqlite3.row delivers its keys for us! SO NICE!
        B.backup_to_file(fetch)
    else:
        print("nothing to backup!")
        exit(1)
    exit(0)
