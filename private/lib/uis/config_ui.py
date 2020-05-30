import argparse
import lib.cwd

argparser = argparse.ArgumentParser(description='Tilde administration tools ',
                                    conflict_handler="resolve")
argparser.add_argument('-c', '--config', default=lib.cwd.cwd,
                       type=str,
                       help='Path to configuration file. If not set, we look for it in $TILDE_CONF',
                       required=False)
