#!/usr/bin/env python3

import csv
import os
import configparser
import lib.UserExceptions
import lib.uis.config_ui  # dont go to default, just following -c flag


def import_from_file(file_path: str, db: str, user_ids: tuple = tuple([])) -> bool:
    """ Imports Users from a given CSV-file to the system and DB

    :param file_path:
    :type file_path: str
    :param db: Path to the sqlite db
    :type db: str
    :param user_ids: FIXME: Tuple which user_ids should we write
    :type user_ids: tuple
    :return: True on success, False when not
    :rtype: bool
    """
    if not os.path.isfile(file_path):
        print(f"File {file_path} don't exist")
        return False
    if not os.path.isfile(db):
        print(f"The database file {db} don't exist")
        return False
    if user_ids:
        pass  # empty tuple means everything
    # noinspection PyBroadException
    try:
        with open(file_path, 'r', newline='') as f:
            import lib.Validator
            sql = lib.sqlitedb.SQLiteDB(db)
            err = lib.Validator.checkImportFile(file_path, db)
            if err is not True:
                print(err)
                exit(0)
            import lib.sqlitedb
            import lib.System
            sys_ctl = lib.System.System("root")
            reader = csv.DictReader(f)  # @TODO csv.Sniffer to compare? When yes, give force-accept option
            for row in reader:
                if row["status"] == "1":
                    try:
                        sys_ctl.setUser(row["username"])
                        sys_ctl.aio_register(row["pubkey"])
                        print(row['username'], "====> Registered.")
                    except lib.UserExceptions.General as GeneralExcept:
                        print(f"Something didnt work out! {GeneralExcept}")
                elif row["status"] == "0":
                    print(row['username'] + " not approved, therefore not registered.")
                try:
                    sql.safequery(
                        "INSERT INTO `applications` (username, name, timestamp, email, pubkey, status) "
                        "VALUES (?,?,?,?,?,?)", tuple([row["username"], row["name"], row["timestamp"],
                                                       row["email"], row["pubkey"], row["status"]]))
                except OSError as E:
                    pass
                    print(f"UUFFF, something went WRONG with the file {file_path}: {E}")
    except Exception as didntCatch:
        print(f"Exception! UNCATCHED! {type(didntCatch)}: {didntCatch}")
    return True


if __name__ == "__main__":

    ArgParser = lib.uis.config_ui.argparser
    ArgParser.description += "- Imports a CSV file consisting of user specific details to the database"
    ArgParser.add_argument('-f', '--file', default="stdout",
                           type=str, help='Import from CSV file', required=True)
    ArgParser.add_argument('--Import', default=False, action="store_true",
                           help="Import Users.", required=True)
    args = ArgParser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    try:
        if not args.Import:
            print("Error, need the import flag")
        if not args.file:
            print("Error, need the import file")
            if not args.file:
                print("You MUST set a CSV-file with the -f/--file flag that already exist")
                exit(1)
        import_from_file(args.file, config['DEFAULT']['applications_db'])
        exit(0)
    except KeyboardInterrupt as e:
        pass
