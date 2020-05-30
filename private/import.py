#!/usr/bin/env python3
"""
Import users or sanitize backup files
"""
import configparser
import csv
import os

import lib.UserExceptions
import lib.uis.config_ui  # dont go to default, just following -c flag
import lib.Validator


def import_from_file(file_path: str, database_file: str, user_ids: tuple = tuple([])) -> bool:
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
    if not os.path.isfile(database_file):
        print(f"The database file {database_file} don't exist")
        return False
    if user_ids:
        pass  # empty tuple means everything
    # noinspection PyBroadException
    try:
        with open(file_path, 'r', newline='') as f:
            import lib.sqlitedb
            import lib.System
            sql = lib.sqlitedb.SQLiteDB(database_file)
            err = lib.Validator.checkImportFile(file_path, database_file)
            if err is not True:
                print(err)
                exit(0)
            sys_ctl = lib.System.System("root")
            reader = csv.DictReader(f)  # @TODO csv.Sniffer to compare? When yes, give force-accept option
            for row in reader:
                if row["status"] == "1":
                    try:
                        sys_ctl.setUser(row["username"])
                        sys_ctl.aio_approve(row["pubkey"])
                        print(row['username'], "====> Registered.")
                    except lib.UserExceptions.General as general_except:
                        print(f"Something didnt work out! {general_except}")
                elif row["status"] == "0":
                    print(row['username'] + " not approved, therefore not registered.")
                try:
                    sql.safequery(
                        "INSERT INTO `applications` (username, name, timestamp, email, pubkey, status) "
                        "VALUES (?,?,?,?,?,?)", tuple([row["username"], row["name"], row["timestamp"],
                                                       row["email"], row["pubkey"], row["status"]]))
                except OSError as os_exception:
                    print(f"UUFFF, something went WRONG with the file {file_path}: {os_exception}")
    except Exception as didnt_catch:
        print(f"Exception! UNCATCHED! {type(didnt_catch)}: {didnt_catch}")
    return True


if __name__ == "__main__":

    ArgParser = lib.uis.config_ui.argparser
    ArgParser.description += "- Imports a CSV file consisting of user specific details to the database"
    ArgParser.add_argument('-f', '--file', default="stdout",
                           type=str, help='Import from CSV file', required=True)
    ArgParser.add_argument('--Import', default=False, action="store_true",
                           help="Import Users. If not set, just sanitize the supplied csv", required=False)
    args = ArgParser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)

    if not args.file:
        print("Error, need the import file")
    if not args.Import:
        # we assume that you just want to sanitize the backup
        if not os.path.isfile(args.file):
            print(f"File {args.file} doesnt exist")
            exit(1)
        sanitized = lib.Validator.checkImportFile(args.file, config['DEFAULT']['applications_db'])
        if sanitized is not True:
            print(sanitized)
        else:
            print(f"{args.file} is valid!")
        exit(0)
    elif args.Import:
        import_from_file(args.file, config['DEFAULT']['applications_db'])
    exit(0)
