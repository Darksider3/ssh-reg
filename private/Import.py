import lib.CFG as CFG
import csv
import os
import lib.UserExceptions


def ImportFromFile(fname: str = CFG.args.file, db: str = CFG.config['DEFAULT']['applications_db'],
                   userids: tuple = tuple([])):
    if not os.path.isfile(fname):
        print(f"File {fname} don't exist")
        return None
    if not os.path.isfile(db):
        print(f"The database file {db} don't exist")
        return None
    if userids:
        pass  # empty tuple means everything
    # noinspection PyBroadException
    try:
        with open(fname, 'r', newline='') as f:
            import lib.validator
            err = lib.validator.checkImportFile(f)
            if err is not True:
                print(err)
                exit(0)
            import lib.sqlitedb
            import lib.System
            sysctl = lib.System.System()
            sql = lib.sqlitedb.SQLitedb(CFG.config['DEFAULT']['applications_db'])
            reader = csv.DictReader(f)  # @TODO csv.Sniffer to compare? When yes, give force-accept option
            for row in reader:
                if row["status"] == "1":
                    try:
                        sysctl.register(row["username"])
                        sysctl.lock_user_pw(row["username"])
                        sysctl.add_to_usergroup(row["username"])
                        sysctl.make_ssh_usable(row["username"], row["pubkey"])
                        print(row['username'], "====> Registered.")
                    except lib.UserExceptions.UserExistsAlready as UEA:
                        pass  # @TODO User was determined to exists already, shouldn't happen but is possible
                    except lib.UserExceptions.UnknownReturnCode as URC:
                        pass  # @TODO Unknown Return Codes. Can happen in various function
                    except lib.UserExceptions.SSHDirUncreatable as SDU:
                        pass  # @TODO SSH Directory doesn't exist AND couldn't be created. Inherently wrong design!
                    except lib.UserExceptions.ModifyFilesystem as MFS:
                        pass  # @TODO Same as SSH Dir but more general, same problem: Wrong Permissions,
                        # Missing Dirs etc
                    except Exception as E:  # @TODO well less broad is hard to achieve Kappa
                        print(E)
                        continue
                elif row["status"] == "0":
                    print(row['username'] + " not approved, therefore not registered.")
                try:
                    sql.safequery(
                        "INSERT INTO `applications` (username, name, timestamp, email, pubkey, status) "
                        "VALUES (?,?,?,?,?,?)", tuple([row["username"], row["name"], row["timestamp"],
                                                       row["email"], row["pubkey"], row["status"]]))
                except OSError as E:
                    pass
                    print(f"UUFFF, something went WRONG with the file {fname}: {E}")
    except Exception as didntCatch:
        print(f"Exception! UNCATCHED! {type(didntCatch)}: {didntCatch}")
    return True


if __name__ == "__main__":
    try:
        if not CFG.args.Import:
            print("Error, need the import flag")
        if not CFG.args.file:
            print("Error, need the import file")
            if not CFG.args.file:
                print("You MUST set a CSV-file with the -f/--file flag that already exist")
                exit(1)
        ImportFromFile()
        exit(0)
    except KeyboardInterrupt as e:
        pass
