import configparser
import lib.uis.config_ui  # only follow -c flag
import lib.validator
import sqlite3

lib.uis.config_ui.argparser.description += " - Edit Tilde Users"
ArgParser = lib.uis.config_ui.argparser
ArgParser.add_argument('--user', type=str,
                       help='Tilde users name to edit', required=True)

Mutually = ArgParser.add_mutually_exclusive_group()
Mutually.add_argument('-r', '--remove', default=False, action="store_true",
                      help='Remove an approved/unapproved User from the system. Effectively purges him.',
                      required=False)
Mutually.add_argument('-a', '--approve', default=False, action="store_true",
                      help="Approve the given user", required=False)
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


if __name__ == "__main__":
    try:
        db = config['DEFAULT']['applications_db']
        if not args.sshpubkey and not args.name and not args.username and not args.email and not args.status \
                and not args.approve and not args.remove:
            print(f"Well, SOMETHING must be done with {args.user} ;-)")
            exit(1)
        if not lib.validator.checkUserInDB(args.user, db):
            print(f"User {args.user} doesn't exist in the database.")
            exit(1)
        import lib.sqlitedb
        import lib.System
        import lib.UserExceptions
        DB = lib.sqlitedb.SQLitedb(db)
        Sysctl = lib.System.System()
        if not DB:
            print("Couldn't establish connection to database")
            exit(1)
        if args.sshpubkey:
            if not lib.validator.checkSSHKey(args.sshpubkey):
                print(f"Pubkey {args.sshpubkey} isn't valid.")
                exit(1)
            try:
                DB.safequery("UPDATE `applications` SET `pubkey`=? WHERE `username`=?",
                             tuple([args.sshpubkey, args.user]))
            except sqlite3.Error as e:
                print(f"Something unexpected happened! {e}")
                exit(1)
            fetch = DB.safequery("SELECT * FROM `applications` WHERE `username` = ? ", tuple([args.user]))
            if int(fetch[0]["status"]) == 1:
                try:
                    Sysctl.make_ssh_usable(args.user, args.sshpubkey)
                except lib.UserExceptions.ModifyFilesystem as e:
                    print(f"One action failed during writing the ssh key back into the authorization file")
            print(f"{args.user} updated successfully.")

        if args.name:
            pass
        if args.username:
            print(f"{args.username}")
        if args.email:
            print(f"{args.email}")
        if args.status:
            print(f"{args.status}")
        exit(0)
    except KeyboardInterrupt as e:
        pass
