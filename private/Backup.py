#!/usr/bin/env python3

import ListUsers
import csv
import io
import configparser
import lib.uis.default as default_cmd  # Follows -u, -a, -f flags


class Backup:
    """Backups a Tilde database to an CSV file

    :Example:
    >>> from Backup import Backup
    >>> from ListUsers import ListUsers
    >>> L = ListUsers.ListUsers("/path/to/sqlite").get_fetch()
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

        self.setFilename(output)
        self.setQuoting(quoting)
        self.setDialect(dialect)
        self.setFieldnames(tuple(['id', 'username', 'email', 'name', 'pubkey', 'timestamp', 'status']))

    def setDialect(self, dialect: str) -> None:
        """ Set dialect for Object

        :param dialect: Dialect to set for Object
        :type dialect: str
        :return: None
        :rtype: None
        """

        self.dialect = dialect

    def setQuoting(self, quoting: int) -> None:
        """ Set quoting in the CSV(must be supported by the CSV Module!)

        :param quoting: Quoting Integer given by csv.QUOTE_* constants
        :type quoting: int
        :return: None
        :rtype: None
        """

        self.quoting = quoting

    def setFilename(self, filename: str) -> None:
        """ Sets Filename to output to

        :param filename: Filename to output to(set stdout for stdout)
        :type filename: str
        :return: None
        :rtype: None
        """

        self.filename = filename

    def setFieldnames(self, f_names: tuple) -> None:
        """ Set fieldname to process

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
        write_csv = csv.DictWriter(returner, fieldnames=self.field_names, quoting=self.quoting, dialect=self.dialect)
        write_csv.writeheader()
        for row in fetched:
            write_csv.writerow(dict(row))
            # sqlite3.Row doesn't "easily" convert to a dict itself sadly, so just a quick help from us here
            # it actually even delivers a list(sqlite3.Row) also, which doesnt make the life a whole lot easier

        if self.filename == "stdout":
            print(returner.getvalue())
            return True
        else:
            with open(self.filename, "w") as f:
                print(returner.getvalue(), file=f)
            return True


if __name__ == "__main__":
    default_cmd.argparser.description += " - Backups Tilde Users to stdout or a file."
    args = default_cmd.argparser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    try:
        L = ListUsers.ListUsers(config['DEFAULT']['applications_db'],
                                unapproved=args.unapproved, approved=args.approved)
        fetch = L.get_fetch()
        if fetch:
            B = Backup(args.file)
            B.setFieldnames(fetch[0].keys())  # sqlite3.row delivers its keys for us! SO NICE!
            B.backup_to_file(fetch)
        else:
            print("nothing to backup!")
            exit(1)
        exit(0)
    except KeyboardInterrupt as e:
        pass
