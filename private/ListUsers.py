#!/usr/bin/env python3

import configparser
import lib.uis.default as default_cmd  # Follows -u, -a, -f flags
from lib.ListUsers import ListUsers

if __name__ == "__main__":
    default_cmd.argparser.description += " - Lists Users from the Tilde database."
    default_cmd.argparser.add_argument('--list-asc', default=False, action="store_true",
                                       help='Output a newline seperated list of users', required=False, dest="args_asc")
    default_cmd.argparser.add_argument('--single_user', default=None, type=str,
                                       help="Just show a specific single_user by it's name", required=False)
    args = default_cmd.argparser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)

    OUTPUT = ""
    if args.single_user is not None:
        L = ListUsers(config['DEFAULT']['applications_db'], unapproved=args.unapproved, approved=args.approved,
                      single_user=args.single_user)
    else:
        L = ListUsers(config['DEFAULT']['applications_db'], unapproved=args.unapproved, approved=args.approved)
    if args.args_asc:
        OUTPUT = L.output_as_list()
    else:
        users = L.get_fetch()
        OUTPUT += "ID %-1s| Username %-5s| Mail %-20s| Name %-17s| Registered %-8s | State |\n" % (
            " ", " ", " ", " ", " "
        )
        OUTPUT += 102 * "-" + "\n"
        for single_user in users:
            OUTPUT += "%-4i| %-14s| %-25s| %-22s| %-8s | %-5i |\n" % (
                single_user["id"], single_user["username"], single_user["email"],
                single_user["name"], single_user["timestamp"], single_user["status"]
            )
    if args.file != "stdout":
        with open(args.file, 'w') as f:
            print(OUTPUT, file=f)
    else:
        print(OUTPUT)
    exit(0)
