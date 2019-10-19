class General(Exception):
    pass


class UnknownUser(General):
    pass


class UnknownReturnCode(General):
    pass


class UserExistsAlready(UnknownReturnCode):
    pass


class ModifyFilesystem(General):
    pass


class SSHDirUncreatable(ModifyFilesystem):
    pass


class SQLiteDatabaseDoesntExistYet(General):
    pass


class User(Exception):
    pass


class UsernameLength(User):
    pass


class UsernameTooShort(User):
    pass


class UsernameTooLong(User):
    pass


class UsernameInvalidCharacters(User):
    pass
