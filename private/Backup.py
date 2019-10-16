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

    @staticmethod
    def ImportFromFile(fname: str = CFG.args.file, db: str = CFG.REG_FILE, userids: tuple = tuple([])):
        if not os.path.isfile(fname):
            return None  # @TODO maybe some better output here
        if not os.path.isfile(db):
            return None  # @TODO maybe some better output here
        if userids:
            pass  # empty tuple means everything
        # noinspection PyBroadException
        try:
            with open(fname, 'r', newline='') as f:
                import lib.sqlitedb
                import lib.System
                sysctl = lib.System.System()
                sql = lib.sqlitedb.SQLitedb(CFG.REG_FILE)
                reader = csv.DictReader(f)  # @TODO csv.Sniffer to compare? When yes, give force-accept option
                for row in reader:
                    # if any of this fails move on to the next user, just print a relatively helpful message lel
                    if not lib.validator.checkUsernameLength(row["username"]):
                        print(f"The username {row['username']} is either too long(>16) or short(<3).")
                        continue
                    if not lib.validator.checkUsernameCharacters(row["username"]):
                        print(f"The username contains unsupported characters or starts with a number: "
                              f"{row['username']}")
                        continue
                    if not lib.validator.checkSSHKey(row["pubkey"]):
                        print(f"Following SSH-Key isn't valid: {row['pubkey']}")
                        continue
                    if lib.validator.checkUserExists(row["username"]):
                        print(f"The user '{row['username']}' already exists.")
                        continue
                    if not lib.validator.checkEmail(row["email"]):
                        print(f"The E-Mail address {row['email']} is not valid.")
                        continue
                    if row["status"] == "1":
                        try:
                            sysctl.register(row["username"])  # @TODO exception lib.UserExceptions.UserExistsAlready
                            sysctl.lock_user_pw(row["username"])  # @TODO exception lib.UserExceptions.UnknownReturnCode
                            sysctl.add_to_usergroup(row["username"])  # @TODO exception lib.UnknownReturnCode
                            sysctl.make_ssh_usable(row["username"], row["pubkey"])  # @TODO exception
                            print(row['username'], "====> Registered.")
                        except Exception as e:
                            print(e)
                            continue
                    elif row["status"] == "0":
                        print(row['username'] + "not approved, therefore not registered.")
                    try:
                        sql.safequery(
                            "INSERT INTO `applications` (username, name, timestamp, email, pubkey, status) "
                            "VALUES (?,?,?,?,?,?)", tuple([row["username"], row["name"], row["timestamp"],
                                                           row["email"], row["pubkey"], row["status"]]))
                    except OSError as E:
                        pass
                        print(f"UUFFF, something went WRONG with the file {fname}: {E}")
        except Exception as e:
            print(f"Exception! UNCATCHED! {type(e)}")
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
