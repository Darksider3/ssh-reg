#!/usr/bin/env python3

from lib.sqlitedb import SQLitedb
import lib.CFG as CFG

if __name__ == "__main__":
    try:
        SQLitedb(CFG.REG_FILE)
        print("hi")
        exit(0)
    except KeyboardInterrupt:
        pass
