import argparse
import lib.cwd

argparser = argparse.ArgumentParser(description='Tilde administration tools')
argparser.add_argument('-c', '--config', default=lib.cwd.cwd,
                       type=str, help='Path to configuration file', required=False)
