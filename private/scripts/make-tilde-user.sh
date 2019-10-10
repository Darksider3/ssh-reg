#!/bin/env bash
USERNAME=$1
REALNAME=$2
EMAIL=$3
PUBKEY=$4

adduser $USERNAME

# empty password
usermod --lock $USERNAME

# add to tilde group
usermod -a -G tilde $USERNAME

# paste ssh key
mkdir /home/$USERNAME/.ssh
echo $PUBKEY >/home/$USERNAME/.ssh/authorized_keys

# fix perms
chmod -Rv 700 /home/$USERNAME/.ssh/
chown -Rv $USERNAME:$USERNAME /home/$USERNAME/.ssh/
echo "user created."
return 0
