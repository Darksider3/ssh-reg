import configparser, logging, argparse, os

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