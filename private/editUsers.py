import lib.uis.default

argparser = lib.uis.default.argparser

args = argparser.parse_args()
config = argparser.ConfigParser()
config.read(args.config)
