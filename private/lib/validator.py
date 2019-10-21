import re
import pwd
import lib.sqlitedb


def checkUsernameCharacters(username: str) -> bool:
    if " " not in username and "_" not in username and username.isascii() and username[:1].islower() and \
            not username[0].isnumeric():
        if not re.search(r"\W+", username):
            if not re.search("[^a-zA-Z0-9]", username):
                return True
    return False


def checkUsernameLength(username: str) -> bool:
    if len(username) > 16:
        return False
    if len(username) < 3:
        return False
    return True


def checkUserExists(username: str) -> bool:
    try:
        pwd.getpwnam(username)
    except KeyError:
        return True  # User already exists
    else:
        return False


def checkUserInDB(username: str, db: str) -> bool:
    try:
        ldb = lib.sqlitedb.SQLitedb(db)
        fetched = ldb.safequery("SELECT * FROM 'applications' WHERE username = ?", tuple([username]))
        if fetched:
            return True
    except lib.sqlitedb.sqlite3.Error as e:
        print(f"SQLite Exception: {e}")
    return False


def checkSSHKey(key: str) -> bool:
    # taken from https://github.com/hashbang/provisor/blob/master/provisor/utils.py, all belongs to them! ;)
    import base64
    if len(key) > 8192 or len(key) < 80:
        return False

    key = key.replace("\"", "").replace("'", "").replace("\\\"", "")
    key = key.split(' ')
    types = ['ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384',
             'ecdsa-sha2-nistp521', 'ssh-rsa', 'ssh-dss', 'ssh-ed25519']
    if key[0] not in types:
        return False
    try:
        base64.decodebytes(bytes(key[1], "utf-8"))
    except TypeError:
        return False
    return True


def checkEmail(mail: str) -> bool:
    if not re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", mail):
        return False
    else:
        return True


def checkDatetimeFormat(form: str) -> bool :
    import datetime
    try:
        datetime.datetime.strptime(form, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False
    return True


def checkName(name: str) -> bool:
    if not re.match("\w+\s*\w", name):
        return False
    else:
        return True


def checkImportFile(fname: str, db: str) -> bool:
    error_list = str()
    valid = True
    ln = 1  # line number
    with open(fname, 'r', newline='') as f:
        import csv
        reador = csv.DictReader(f)
        for row in reador:
            # if any of this fails move on to the next user, just print a relatively helpful message lel
            if not lib.validator.checkName(row["name"]):
                error_list += f"Line{ln}: {row['name']} seems not legit. Character followed by character should be " \
                              f"correct.\n"
                valid = False
            if not lib.validator.checkUsernameCharacters(row["username"]):
                error_list += (f"Line {ln}: Username contains unsupported characters or starts with a number: '"
                               f"{row['username']}'.\n")
                valid = False
            if not lib.validator.checkUsernameLength(row["username"]):
                error_list += f"Line {ln}: Username '{row['username']}' is either too long(>16) or short(<3)\n"
                valid = False
            if not lib.validator.checkSSHKey(row["pubkey"]):
                error_list += f"Line {ln}: Following SSH-Key of user '{row['username']}' isn't valid: '{row['pubkey']}'."\
                              f"\n"
                valid = False
            if not lib.validator.checkEmail(row["email"]):
                error_list += f"Line {ln}: E-Mail address of user '{row['username']}' '{row['email']}' is not valid.\n"
                valid = False
            if not lib.validator.checkUserExists(row["username"]) or checkUserInDB(row["username"], db):
                error_list += f"Line {ln}: User '{row['username']}' already exists.\n"
                valid = False
            if not lib.validator.checkDatetimeFormat(row["timestamp"]):
                error_list += f"Line {ln}: Timestamp '{row['timestamp']}' from user '{row['username']}' is invalid.\n"
                valid = False
            if int(row["status"]) > 1 or int(row["status"]) < 0:
                error_list += f"Line {ln}: Status '{row['status']}' MUST be either 0 or 1.\n"
                valid = False
            ln += 1
    if valid:
        return True
    else:
        return error_list
