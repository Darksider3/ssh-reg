import lib.uis.config_ui

argparser = lib.uis.config_ui.argparser

# store_true just stores true when the command is supplied, so it doesn't need choices nor types
argparser.add_argument('-u', '--unapproved', default=False, action="store_true",
                       help='only unapproved users. Default is only approved.', required=False)
argparser.add_argument('-a', '--approved', default=False, action="store_true",
                       help="Only approved Users.", required=False)
argparser.add_argument('-f', '--file', default="stdout",
                       type=str, help='write to file instead of stdout', required=False)
argparser.add_argument('--Import', default=False, action="store_true",
                       help="Import Users from file. Affects currently only Import.py.\n"
                            "Setting this to true will result in -f being interpreted as the input file to import "
                            "users from. The file MUST be a comma separated CSV file being readable having it's "
                            "defined columns written in the first line.")
