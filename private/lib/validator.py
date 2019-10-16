import re
import pwd


def checkUsernameCharacters(username: str):
    if " " not in username and "_" not in username and username.isascii() and username.islower() and \
            not username[0].isnumeric():
        if not re.search(r"\W+", username):
            if not re.search("[^a-z0-9]", username):
                return True
    return False


def checkUsernameLength(username: str):
    if len(username) > 16:
        return False
    if len(username) < 3:
        return False
    return True


def checkUserExists(username: str):
    try:
        pwd.getpwnam(username)
    except KeyError:
        return False  # User already exists
    else:
        return True  # User doesnt exist


def checkSSHKey(key: str):
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


def checkEmail(mail: str):
    if not re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", mail):
        return False
    else:
        return True
