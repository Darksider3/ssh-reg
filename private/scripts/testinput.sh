#!/usr/bin/expect
expr {srand([clock seconds])}    ;# initialize RNG
set username "testuser"
set mail "test@testmail.com"
set name "test Name"
set sshkey "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7Tob2HvgKL5yns9BQpb/EJENR3UurMdhM9oc7tQ/USw/nIiisRDp4qmwqZM3kyl1RfkGoSiEALCogM693jl/2RO2MFLW/Da9WFuXwBmV4wMbQZQiZJCvqyMBW7uPHgfCXJ2E8T707Ixwv9S9gtmwgAqg/+x12C0fF7P45MpO3Mvc+6ZPdP5qg/GCaej67KHqfVTb4/OMrvHkRTlETFYVNj4B/uwuA7NxTi8YkCSKH+BGCLYDl95uISrHOxaKbeDb6OgkgdYS9ygg2F7r3S36n8woLdSXqJNpxx2zLgO8Ow9KE0paezyeQqPPjbYu6l8y2IAkKCWTHKTAQ6DFgcvAD darksider3@prism"
set y "y"
set random "[expr {int(rand() * 1000)}]"
spawn ./userapplication.py

expect "allowed:"
send "$username$random\r"
expect "full name:"
send "$name\r"
expect "email address:"
send "$random$mail\r"
expect "ssh public key:"
send "$sshkey\r"
expect "correct?*"
send "$y\r"
interact

spawn ./administrate.py

expect -glob "*-> "
send "1\r"
expect -glob  "*->"
send "\r"
expect -glob  "*-> "
send "A\r"
expect -glob  "*..."
send "\r"
expect -glob "*-> "
send "4\r"
interact
