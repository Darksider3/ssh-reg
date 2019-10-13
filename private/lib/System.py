import sys
import os
import subprocess
import pwd


class System:
    dry = False
    create_command = []
    home = ""

    def __init__(self, dryrun: bool = False, home: str = "/home/"):
        self.dry = dryrun
        self.home = home

    def register(self, username: str, pubkey: str, cc: tuple = tuple(["useradd", "-m"])) -> bool:
        create_command = cc
        cc = create_command + tuple([username])
        if self.dry:
            self.printTuple(cc)
            return True
        elif not self.dry:
            rt = subprocess.call(cc)
            if rt != 0:
                print(f"Could not create user {username}; '{cc}' returned '{rt}'", file=sys.stderr)
                # @TODO Logging/Exception
                return False
            return True

    def unregister(self, username: str):
        pass

    # @TODO errno
    def make_ssh_usable(self, username: str, pubkey: str, sshdir: str = ".ssh/") -> bool:
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
            print(f"Could not create {ssh_dir}: Exception: {e}", file=sys.stderr)
            return False
        try:
            with open(ssh_dir + "authorized_keys", "w") as f:
                print(pubkey, file=f)
                f.close()
            os.chmod(ssh_dir + "authorized_keys", 0o700)  # directory is already 777?
            os.chmod(ssh_dir, 0o700)  # directory is already 777?
        except OSError as e:
            print(f"Could not write and/or chmod 0700 {ssh_dir} or {ssh_dir}/authorized_keys, Exception: {e}",
                  file=sys.stderr)
            return False  # @TODO Exception in Log
        try:
            pwdnam = pwd.getpwnam(username)
            os.chown(ssh_dir, pwdnam[2], pwdnam[3]) # 2=>uid, 3=>gid
            os.chown(ssh_dir + "authorized_keys", pwd.getpwnam(username)[2], pwd.getpwnam(username)[3])
        except OSError as e:
            print(f"Could not chown {ssh_dir} and/or authorized_keys to {username} and their group, Exception: {e}",
                  file=sys.stderr)
            return False  # @TODO Exception in Log
        return True

    def lock_user_pw(self, username: str, cc: tuple = tuple(["usermod", "--lock"])) -> bool:
        lock_command = cc
        cc = lock_command + tuple([username])
        if self.dry:
            self.printTuple(cc)
            return True
        elif not self.dry:
            rt = subprocess.call(cc)
            if rt != 0:
                print(f"Could not lock user '{username}'; '{cc}' returned '{rt}'", file=sys.stderr)
                return False
                # @TODO Exception in Log
            return True

    def add_to_usergroup(self, username: str, group: str = "tilde", cc: tuple = tuple(["usermod", "-a", "-G"])) -> bool:
        add_command = cc
        cc = add_command + tuple([group, username])
        if self.dry:
            self.printTuple(cc)
            return True
        elif not self.dry:
            rt = subprocess.call(cc)
            if rt != 0:
                print(f"Could not add user '{username}' to group '{group}' with command '{cc}', returned '{rt}'",
                      file=sys.stderr)  # @TODO Exception in Log
                return False
            return True

    def printTuple(self, tup: tuple) -> None:
        pp = ""
        for i in tup:
            pp += i + " "
        print(pp)

    def removeUser(self, username: str, cc: tuple = tuple(["userdel", "-r"])) -> bool:
        remove_command = cc
        cc = remove_command + tuple([username])
        if self.dry:
            self.printTuple(cc)
            return True
        else:
            ret = subprocess.call(cc)
            if ret != 0:
                print(f"Could not delete user with command {cc}. Return code: {ret}")
                return False
            return True


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
