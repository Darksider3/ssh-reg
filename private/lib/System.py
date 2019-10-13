import sys, os, subprocess, pwd
"""
    @staticmethod
    def __execScript(user):
        # @TODO: omfg just write some wrapper-class/lib... sucks hard!
        username = user["username"]
        home_dir = "/home/" + username + "/"
        ssh_dir = home_dir + ".ssh/"
        executed = []
"""


class System:
    dry = False
    create_command = []
    home = ""

    def __init__(self, dryrun: bool = False, home: str = "/home/"):
        self.dry = dryrun
        self.home = home

    def register(self, username: str, pubkey: str, cc: tuple = tuple(["useradd", "-m"])):
        create_command = cc
        cc = create_command + tuple([username])
        if self.dry:
            self.printTuple(cc)
            return 0
        elif not self.dry:
            rt = subprocess.call(cc)
            if rt != 0:
                print(f"Could not create user {username}; '{cc}' returned '{rt}'") # @TODO Logging/Exception
                return False

    def unregister(self, username: str):
        pass

    def make_ssh_usable(self, username: str, pubkey: str, sshdir: str = ".ssh/"):
        if self.dry:
            print("Nah, @TODO, but actually kinda too lazy for this lul. Just a lot happening here")
            return True
        if not sshdir.endswith("/"):
            return False # @TODO Exception in Log
        ssh_dir = self.home + username + "/" + sshdir
        try:
            os.mkdir(ssh_dir)
        except FileExistsError:
            pass # thats actually a good one for us :D
        except OSError as e:
            print(f"Could not create {ssh_dir}: Exception: {e}")
            return False
        with open(ssh_dir + "authorized_keys",  "w") as f:
            print(pubkey, file=f)
            f.close()
        try:
            os.chmod(ssh_dir + "authorized_keys", 0o700)  # directory is already 777?
            os.chmod(ssh_dir, 0o700)  # directory is already 777?
        except OSError as e:
            print(f"Could not chmod 0700 {ssh_dir} or {ssh_dir}/authorized_keys, Exception: {e}")
            return False
        try:
            pwdnam = pwd.getpwnam(username)
            os.chown(ssh_dir, pwdnam[2], pwdnam[3]) # 2=>uid, 3=>gid
            os.chown(ssh_dir + "authorized_keys", pwd.getpwnam(username)[2], pwd.getpwnam(username)[3])
        except OSError as e:
            print(f"Could not chown {ssh_dir} and/or authorized_keys to {username} and their group, Exception: {e}")
            return False
        return True

    def lock_user_pw(self, username: str, cc: tuple = tuple(["usermod", "--lock"])):
        lock_command = cc
        cc = lock_command + tuple([username])
        if self.dry:
            self.printTuple(cc)
            return 0
        elif not self.dry:
            rt = subprocess.call(cc)
            if rt != 0:
                print(f"Could not lock user '{username}'; '{cc}' returned '{rt}'")

    def add_to_usergroup(self, username: str, group: str = "tilde", cc: tuple = tuple(["usermod", "-a", "-G"])):
        add_command = cc
        cc = add_command + tuple([group, username])
        if self.dry:
            self.printTuple(cc)
            return 0
        elif not self.dry:
            rt = subprocess.call(cc)
            if rt != 0:
                print(f"Could not add user '{username}' to group '{group}' with command '{cc}', returned '{rt}'")

    def printTuple(self, tup: tuple):
        pp = ""
        for i in tup:
            pp += i + " "
        print(pp)


if __name__ == "__main__":
    try:
        S = System(dryrun=True)
        S.register("dar", "test")
        S.lock_user_pw("dar")
        S.add_to_usergroup("dar")
        #if not S.make_ssh_usable("dar", "SSHpub"):
        #    print("Huh, error :shrug:")
        exit(0)
    except KeyboardInterrupt:
        pass
