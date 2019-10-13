import sys
import os
import subprocess
import pwd


class System:
    """Class to interact with the system specifically to support our needs 0w0"""

    dry = False
    create_command = []
    home = ""

    def __init__(self, dryrun: bool = False, home: str = "/home/"):
        """Creates an objects. Can set dry run.

        :param dryrun: Run all command in a dry-run? When enabled, doesn't make any changes to the system (defaults to
        false)
        :type dryrun: bool
        :param home: Standard directory to search for the home directories of your users(default is /home/)
        :type home: str
        """

        self.dry = dryrun
        if not home.endswith("/"):
            home += "/"
        if not os.path.isdir(home):
            raise ValueError("home should be an existent directory...")
        self.home = home

    def register(self, username: str, cc: tuple = tuple(["useradd", "-m"])) -> bool:
        """Creates an local account for the given username

        :param username: Username to create
        :type username: str
        :param cc: Tuple with commands separated to execute on the machine. (defaults to useradd -m)
        :type cc: tuple
        :returns: True, when the user was successfully created, False when not
        :rtype: bool
        """

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
        """ Make SSH usable for our newly registered user

        :param username: Username you want to affect with it, casually used directly after register()
        :type username: str
        :param pubkey: Public SSH Key for the User you want accessible by SSH
        :type pubkey: str
        :param sshdir: Directory to write the authorized_keys File to. PWD is $HOME of said user. (defaults to ".ssh/")
        :type sshdir: str
        :return: True, when everything worked out good, false when something bad happened. Outputs the error of it.
        :rtype: bool
        """

        if self.dry:
            print("Nah, @TODO, but actually kinda too lazy for this lul. Just a lot happening here")
            return True
        if not sshdir.endswith("/"):
            sshdir += "/"
        ssh_dir = self.home + username + "/" + sshdir
        try:
            os.mkdir(ssh_dir)
        except FileExistsError:
            pass  # thats actually a good one for us :D
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
            os.chown(ssh_dir, pwdnam[2], pwdnam[3])  # 2=>uid, 3=>gid
            os.chown(ssh_dir + "authorized_keys", pwd.getpwnam(username)[2], pwd.getpwnam(username)[3])
        except OSError as e:
            print(f"Could not chown {ssh_dir} and/or authorized_keys to {username} and their group, Exception: {e}",
                  file=sys.stderr)
            return False  # @TODO Exception in Log
        return True

    def lock_user_pw(self, username: str, cc: tuple = tuple(["usermod", "--lock"])) -> bool:
        """Lock a users password so it stays empty

        :param username: Username of the user which accounts password you want to lock
        :type username: str
        :param cc: Commands to run in the subprocess to lock it down(defaults to usermod --lock)
        :type cc: tuple
        :rtype: bool
        :return: True when the lock worked, false when not.
        """

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
        """ Adds a given user to a given group

        :param username: Username to add to your wanted group
        :type username: str
        :param group: Groupname where you want to add your user to
        :type group: str
        :param cc: Commands to execute that adds your user to said specific group(defaults to usermod -a -G")
        :type cc: tuple
        :return: True, if worked, False when not.
        :rtype bool
        """

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

    @staticmethod
    def printTuple(tup: tuple) -> None:
        """Prints a tuple with spaces as separators

        :param tup: Tuple you want to print
        :type tup: tuple
        :rtype: None
        :returns: Nothing
        """

        pp = ""
        for i in tup:
            pp += i + " "
        print(pp)

    def removeUser(self, username: str, cc: tuple = tuple(["userdel", "-r"])) -> bool:
        """Removes the specified user from the system

        :param username: The username you want to delete from the system.
        :type username: str
        :param cc: Commands to execute to delete the user from the System(defaults to userdel -r)
        :type cc: tuple
        :return: True, when worked, False if not.
        :rtype: bool
        """

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
        S.register("dar")
        S.lock_user_pw("dar")
        S.add_to_usergroup("dar")
        # if not S.make_ssh_usable("dar", "SSHpub"):
        #    print("Huh, error :shrug:")
        exit(0)
    except KeyboardInterrupt:
        pass
