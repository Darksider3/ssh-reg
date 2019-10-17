#!/usr/bin/env python3

import ListUsers
import csv
import io
import lib.CFG as CFG
import lib.validator
import lib.UserExceptions
import os


class Backup:
    filename: str
    quoting: int
    dialect: str
    field_names: tuple

    def __init__(self, fname: str = CFG.args.file, quoting: int = csv.QUOTE_NONNUMERIC, dialect: str = "excel"):
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
        L = ListUsers.ListUsers()
        fetch = L.getFetch()
        B = Backup()
        if CFG.args.Import:
            print("For importing please call the ./Import.py file with the --Import flag")
        else:
            B.BackupToFile(fetch)
        exit(0)
    except KeyboardInterrupt as e:
        pass
