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


class HomeDirExistsAlready(ModifyFilesystem):
    pass
