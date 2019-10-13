import configparser, logging, argparse, os

cwd = os.environ.get('TILDE_CONF')
if cwd is None:
    cwd = os.getcwd() + "/applicationsconfig.ini"
else:
    if os.path.isfile(cwd) is False:
        cwd = os.getcwd() + "/applicationsconfig.ini"
# cwd is now either cwd/applicationsconfig or $TILDE_CONF
argparser = argparse.ArgumentParser(description='Tilde administration tools')
argparser.add_argument('-c', '--config', default=cwd,
                       type=str, help='Path to configuration file', required=False)
# store_true just stores true when the command is supplied, so it doesn't need choices nor types
argparser.add_argument('-u', '--unapproved', default=False, action="store_true",
                       help='only unapproved users. Default is only approved.', required=False)
argparser.add_argument('-a', '--approved', default=False, action="store_true",
                       help="Only approved Users.", required=False)
argparser.add_argument('-f', '--file', default="stdout",
                       type=str, help='write to file instead of stdout', required=False)
args = argparser.parse_args()

CONF_FILE = args.config
config = configparser.ConfigParser()
config.read(CONF_FILE)
logging.basicConfig(format="%(asctime)s: %(message)s",
                    level=int(config['LOG_LEVEL']['log_level'])
                    )
del cwd
REG_FILE = config['DEFAULT']['applications_db']