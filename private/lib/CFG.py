import configparser
import logging
import lib.uis.default as default_cmd

args = default_cmd.argparser.parse_args()
CONF_FILE = args.config
config = configparser.ConfigParser()
config.read(CONF_FILE)
logging.basicConfig(format="%(asctime)s: %(message)s",
                    level=int(config['LOG_LEVEL']['log_level'])
                    )