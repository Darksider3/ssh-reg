import configparser
import lib.uis.default as default_cmd

args = default_cmd.argparser.parse_args()
config = configparser.ConfigParser()
config.read(args.config)
