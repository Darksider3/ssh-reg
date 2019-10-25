#!/usr/bin/env python3

import configparser
import lib.uis.config_ui  # only follow -c flag
import lib.Validator
import lib.sqlitedb
import lib.System
import lib.UserExceptions
import sqlite3

if __name__ == "__main__":
    lib.uis.config_ui.argparser.description += " - Edit Tilde Users"
    ArgParser = lib.uis.config_ui.argparser
    ArgParser.add_argument('--user', type=str,
                           help='Tilde users name to edit', required=True)

    Mutually = ArgParser.add_mutually_exclusive_group()
    Mutually.add_argument('-r', '--remove', default=False, action="store_true",
                          help='Remove an approved/unapproved User from the system(and DB). Effectively purges him.',
                          required=False)
    Mutually.add_argument("--verify", default=True, action="store_false",
                          help="Turns off value checks",
                          required=False)

    ArgParser.add_argument('--sshpubkey', type=str, default=None,
                           help="Stores the new given SSH-Key in given user", required=False)
    ArgParser.add_argument('--name', type=str, default=None,
                           help="Sets the stored name of the given user")
    ArgParser.add_argument('--username', type=str, default=None,
                           help="Rename given User")
    ArgParser.add_argument('--email', type=str, default=None,
                           help="Set new email address for given user")
    ArgParser.add_argument('--status', type=int, default=None,
                           help="Set status of given user")
    args = ArgParser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    try:
        db = config['DEFAULT']['applications_db']
        if not args.sshpubkey and not args.name and not args.username and not args.email and args.status is None \
                and not args.remove:
            print(f"Well, SOMETHING must be done with {args.user} ;-)")
            exit(1)
        # --> --user
        if not lib.Validator.checkUserInDB(args.user, db):
            print(f"User {args.user} does not exist in the database.")
            exit(1)
        DB = lib.sqlitedb.SQLiteDB(db)
        sys_ctl = lib.System.System(args.user)
        if not DB:
            print("Could not establish connection to database")
            exit(1)
        CurrentUser = DB.safequery("SELECT * FROM `applications` WHERE `username`=?", tuple([args.user]))[0]

        # --> --remove
        if args.remove:
            print(f"Removing {args.user} from the system and the database...")
            try:
                DB.removeApplicantFromDBperUsername(args.user)
                print(f"Purged from the DB")
                if CurrentUser["status"] == 1:
                    sys_ctl.remove_user()
                    print(f"Purged from the system")
                else:
                    print(f"'{args.user}' was not approved before, therefore not deleting from system itself.")
            except lib.UserExceptions.General as e:
                print(f"{e}")
                exit(1)
            print(f"Successfully removed '{args.user}'.")
            exit(0)

        # --> --sshpubkey
        if args.sshpubkey:
            if not lib.Validator.checkSSHKey(args.sshpubkey):
                print(f"Pubkey '{args.sshpubkey}' isn't valid.")
                exit(1)
            try:
                DB.safequery("UPDATE `applications` SET `pubkey`=? WHERE `username`=?",
                             tuple([args.sshpubkey, args.user]))
                CurrentUser = DB.safequery("SELECT * FROM `applications` WHERE `username` = ? ", tuple([args.user]))[0]
                if int(CurrentUser["status"]) == 1:
                    sys_ctl.make_ssh_usable(args.sshpubkey)
            except sqlite3.Error as e:
                print(f"Something unexpected happened! {e}")
                exit(1)
            except lib.UserExceptions.ModifyFilesystem as e:
                print(f"One action failed during writing the ssh key back to the authorization file. {e}")
            print(f"'{args.user}'s SSH-Key updated successfully.")

        # --> --name
        if args.name:
            if not lib.Validator.checkName(args.name):
                print(f"'{args.name}' is not a valid Name.")
                exit(1)
            try:
                DB.safequery("UPDATE `applications` SET `name` =? WHERE `username` =?", tuple([args.name, args.user]))
            except sqlite3.Error as e:
                print(f"Could not write '{args.name}' to database: {e}")
            print(f"'{args.user}'s Name changed to '{args.name}'.")

        # --> --email
        if args.email:
            if not lib.Validator.checkEmail(args.email):
                print(f"'{args.email}' is not a valid Mail address!")
                exit(1)
            try:
                DB.safequery("UPDATE `applications` SET `email` =? WHERE `username` =?", tuple([args.email]))
            except sqlite3.Error as e:
                print(f"Could not write '{args.email}' to the database. {e}")
            print(f"'{args.user}' Mail changed to '{args.email}'.")

        # --> --status
        if args.status is not None:
            if args.status != 0 and args.status != 1:
                print("Only 0 and 1 are valid status, where 1 is activated and 0 is unapproved.")
                exit(0)

            # just takes first result out of the dict
            if args.status == int(CurrentUser["status"]):
                print(f"New and old status are the same.")

            if args.status == 0 and int(CurrentUser["status"]) == 1:
                try:
                    DB.safequery("UPDATE `applications` SET `status` =? WHERE `id`=?",
                                 tuple([args.status, CurrentUser["id"]]))
                    sys_ctl.remove_user()
                except sqlite3.Error as e:
                    print(f"Could not update database entry for '{args.user}', did not touch the system")
                    exit(1)
                except lib.UserExceptions.UnknownReturnCode as e:
                    print(f"Could not remove '{args.user}' from the system, unknown return code: {e}. DB is modified.")
                    exit(1)
                print(f"Successfully changed '{args.user}'s status to 0 and cleared from the system.")

            if args.status == 1 and int(CurrentUser["status"]) == 0:
                try:
                    DB.safequery("UPDATE `applications` SET `status`=? WHERE `username`=?",
                                 tuple([args.status, args.user]))
                    sys_ctl.aio_approve(CurrentUser["pubkey"])
                except sqlite3.Error as e:
                    print(f"Could not update Users status in database")
                    exit(1)
                except lib.UserExceptions.General as ChangeUser:
                    print(f"Some chain in the cattle just slipped away, my lord! {ChangeUser}")
                    exit(1)
                print(f"Successfully changed '{args.user}'s status to 1 and created on the system.")
        exit(0)
    except KeyboardInterrupt as e:
        pass
