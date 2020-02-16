import lib.uis.config_ui

argparser = lib.uis.config_ui.argparser

# store_true just stores true when the command is supplied, so it doesn't need choices nor types
argparser.add_argument('-u', '--unapproved', default=False, action="store_true",
                       help='only unapproved users. Default is only approved.', required=False)
argparser.add_argument('-a', '--approved', default=False, action="store_true",
                       help="Only approved Users.", required=False)
argparser.add_argument('-f', '--file', default="stdout",
                       type=str, help='write to file instead of stdout', required=False)
