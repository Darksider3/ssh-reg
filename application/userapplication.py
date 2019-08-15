#!/usr/bin/env python3

import re, configparser, logging, sqlite3, argparse
from os import getcwd

import re, configparser, logging, sqlite3


try:
  cwd=getcwd()+"/applicationsconfig.ini"
  argparser = argparse.ArgumentParser(description='interactive registration formular for tilde platforms')
  argparser.add_argument('-c', '--config', default=cwd, type=str, help='Config file', required=False)
  args = argparser.parse_args()
  CONF_FILE=args.config
except:
  logging.exception("Argumentparser-Exception: ")

try:
  config = configparser.ConfigParser()
  config.read(CONF_FILE)
  logging.basicConfig(format="%(asctime)s: %(message)s", filename=config['DEFAULT']['log_file'],level=int(config['LOG_LEVEL']['log_level']))
  del(cwd)
  REG_FILE=config['DEFAULT']['applications_db']
except:
  logging.exception("logging or configparser-Exception: ")

VALID_SSH=False
VALID_USER=False


def __createTable(cursor, connection):
  try:
    cursor.execute(
      "CREATE TABLE IF NOT EXISTS applications(" \
      "id INTEGER PRIMARY KEY AUTOINCREMENT,"\
      "username TEXT NOT NULL, email TEXT NOT NULL,"\
      "name TEXT NOT NULL, pubkey TEXT NOT NULL,"\
      "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, status INTEGER NOT NULL DEFAULT 0);")
    connection.commit()
  except:
    logging.exception("Couldn't create needed SQLite Table!")

def addtotable(cursor, connection, username, name, email, pubkey):
  try:
    cursor.execute("INSERT INTO 'applications'(username, name, email, pubkey)VALUES("\
      "?,?,?,?)", [username, name, email, pubkey])
    connection.commit()
  except:
    logging.exception("Couldn't insert user into the db")
  
# check if sqlite file does exists or already and has our structure
def __checkSQLite(cursor, connection):
  #SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='applications'")
  res=cursor.fetchall()
  
  if res== []:
    try:
      __createTable(cursor, connection)
    except:
      logging.exception("couldn't create table on given database. Exception: ")
  else:
    pass
  return True

def check_username(value):
  global VALID_USER
  if len(value) < 3:
    VALID_USER=False
    return False
  try:
    from pwd import getpwnam
    getpwnam(value)
    VALID_USER=False
  except:
    VALID_USER=True
    return True
  return False

      
# taken from https://github.com/hashbang/provisor/blob/master/provisor/utils.py, all belongs to them! ;)
def validate_pubkey(value):
  global VALID_SSH
  import base64
  if len(value) > 8192 or len(value) < 80:
    VALID_SSH=False
    return False

  value = value.replace("\"", "").replace("'", "").replace("\\\"", "")
  value = value.split(' ')
  types = [ 'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384',
            'ecdsa-sha2-nistp521', 'ssh-rsa', 'ssh-dss', 'ssh-ed25519' ]
  if value[0] not in types:
    VALID_SSH=False
    return False

  try:
    base64.decodebytes(bytes(value[1], "utf-8"))
  except TypeError:
    VALID_SSH=False
    return False
  
  VALID_SSH=True
  return True



def main():
  print("    ▗▀▖      \n▗▖▖ ▐  ▌ ▌▛▀▖\n▘▝▗▖▜▀ ▌ ▌▌ ▌\n  ▝▘▐  ▝▀▘▘ ▘")

  username = input("Welcome to the ~.fun user application form!\n\nWhat is your desired username? [a-z0-9] allowed:\n")
  while (not re.match("[a-z]+[a-z0-9]", username)) or (not check_username(username)):
    username = input("Invalid Username, maybe it exists already?\nValid characters are only a-z and 0-9.\nMake sure your username starts with a character and not a number." \
    "\nWhat is your desired username? [a-z0-9] allowed:\n")


  fullname = input("\nPlease enter your full name:\n")
  while not re.match("\w+\s*\w*", username):
    fullname = input("\nThat is not your real name.\nPlease enter your full name:\n")


  email = input("\nPlease enter your email address:\n")
  while not re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
    email = input("\nThat is not a valid mail address.\nPlease enter your email address:\n")

  
  pubkey = input("\nPlease paste your ssh public key:\n")
  while (not re.match("ssh-(\w)+\s(\w+)(\s*)([a-zA-Z0-9@]*)", pubkey)) or (not validate_pubkey(pubkey)):
    pubkey = input("\nPlease enter a valid public key. You can show it with ssh-keygen -f .ssh/id_rsa -y on your local machine.\nPlease enter your pubkey:\n")
    validate_pubkey(pubkey)

  
  print("\nUsername: {0!s}".format(username))
  print("Full Name: {0!s}".format(fullname))
  print("Email: {0!s}".format(email))
  print("Public {0!s}".format(pubkey))

  
  validation = input("\nIs this information correct? [y/N]")
  while not re.match("[yYnN\n]", validation):
    print("Please answer y for yes or n for no")
    validation = input("Is this information correct? [y/N]")
  if re.match("[yY]", validation):
    print("Thank you for your application! We'll get in touch shortly. 🐧")
    try:
      connection=sqlite3.connect(REG_FILE)
      cursor=connection.cursor()
      __checkSQLite(cursor, connection)
      addtotable(cursor, connection, username, fullname, email, pubkey)
      connection.commit()
      connection.close()
    except:
      logging.exception("Database {0!s} couldnt be accessed or created. Exception:".format(config['DEFAULT']['applications_db']))
      connection.close()
      exit(1)
  pass
  return 0

if __name__ == "__main__":
  try:
    main()
    exit(0)
  except KeyboardInterrupt:
    pass
