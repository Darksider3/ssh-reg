#!/usr/bin/env python3

import ListUsers
import csv
import io
import lib.CFG as CFG

if __name__ == "__main__":
    try:
        L = ListUsers.ListUsers()
        fetch = L.getFetch()
        ret = io.StringIO()
        writer = csv.writer(ret, quoting=csv.QUOTE_NONNUMERIC) # @TODO: Should be a specific dialect instead?
        writer.writerow(['id', 'username', 'email', 'name', 'pubkey' 'timestamp', 'status'])
        for user in fetch:
            writer.writerow([user['id'], user['username'], user['email'], user['name'], user['pubkey'],
                            user['timestamp'], user['status']])

        if CFG.args.file == "stdout":
            print(ret.getvalue())
        else:
            with open(CFG.args.file, "w") as f:
                print(ret.getvalue(), file=f)
        exit(0)
    except KeyboardInterrupt as e:
        pass