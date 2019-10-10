#!/bin/bash
cut -d: -f1 /etc/passwd | grep test > deltest.txt
while read name; do 
	userdel "$name"
	rm -rf /home/$name
  if [ "$#" -eq 1 ]; then
    sqlite3 -batch $1 "DELETE FROM applications WHERE username = '$name'"
  fi
done < deltest.txt

rm -f deltest.txt
