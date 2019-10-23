import re
import pwd
import lib.sqlitedb
import csv


def checkUsernameCharacters(username: str) -> bool:
    """ Checks the Username for invalid characters. Allow only alphanumerical characters, a lower alpha one first,
    Followed by any sequence of digits and characters

    :param username: String to check for validity
    :type username: str
    :return: True when valid, False when not
    :rtype: bool
    """

    if " " not in username and "_" not in username and username.isascii() and username[:1].islower() and \
            not username[0].isnumeric():
        if not re.search(r"\W+", username):
            if not re.search("[^a-zA-Z0-9]", username):
                return True
    return False


def checkUsernameLength(username: str, upper_limit: int = 16, lower_limit: int = 3) -> bool:
    """ Checks username for an upper and lower bounds limit character count

    :param username: Username to check
    :type username: str
    :param upper_limit: Upper limit bounds to check for(default is 16)
    :type upper_limit: int
    :param lower_limit: Lower limit bounds to check for(default is 3)
    :return: True, when all bounds are in, False when one or both aren't.
    :rtype: bool
    """

    if len(username) > upper_limit:
        return False
    if len(username) < lower_limit:
        return False
    return True


def checkUserExists(username: str) -> bool:
    """ Checks if the User exists on the **SYSTEM** by calling PWD on it.
    **Note**: You might want to use this in conjunction with checkUserInDB

    :param username:
    :type username: str
    :return: True when exists, False when not
    :rtype: bool
    """

    try:
        pwd.getpwnam(username)
    except KeyError:
        return True  # User already exists
    else:
        return False


def checkUserInDB(username: str, db: str) -> bool:
    """ Checks users existence in the **DATABASE**.
    :Note: You might want to use this in conjunction with `checkUserExists`

    :param username: Username to check existence in database
    :type username: str
    :param db: Path to database to check in
    :type db: str
    :return: True, when User exists, False when not
    """

    try:
        ldb = lib.sqlitedb.SQLiteDB(db)
        fetched = ldb.safequery("SELECT * FROM 'applications' WHERE username = ?", tuple([username]))
        if fetched:
            return True
    except lib.sqlitedb.sqlite3.Error as e:
        print(f"SQLite Exception: {e}")
    return False


def checkSSHKey(key: str) -> bool:
    """ Checks SSH Key for meta-data that we accept.
    :Note: We currently only allow ssh keys without options but with a mail address at the end in b64 encoded.
    The currently supported algorithms are: ecdfsa-sha2-nistp256, 'ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp521',
    'ssh-rsa', 'ssh-dss' and 'ssh-ed25519'

    :param key: Key to check
    :return: True, when Key is valid, False when not
    :rtype: bool
    """

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
    """ Checks Mail against a relatively simple REgex Pattern.

    :param mail: Mail to check
    :type mail: str
    :return: False, when the Mail is invalid, True when valid.
    :rtype: bool
    """

    if not re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", mail):
        return False
    else:
        return True


def checkDatetimeFormat(datetime_str: str) -> bool:
    """ Checks a Strings format on date time.

    :param datetime_str: String to check
    :type datetime_str: str
    :return: True when valid, False when not.
    :rtype: bool
    """

    import datetime
    try:
        datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False
    return True


def checkName(name: str) -> bool:
    """ Checks a users (real) Name against a real simple REgex Pattern.

    :param name: Name/String to check
    :type name: str
    :return: True when valid, False when not.
    :rtype: bool
    """

    if not re.match("\w+\s*\w", name):
        return False
    else:
        return True


def checkImportFile(path: str, db: str):
    """ Checks an CSV file against most of the validators and prints an Error message with the line number corresponding
    to said failure.. Those includes: checkName, checkUsernameCharacters,
    ckeckUsernameLength, duplicate usernames(in the CSV), checkSSHKey, checkEmail, checkUserExists, checkUserInDB,
    checkDatetimeformat and if the status is 1 or 0.

    :param path: Path to file to check
    :type path: str
    :param db: Path to database file(SQLite)
    :type db: str
    :return: Str when Failure, True when success(All tests passed)
    :rtype: Str or None
    """

    errstr = ""
    valid = True
    ln = 1  # line number
    valid_names_list = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # if any of this fails move on to the next user, just print a relatively helpful message lel
            if not lib.Validator.checkName(row["name"]):
                errstr += f"Line {ln}: Name: '{row['name']}' seems not legit. Character followed by character should" \
                          f" be correct.\n"
                valid = False
            if not lib.Validator.checkUsernameCharacters(row["username"]):
                errstr += (f"Line {ln}: Username contains unsupported characters or starts with a number: '"
                           f"{row['username']}'.\n")
                valid = False
            if not lib.Validator.checkUsernameLength(row["username"]):
                errstr += f"Line {ln}: Username '{row['username']}' is either too long(>16) or short(<3)\n"
                valid = False
            # dup checking
            if row["username"] in valid_names_list:
                errstr += f"Line {ln}: Duplicate Username {row['username']}!\n"
                valid = False
            else:
                valid_names_list.append(row["username"])
            # dup end
            if not lib.Validator.checkSSHKey(row["pubkey"]):
                errstr += f"Line {ln}: Following SSH-Key of user '{row['username']}' isn't valid: " \
                          f"'{row['pubkey']}'.\n"
                valid = False
            if not lib.Validator.checkEmail(row["email"]):
                errstr += f"Line {ln}: E-Mail address of user '{row['username']}' '{row['email']}' is not valid.\n"
                valid = False
            if not lib.Validator.checkUserExists(row["username"]) or checkUserInDB(row["username"], db):
                errstr += f"Line {ln}: User '{row['username']}' already exists.\n"
                valid = False
            if not lib.Validator.checkDatetimeFormat(row["timestamp"]):
                errstr += f"Line {ln}: Timestamp '{row['timestamp']}' from user '{row['username']}' is invalid.\n"
                valid = False
            if int(row["status"]) > 1 or int(row["status"]) < 0:
                errstr += f"Line {ln}: Status '{row['status']}' MUST be either 0 or 1.\n"
                valid = False
            ln += 1
    if valid:
        return True
    else:
        return errstr
