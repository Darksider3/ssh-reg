#!/usr/bin/env python3

import configparser, logging, sqlite3, argparse, pwd
import os
import subprocess

# Clear shell
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# create dictionary out of sqlite results
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
# prints command(but doesnt execute them)
# need this for work, just convenience
def debugExec(commands):
  print("Commands: {!s} -> Returns 0".format(commands))
  return 0


# @TODO hardcoded config?
cwd = os.getcwd() + "/applicationsconfig.ini"
argparser = argparse.ArgumentParser(description = 'interactive registration formular for tilde platforms')
argparser.add_argument('-c', '--config', default = cwd, 
      type = str, help = 'Path to configuration file', required = False)
args = argparser.parse_args()


CONF_FILE = args.config
config = configparser.ConfigParser()
config.read(CONF_FILE)
logging.basicConfig(format="%(asctime)s: %(message)s",
      level = int(config['LOG_LEVEL']['log_level'])
      )
del(cwd)
REG_FILE = config['DEFAULT']['applications_db']

# Does everything related to applicants, i.e. creating, manipulations...
class applicants():
  # User identifier
  identifier = "username"
  # SQLite DB Path
  sourceDB = ""
  # another sqlite to batch-recreate users
  differentDB = ""
  def __init__(self, lident, sourceDB=REG_FILE):
    self.identifier = lident
    self.sourceDB = sourceDB
    self.__connectToDB__("source")
    # all results shall be done with dict_factory! Makes everything so much simpler
    self.sdbCursor.row_factory = dict_factory
  
  def __del__(self):
    self.__closeDB__("source")
    
  def __connectToDB__(self, which):
    if which == "source":
      try:
        self.sdbConnection = sqlite3.connect(self.sourceDB)
        self.sdbCursor = self.sdbConnection.cursor()
      except sqlite3.Error as e:
        logging.exception("Database: Couldn't open database and get cursor: %s" % e)
    else:
      self.ddbConnection = sqlite3.connect(self.differentDB)
      self.ddbCursor = self.ddbConnection.cursor()
      
  def __closeDB__(self, which):
    if(which == "source"):
      try:
        self.sdbConnection.close()
      except sqlite3.Error as e:
        logging.exception("Couldn't close database! Error: %s" % e) # @TODO: Dump full db with query or just the executed querys to file
    else:
      self.ddbConnection.close() # @TODO: Evaluate getting rid of ddb(differentDB)?
  
  # get List of all applications(not accepted yet)
  def getApplicationsList(self):
    query = "SELECT * FROM `applications` WHERE `status` = '0'"
    try:
      self.sdbCursor.execute(query)
      rows = self.sdbCursor.fetchall()
    except sqlite3.Error as e:
      logging.exception("Database Error: %s" % e)
      rows=[]
    return rows
  
  def getApprovedApplicantsList(self):
    query = "SELECT * From `applications` WHERE `status` = '1'"
    try:
      self.sdbCursor.execute(query)
      rows = self.sdbCursor.fetchall()
    except sqlite3.Error as e:
      logging.exception("Database Error: %s" % e)
      rows=[]
    return rows
  
  # edit aproved users
  def editApprovedApplicant(self, term, updaterow):
    try:
      self.sdbCursor.execute(
        "UPDATE `applications` SET ? WHERE id=?",
        ( str(term), )
      )
      self.sdbConnection.commit()
    except sqlite3.Error as e:
      logging.exception("Database Error: %s" % e)
  
  # set user to aproved
  def setApprovedApplication(self, selectterm):
    query = "SELECT `username` FROM `applications` WHERE `username` = `{0!s}`".format(selectterm)
    
  # get applicants data
  def getApplicantsData(self, term):
    # @TODO: Use shorthand if for the correct query, directly into sqlite
    if self.identifier == "id":
      try:
        self.sdbCursor.execute(
          "SELECT * FROM `applications` WHERE id = ?",
          ( str(term), )
        )
      except sqlite3.Error as e:
        logging.exception("Database Error: %s" % e)
        
    else:
      self.sdbCursor.execute(
        "SELECT * FROM `applications` WHERE username = ?",
        ( str(term), )
      )
    result = self.sdbCursor.fetchone()
    return result
    
  # @TODO: migrade just approved users to some new/another sqlitedb
  def migrateApprovedData(self, different_db):
    pass
  
  # @TODO: delete migrated data 
  def deleteMigratedDataSet(self, selectterm):
    pass

  # Applicants whom doesnt got approved should get removed
  def removeApplicant(self, term):
    if self.identifier == "id":
      try:
        self.sdbCursor.execute(
          "DELETE FROM `applications` WHERE id = ?", 
          ( str(term), )
        )
        self.sdbConnection.commit()
      except sqlite3.Error as e:
        logging.exception("Database Error: %s" % e)
        
    else:
      self.sdbCursor.execute(
        "DELETE FROM `applications` WHERE username = ?",
        ( str(term), )
      )
      self.sdbConnection.commit()
    
  #@TODO: Possibility to work without passing users manually
  def selectedUser(userid, username = False):
    pass
  
  # Print out a list of aprovable users
  def printApprovableUsers(self, users):
    i=0
    for user in users:
      print("ID: {0!s}, Status: {0!s}, Name: {0!s}".format(i, user["status"], user["username"]))
      i += 1
    return i
  
  # Get List of users
  def userPrint(self, fetched, userid):
    print("ID: {0!s}".format(fetched[int(userid)]["id"]))
    print("Username: {0!s}".format(fetched[int(userid)]["username"]))
    print("Mail: {0!s}".format(fetched[int(userid)]["email"]))
    print("SSH: {0!s}".format(fetched[int(userid)]["pubkey"]))
    print("Registrated time: {0!s}".format(fetched[int(userid)]["timestamp"]))
  
  # Approve an applicant. Handles everything related, like create home dir, set flags blabla
  def approveApplicant(self, term):
    user = self.getApplicantsData(term)
    ret = self.__execScript(user)
    if ret[0] != 0: # @DEBUG: Change to == 0
      print("Something went wrong in the user creation! Exiting without deleting users record in database!")
      print("Last executed commands: {0!s}\nreturn code: {1!s}".format(ret[-1][1], ret[-1][0]))
      exit(0)
    
    if self.identifier == "id":
      try:
        self.sdbCursor.execute(
          "UPDATE `applications` SET `status`=1 WHERE `id`=?", 
          ( str(term), )
        )
        self.sdbConnection.commit()
      except sqlite3.Error as e:
        logging.exception("Database Error: %s" % e)
    
    else:
      self.sdbCursor.execute(
        "UPDATE `applications` SET `status`=1 WHERE `username`=?"
        ( str(term), )
      )
      self.sdbConnection.commit()
  
  # Script execution, handles everything done with the shell/commands themselves
  def __execScript(self, user):
    # @TODO: omfg just write some wrapper-class/lib... sucks hard! 
    username=user["username"]
    homeDir="/home/"+username+"/"
    sshDir=homeDir+".ssh/"
    executed=[]
    
    executed.append(["useradd", "-m", username])
    rcode = subprocess.call(executed[0])
    if rcode != 0:
      return [rcode,executed,]
    
    executed.append(["usermod", "--lock", username])
    rcode = subprocess.call(executed[1]) #empty pw
    if rcode != 0:
      return [rcode,executed,]
    
    executed.append(["usermod", "-a", "-G", "tilde", username])
    rcode = subprocess.call(executed[2]) # add to usergroup
    if rcode != 0:
      return [rcode,executed,]
    
    executed.append(["mkdir", sshDir])
    try:
      # @TODO: use config variable(chmodPerms)
      ret = os.mkdir(sshDir, 0o777) #create sshdir
      rcode = 0
    except OSError as e:
      logging.exception(e.strerror)
      rcode = e.errno # False, couldn't create.
      return [rcode,executed,]
    
    executed.append(["write(sshkey) to", sshDir+"authorized_keys"])
    with open(sshDir+"authorized_keys", "w") as f:
      f.write(user["pubkey"])
    if f.closed != True:
      logging.exception("Could'nt write to authorized_keys!")
      return [rcode,executed,]
    
    executed.append(["chmod", "-Rv", "700", sshDir])

    try:
      os.chmod(sshDir+"authorized_keys", 0o700) # directory is already 700
      rcode = 0
    except OSError as e:
      logging.exception(e.strerror)
      rcode = e.errno
      return [rcode, executed,]
    
    
    try:
      executed.append(["chown", "-Rv", username+":"+username, sshDir])
      os.chown(sshDir, pwd.getpwnam(username)[2], pwd.getpwnam(username)[3]) #2=>uid, 3=>gid
      executed.append(["chown", "-v", username+":"+username, sshDir+"authorized_keys"])
      os.chown(sshDir+"authorized_keys", pwd.getpwnam(username)[2], pwd.getpwnam(username)[3])
      rcode = 0
    except OSError as e:
      logging.exception(e.strerror) # @TODO: maybe append strerror to executed instead of printing it
      rcode = e.errno
      return [rcode, executed,]
    
    return [rcode,executed,]
    """
{'id': 7, 'username': 'testuser47', 'email': '47test@testmail.com', 'name': 
'test Name', 'pubkey': 'ssh-rsa [...]', 'timestamp': '2018-08-22 13:31:16', 'status': 0}

    """
  

def main():
  # how many times the Seperator/Delimiter?
  delcount = 40
  # The seperator for the menu
  Seperator = "="*delcount
  Menu = Seperator+"\n\t\t Main-Menu:\n\n" \
      "\t 1) list and edit pending users\n"\
      "\t 2) list applicants\n"\
      "\t 3) edit applicant\n"\
      "\t 4) quit\n"+Seperator+"\n"

  # Identify by ID
  applications = applicants(lident = "id")
  while 1 != 0:
    print(Menu)

    command = input("Please select, what you want to do: \n -> ")
    # User shouldnt be able to type something in that isnt a number
    if command.isalpha() or command == '':
      clear()
      print("!!! invalid input, please try again. !!!")
      continue
    
    # convert
    command=int(command)

    if command == 4 or command == "q":
      exit(0)
    # Edit and list pending users/applicants @TODO Wording: Users or applicants?
    elif command == 1:
      users = applications.getApplicationsList()
      i=applications.printApprovableUsers(users)
      
      if i == 0 :
        print("No pending users")
        # giving some time to aknowledge that something WRONG happened
        input("Continue with Keypress...")
        clear()
        continue
      
      usersel = 0
      UserMax = i
      print("Menu:\n r=>return to main")
      
      # Edit Menue
      while 1 != 0 or usersel != "r":
        i = applications.printApprovableUsers(users)
        if usersel == "r":
          break # break when user presses r
        
        usersel = input("Which user( ID ) do you want to change? ->")
        if len(usersel) > 1 or usersel.isalpha():
          usersel = ""
        # convert to int if input isnt an r
        usersel = int(usersel) if usersel != '' and usersel != 'r' else 0
        if usersel > UserMax - 1:
          print("User {0!s} doesn't exist!".format(usersel))
          continue
        # Show the user his chosen user and ask what to do
        applications.userPrint(users, usersel)
        print("You chosed ID No. {0!s}, what do you like to do?".format(usersel))
        
        chosenUser = usersel
        usersel = ""
        
        # Finally down the edit menue!
        while usersel != "e":
          usersel = input("User: {0!s}\n \t\t(A)ctivate \n\t\t(R)emove \n\t\tR(e)turn\n -> ".format(chosenUser))
          if usersel == "A":
            applications.approveApplicant(users[chosenUser]['id'])
            print("User {0!s} has been successfully approved!".format(users[chosenUser]['username']))
            input("waiting for input...")
            clear()
            usersel="e" # remove for being able to continue editing?
            continue
          elif usersel == "R":
            applications.removeApplicant(users[chosenUser]['id'])
            print("User {0!s} successfully deleted!".format(user[chosenUser]['username']))
            input("waiting for input...")
            clear()
            continue
          elif usersel == "e": 
            clear()
            continue
        
    elif int(command) == 2:
      users = applications.getApprovedApplicantsList()
      
      if users == []:
        print("no activate users yet!")
      i=0
      for user in users:
        print("ID: {0!s}, Status: {1!s}, Name: {2!s}".format(user["id"], user["status"], user["username"]))
      continue
    elif command == str(3):
      pass
    else:
      exit(0)

if __name__ == "__main__":
  try:
    main()
    exit(0)
  except KeyboardInterrupt:
    pass
    #print("Exception occured. View log file for details.")
    #logging.exception("Some exception occured")
