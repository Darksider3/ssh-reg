#!/usr/bin/env python3

import ListUsers
import csv
import io
import lib.CFG as CFG
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

    @staticmethod
    def ImportFromFile(fname: str = CFG.args.file, db: str = CFG.REG_FILE, userids: tuple = tuple([])):
        if not os.path.isfile(fname):
            return None  # @TODO maybe some better output here
        if not os.path.isfile(db):
            return None  # @TODO maybe some better output here
        if userids:
            pass  # empty tuple means everything
        try:
            with open(fname, 'r', newline='') as f:
                import lib.sqlitedb
                import lib.System
                sysctl = lib.System.System()
                sql = lib.sqlitedb.SQLitedb(CFG.REG_FILE)
                reader = csv.DictReader(f)  # @TODO csv.Sniffer to compare? When yes, give force-accept option
                for row in reader:
                    if row["status"] == "1":
                        sysctl.register(row["username"])
                        sysctl.lock_user_pw(row["username"])
                        sysctl.add_to_usergroup(row["username"])
                        sysctl.make_ssh_usable(row["username"], row["pubkey"])
                        print(row['id'], row['username'], row['email'], row['name'], row['pubkey'], row['timestamp'],
                              row['status'] + "====> Registered.")
                    elif row["status"] == "0":
                        print(row['id'], row['username'], row['email'], row['name'], row['pubkey'], row['timestamp'],
                              row['status'] + "not approved, therefore not registered.")
                    else:
                        print(f"Uhm, ok. Type is {type(row['status'])}, and value is {row['status']}")
                    sql.safequery("INSERT INTO `applications` (username, name, timestamp, email, pubkey, status) "
                                  "VALUES (?,?,?,?,?,?)",
                                  tuple([row["username"], row["name"], row["timestamp"],
                                         row["email"], row["pubkey"], row["status"]]))  # @TODO: without IDs
                    pass  # @TODO: Import with sqlitedb and system. Will be fun Kappa
        except OSError as E:
            print(f"UUFFF, something went WRONG with the file {fname}: {E}")
        return True


if __name__ == "__main__":
    try:
        L = ListUsers.ListUsers()
        fetch = L.getFetch()
        B = Backup()
        if CFG.args.Import:
            if not CFG.args.file:
                print("You MUST set a CSV-file with the -f/--file flag that already exist")
                exit(1)
            if not B.ImportFromFile(CFG.args.file):
                print("Backup didn't work because the file doesnt exist")
        else:
            B.BackupToFile(fetch)
        exit(0)
    except KeyboardInterrupt as e:
        pass
