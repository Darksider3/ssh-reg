import csv
import pwd
import re

import lib.sqlitedb


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
        return False
    return True  # User already exists


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
        fetched = ldb.safe_query("SELECT * FROM 'applications' WHERE username = ?", tuple([username]))
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


def checkImportFile(path: str, db: str, test_existence: bool = True):
    """ Checks an CSV file against most of the validators and prints an Error message with the line number corresponding
    to said failure.. Those includes: checkName, checkUsernameCharacters,
    ckeckUsernameLength, duplicate usernames(in the CSV), checkSSHKey, checkEmail, checkUserExists, checkUserInDB,
    checkDatetimeformat and if the status is 1 or 0.

    :param path: Path to file to check
    :type path: str
    :param db: Path to database file(SQLite)
    :type db: str
    :param test_existence: Flag, checking users existence while true, won't when set to false. Default's to true.
    :type test_existence: bool
    :return: Str when Failure, True when success(All tests passed)
    :rtype: Str or None
    """

    err_str = ""
    valid = True
    line = 1  # line number
    valid_names_list = []
    with open(path, 'r', newline='') as file_handle:
        reader = csv.DictReader(file_handle)
        for row in reader:
            # if any of this fails move on to the next user, just print a relatively helpful message lel
            if not lib.Validator.checkName(row["name"]):
                err_str += f"Line {line}: Name: '{row['name']}' seems not legit. " \
                           f"Character followed by character should be correct.\n"
                valid = False
            if not lib.Validator.checkUsernameCharacters(row["username"]):
                err_str += (f"Line {line}: "
                            f"Username contains unsupported characters or starts with a number: '"
                            f"{row['username']}'.\n")
                valid = False
            if not lib.Validator.checkUsernameLength(row["username"]):
                err_str += f"Line {line}: " \
                           f"Username '{row['username']}' is either too long(>16) or short(<3)\n"
                valid = False
            # dup checking
            if row["username"] in valid_names_list:
                err_str += f"Line {line}: Duplicate Username {row['username']}!\n"
                valid = False
            else:
                valid_names_list.append(row["username"])
            # dup end
            if not lib.Validator.checkSSHKey(row["pubkey"]):
                err_str += f"Line {line}: " \
                           f"Following SSH-Key of user '{row['username']}' isn't valid: " \
                           f"'{row['pubkey']}'.\n"
                valid = False
            if not lib.Validator.checkEmail(row["email"]):
                err_str += \
                    f"Line {line}: " \
                    f"E-Mail address of user '{row['username']}' '{row['email']}' is not valid.\n"
                valid = False
            if lib.Validator.checkUserExists(row["username"]) or checkUserInDB(row["username"], db):
                if test_existence:
                    err_str += f"Line {line}: User '{row['username']}' already exists.\n"
                    valid = False
                else:
                    pass
            if not lib.Validator.checkDatetimeFormat(row["timestamp"]):
                err_str += f"Line {line}: Timestamp '{row['timestamp']}' " \
                           f"from user '{row['username']}' is invalid.\n"
                valid = False
            if int(row["status"]) > 1 or int(row["status"]) < 0:
                err_str += f"Line {line}: Status '{row['status']}' MUST be either 0 or 1.\n"
                valid = False
            line += 1
    if valid:
        err_str = True
    return err_str
