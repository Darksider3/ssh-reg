import lib.CFG as CFG
import csv
import os
import lib.UserExceptions
import lib.validator


def ImportFromFile(fname: str = CFG.args.file, db: str = CFG.REG_FILE, userids: tuple = tuple([])):
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
            import lib.sqlitedb
            import lib.System
            sysctl = lib.System.System()
            sql = lib.sqlitedb.SQLitedb(CFG.REG_FILE)
            reader = csv.DictReader(f)  # @TODO csv.Sniffer to compare? When yes, give force-accept option
            for row in reader:
                # if any of this fails move on to the next user, just print a relatively helpful message lel
                if not lib.validator.checkUsernameCharacters(row["username"]):
                    print(f"The username contains unsupported characters or starts with a number: "
                          f"{row['username']}")
                    continue
                if not lib.validator.checkUsernameLength(row["username"]):
                    print(f"The username {row['username']} is either too long(>16) or short(<3).")
                    continue
                if not lib.validator.checkSSHKey(row["pubkey"]):
                    print(f"Following SSH-Key isn't valid: {row['pubkey']}")
                    continue
                if not lib.validator.checkEmail(row["email"]):
                    print(f"The E-Mail address {row['email']} is not valid.")
                    continue
                if lib.validator.checkUserExists(row["username"]):
                    print(f"The user '{row['username']}' already exists.")
                    continue
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
        print(f"Exception! UNCATCHED! {type(didntCatch)}")
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
        exit(0)
    except KeyboardInterrupt as e:
        pass
