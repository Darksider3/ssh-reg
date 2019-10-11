#!/usr/bin/env python3

import configparser, logging, sqlite3, argparse, pwd
import os
import subprocess


# Clear shell
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# create dictionary out of sqlite results
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# prints command(but doesnt execute them)
# need this for work, just convenience
def debugExec(commands):
    print("Commands: {!s} -> Returns 0".format(commands))
    return 0


# @TODO hardcoded config?
cwd = os.environ.get('TILDE_CONF')
if cwd is None:
    cwd = os.getcwd() + "/applicationsconfig.ini"
else:
    if os.path.isfile(cwd) is False:
        cwd = os.getcwd() + "/applicationsconfig.ini"
# cwd is now either cwd/applicationsconfig or $TILDE_CONF
argparser = argparse.ArgumentParser(description='interactive registration formular for tilde platforms')
argparser.add_argument('-c', '--config', default=cwd,
                       type=str, help='Path to configuration file', required=False)
args = argparser.parse_args()

CONF_FILE = args.config
config = configparser.ConfigParser()
config.read(CONF_FILE)
logging.basicConfig(format="%(asctime)s: %(message)s",
                    level=int(config['LOG_LEVEL']['log_level'])
                    )
del cwd
REG_FILE = config['DEFAULT']['applications_db']


# Does everything related to applicants, i.e. creating, manipulations...
class Applicants:
    # User identifier
    identifier = "username"
    # SQLite DB Path
    sourceDB = ""
    # another sqlite to batch-recreate users
    differentDB = ""

    def __init__(self, lident, sourcedb=REG_FILE):
        self.identifier = lident
        self.sourceDB = sourcedb
        self.__connectToDB__("source")
        # all results shall be done with dict_factory! Makes everything so much simpler
        self.sdbCursor.row_factory = dict_factory

    def __del__(self):
        self.__closeDB__("source")

    def __connectToDB__(self, which):
        if which == "source":
            try:
                self.sdbConnection = sqlite3.connect(self.sourceDB)
                self.sdbCursor = self.sdbConnection.cursor()
            except sqlite3.Error as e:
                logging.exception("Database: Couldn't open database and get cursor: %s" % e)
        else:
            self.ddbConnection = sqlite3.connect(self.differentDB)
            self.ddbCursor = self.ddbConnection.cursor()

    def __closeDB__(self, which):
        if which == "source":
            try:
                self.sdbConnection.close()
            except sqlite3.Error as e:
                logging.exception(
                    "Couldn't close database! Error: %s" % e)
                # @TODO: Dump full db with query or just the executed querys to file
        else:
            self.ddbConnection.close()  # @TODO: Evaluate getting rid of ddb(differentDB)?

    # get List of all applications(not accepted yet)
    def getapplicationslist(self):
        query = "SELECT * FROM `applications` WHERE `status` = '0'"
        try:
            self.sdbCursor.execute(query)
            rows = self.sdbCursor.fetchall()
        except sqlite3.Error as e:
            logging.exception("Database Error: %s" % e)
            rows = []
        return rows

    def getapprovedapplicantslist(self):
        query = "SELECT * From `applications` WHERE `status` = '1'"
        try:
            self.sdbCursor.execute(query)
            rows = self.sdbCursor.fetchall()
        except sqlite3.Error as e:
            logging.exception("Database Error: %s" % e)
            rows = []
        return rows

    # edit aproved users
    def editapprovedapplicants(self, term):
        try:
            # the fuck did i try here?
            self.sdbCursor.execute(
                "UPDATE `applications`  WHERE id=?", (str(term),)
            )
            self.sdbConnection.commit()
        except sqlite3.Error as e:
            logging.exception("Database Error: %s" % e)

    # set user to aproved
    def setapprovedapplication(self, selectterm):
        # query = "SELECT `username` FROM `applications` WHERE `username` = `{0!s}`".format(selectterm)
        pass

    # get applicants data
    def getapplicantsdata(self, term):
        # @TODO: Use shorthand if for the correct query, directly into sqlite
        if self.identifier == "id":
            try:
                self.sdbCursor.execute(
                    "SELECT * FROM `applications` WHERE id = ?",
                    (str(term),)
                )
            except sqlite3.Error as e:
                logging.exception("Database Error: %s" % e)

        else:
            self.sdbCursor.execute(
                "SELECT * FROM `applications` WHERE username = ?",
                (str(term),)
            )
        result = self.sdbCursor.fetchone()
        return result

    # @TODO: migrade just approved users to some new/another sqlitedb
    def migrateapproveddata(self, different_db):
        pass

    # @TODO: delete migrated data
    def deletemigrateddata(self, selectterm):
        pass

    # Applicants whom doesnt got approved should get removed
    def removeapplicant(self, term):
        if self.identifier == "id":
            try:
                self.sdbCursor.execute(
                    "DELETE FROM `applications` WHERE id = ?",
                    (str(term),)
                )
                self.sdbConnection.commit()
            except sqlite3.Error as e:
                logging.exception("Database Error: %s" % e)

        else:
            self.sdbCursor.execute(
                'DELETE FROM `applications` WHERE username = ?',
                (str(term),)
            )
            self.sdbConnection.commit()

    # @TODO: Possibility to work without passing users manually
    def selecteduser(userid, username=False):
        pass

    # Print out a list of aprovable users
    def printapprovableusers(self, users):
        i = 0
        for user in users:
            print("ID: {0!s}, Status: {0!s}, Name: {0!s}".format(i, user["status"], user["username"]))
            i += 1
        return i

    # Get List of users
    @staticmethod
    def userprint(fetched, userid):
        print("ID: {0!s}".format(fetched[int(userid)]["id"]))
        print("Username: {0!s}".format(fetched[int(userid)]["username"]))
        print("Mail: {0!s}".format(fetched[int(userid)]["email"]))
        print("SSH: {0!s}".format(fetched[int(userid)]["pubkey"]))
        print("Registrated time: {0!s}".format(fetched[int(userid)]["timestamp"]))

    # Approve an applicant. Handles everything related, like create home dir, set flags blabla
    def approveapplicant(self, term):
        user = self.getapplicantsdata(term)
        ret = self.__execScript(user)
        if ret[0] != 0:  # @DEBUG: Change to == 0
            print("Something went wrong in the user creation! Exiting without deleting users record in database!")
            print("Last executed commands: {0!s}\nreturn code: {1!s}".format(ret[-1][1], ret[-1][0]))
            exit(0)

        if self.identifier == "id":
            try:
                self.sdbCursor.execute(
                    "UPDATE `applications` SET `status`=1 WHERE `id`=?",
                    (str(term),)
                )
                self.sdbConnection.commit()
            except sqlite3.Error as e:
                logging.exception("Database Error: %s" % e)

        else:
            self.sdbCursor.execute(
                "UPDATE `applications` SET `status`=1 WHERE `username`=?",
                (str(term), )
            )
            self.sdbConnection.commit()

    # Script execution, handles everything done with the shell/commands themselves
    @staticmethod
    def __execScript(user):
        # @TODO: omfg just write some wrapper-class/lib... sucks hard!
        username = user["username"]
        home_dir = "/home/" + username + "/"
        ssh_dir = home_dir + ".ssh/"
        executed = []

        executed.append(["useradd", "-m", username])
        returncode = subprocess.call(executed[0])
        if returncode != 0:
            return [returncode, executed, ]

        executed.append(["usermod", "--lock", username])
        returncode = subprocess.call(executed[1])  # empty pw
        if returncode != 0:
            return [returncode, executed, ]

        executed.append(["usermod", "-a", "-G", "tilde", username])
        returncode = subprocess.call(executed[2])  # add to usergroup
        if returncode != 0:
            return [returncode, executed, ]

        executed.append(["mkdir", ssh_dir])
        try:
            # @TODO: use config variable(chmodPerms)
            os.mkdir(ssh_dir, 0o777)  # create sshdir
            returncode = 0
        except OSError as e:
            logging.exception(e.strerror)
            returncode = e.errno  # False, couldn't create.
            return [returncode, executed, ]

        executed.append(["write(sshkey) to", ssh_dir + "authorized_keys"])
        with open(ssh_dir + "authorized_keys", "w") as f:
            f.write(user["pubkey"])
        if not f.closed:
            logging.exception("Could'nt write to authorized_keys!")
            return [returncode, executed, ]

        executed.append(["chmod", "-Rv", "700", ssh_dir])

        try:
            os.chmod(ssh_dir + "authorized_keys", 0o700)  # directory is already 700
            returncode = 0
        except OSError as e:
            logging.exception(e.strerror)
            returncode = e.errno
            return [returncode, executed, ]

        try:
            executed.append(["chown", "-Rv", username + ":" + username, ssh_dir])
            os.chown(ssh_dir, pwd.getpwnam(username)[2], pwd.getpwnam(username)[3])  # 2=>uid, 3=>gid
            executed.append(["chown", "-v", username + ":" + username, ssh_dir + "authorized_keys"])
            os.chown(ssh_dir + "authorized_keys", pwd.getpwnam(username)[2], pwd.getpwnam(username)[3])
            returncode = 0
        except OSError as e:
            logging.exception(e.strerror)  # @TODO: maybe append strerror to executed instead of printing it
            returncode = e.errno
            return [returncode, executed, ]

        return [returncode, executed, ]
        # {'id': 7, 'username': 'testuser47', 'email': '47test@testmail.com', 'name':
        # 'test Name', 'pubkey': 'ssh-rsa [...]', 'timestamp': '2018-08-22 13:31:16', 'status': 0}


def main():
    # how many times the Separator/Delimiter?
    delcount = 40
    # The separator for the menu
    separator = "=" * delcount
    menu = separator + "\n\t\t Main-Menu:\n\n" \
                       "\t 1) list and edit pending users\n" \
                       "\t 2) list applicants\n" \
                       "\t 3) edit applicant\n" \
                       "\t 4) quit\n" + separator + "\n"

    # Identify by ID
    applications = Applicants(lident="id")
    while 1 != 0:
        print(menu)

        command = input("Please select, what you want to do: \n -> ")
        # User shouldn't be able to type something in that isnt a number
        if command.isalpha() or command == '':
            clear()
            print("!!! invalid input, please try again. !!!")
            continue

        # convert
        command = int(command)

        if command == 4 or command == "q":
            exit(0)
        # Edit and list pending users/applicants @TODO Wording: Users or applicants?
        elif command == 1:
            users = applications.getapplicationslist()
            i = applications.printapprovableusers(users)

            if i == 0:
                print("No pending users")
                # giving some time to acknowledge that something WRONG happened
                input("Continue with Keypress...")
                clear()
                continue

            user_selection = 0
            user_max = i
            print("Menu:\n r=>return to main")

            # Edit Menu
            while 1 != 0 or user_selection != "r":
                i = applications.printapprovableusers(users)
                if user_selection == "r":
                    break  # break when user presses r

                user_selection = input("Which user( ID ) do you want to change? ->")
                if len(user_selection) > 1 or user_selection.isalpha():
                    user_selection = ""
                # convert to int if input isnt an r
                user_selection = int(user_selection) if user_selection != '' and user_selection != 'r' else 0
                if user_selection > user_max - 1:
                    print("User {0!s} doesn't exist!".format(user_selection))
                    continue
                # Show the user his chosen user and ask what to do
                applications.userprint(users, user_selection)
                print("You chosed ID No. {0!s}, what do you like to do?".format(user_selection))

                chosen_user = user_selection
                user_selection = ""

                # Finally down the edit menu!
                while user_selection != "e":
                    user_selection = input(
                        "User: {0!s}\n \t\t(A)ctivate \n\t\t(R)emove \n\t\tR(e)turn\n -> ".format(chosen_user))
                    if user_selection == "A":
                        applications.approveapplicant(users[chosen_user]['id'])
                        print("User {0!s} has been successfully approved!".format(users[chosen_user]['username']))
                        input("waiting for input...")
                        clear()
                        user_selection = "e"  # remove for being able to continue editing?
                        continue
                    elif user_selection == "R":
                        applications.removeapplicant(users[chosen_user]['id'])
                        print("User {0!s} successfully deleted!".format(user[chosen_user]['username']))
                        input("waiting for input...")
                        clear()
                        continue
                    elif user_selection == "e":
                        clear()
                        continue

        elif int(command) == 2:
            users = applications.getapprovedapplicantslist()

            if not users:
                print("no activate users yet!")
            i = 0
            for user in users:
                print("ID: {0!s}, Status: {1!s}, Name: {2!s}".format(user["id"], user["status"], user["username"]))
            continue
        elif command == str(3):
            pass
        else:
            exit(0)


if __name__ == "__main__":
    try:
        main()
        exit(0)
    except KeyboardInterrupt:
        pass
        # print("Exception occured. View log file for details.")
        # logging.exception("Some exception occured")
