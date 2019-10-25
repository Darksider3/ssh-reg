class General(Exception):
    pass


class User(General):
    pass


class UnknownUser(User):
    def __init__(self, name):
        Exception.__init__(self, f"Tried to perform action on unknown user '{name}'")


class UserExistsAlready(User):
    def __init__(self, name):
        Exception.__init__(self, f"User '{name}' is already registered")


class UnknownReturnCode(General):
    pass


class ModifyFilesystem(General):
    pass


class SSHDirUncreatable(ModifyFilesystem):
    pass


class SQLiteDatabaseDoesntExistYet(General):
    pass


class UsernameLength(User):
    pass


class UsernameTooShort(User):
    pass


class UsernameTooLong(User):
    pass


class UsernameInvalidCharacters(User):
    pass
