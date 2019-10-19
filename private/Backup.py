#!/usr/bin/env python3

import ListUsers
import csv
import io
import configparser
import lib.uis.default as default_cmd  # Follows -u, -a, -f flags


default_cmd.argparser.description += " - Backups Tilde Users to stdout or a file."
args = default_cmd.argparser.parse_args()
config = configparser.ConfigParser()
config.read(args.config)


class Backup:
    filename: str
    quoting: int
    dialect: str
    field_names: tuple

    def __init__(self, fname: str, quoting: int = csv.QUOTE_NONNUMERIC, dialect: str = "excel"):
        self.setFilename(fname)
        self.setQuoting(quoting)
        self.setDialect(dialect)
        self.setFieldnames(tuple(['id', 'username', 'email', 'name', 'pubkey', 'timestamp', 'status']))

    def setDialect(self, dialect: str):
        self.dialect = dialect

    def setQuoting(self, quoting: int):
        self.quoting = quoting

    def setFilename(self, filename: str):
        self.filename = filename

    def setFieldnames(self, f_names: tuple):
        self.field_names = f_names

    def BackupToFile(self, fetched: list):
        returner = io.StringIO()
        write_csv = csv.DictWriter(returner, fieldnames=self.field_names, quoting=self.quoting, dialect=self.dialect)
        write_csv.writeheader()
        write_csv.writerows(fetched)

        if self.filename == "stdout":
            print(returner.getvalue())
        else:
            with open(self.filename, "w") as f:
                print(returner.getvalue(), file=f)
            return True


if __name__ == "__main__":
    try:
        L = ListUsers.ListUsers(config['DEFAULT']['applications_db'], uap=args.unapproved, app=args.approved)
        fetch = L.getFetch()
        B = Backup(args.file)
        B.BackupToFile(fetch)
        exit(0)
    except KeyboardInterrupt as e:
        pass
