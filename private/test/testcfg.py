test_backup_csv: str = "test/testbackup.csv"
test_db: str = "./test/applications.sqlite"
test_import_csv: str = "test/testimport.csv"
test_import_invalid_csv: str = "test/testimport_fail.csv"
ListUsers_fetch_size_min: int = 3
ListUsers_output_newlines: int = 1

Validator_Valid_Users_Chars_List: list = ["darksider", "dirty", "hAndS", "world312Lol"]
Validator_Invalid_Users_Chars_List: list = ["12", "#uß", "Rawr"]

Validator_Valid_Users_Length: list = ["w💁💁💞💞elt", "hallo", "japp", "eksdee", "harrharr", "räraRüdigerSauß하",
                                      "التَّطْبِيقَاتُ",
                                      "𝓽𝓱𝓮", "𝓵𝓪𝔃𝔂", "𝓭𝓸𝓰"]
Validator_Invalid_Users_Length: list = ["f", "i", "fa", "fo", "ar"]

Validator_Valid_Mail: list = ["larp@example.org", "rawr@lulz.com", "woerld@hassa.fun"]
Validator_Invalid_Mail: list = ["läÄ@wi", "@rawr.", ".com", "@.de", ".@.de"]

Validator_db_user_exists: list = ["darksider3", "Darksider2", "Darksider1"]
Validator_db_user_inexistent: list = ["welt", "world", "hä#", "root"]

# @TODO: More valid and invalid test keys...
Validator_valid_ssh: list = ["""ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC7qmegDxzv1omqG2cWM+
i+qaEGzCoSBwqCeXyGUU93sTqtNYYHJVGj6YZqXeXEGzJtKm2A/uo59Y+WmqhJgW7HcT2Hqvo80NfbIRhqE9TJETyBe
GiiC8qpiYgPC2zigCNvTsRXh0CH5FJ1qy4QEBjztQDWOqSrsoOSJEEWCJiKJizTiXDmlGdiKE409GBo8lvlbMRWbrMj
3iX825WTqy/T0Pio1kqANDotLnPA0sRXUPVyzc/ghzqRHzFetzP9j7C0nh
EvjiJphiuYvhbgix79FrCQG0lXBGcAWzsWUeAoT/d3kQu79+UTWxm+z4pnJ7gkKVMejqrWys560SdAqD264dc5UBRGI9j6X
xVKdraSaEitDneONrSAt2tE/RwRxh2ASxqQfdF88zyDI8/ma608tHc
FROaNsn5hF+/wzjRK9akdhp5WjA5HXhg2OlkwKvSMhGlSgotRj5pr4Ebxjegysy1mEWRFN/vh/oNq4uHQy8adpfogaVELkI/Z2nuAdQk
+uMy6D1hrKhUWubmBPxTbG00IWF25Tyuz8hnFRP9+gB/P
NRlF59/EHy27a72nirvuOyfxKnx/Mn+FD9Ah59OSLhWuo3sN9Im8yc2cliecwMz+DmTtE7TwzNw9v2zfxU9JDQwyLtppULiGpmKFOLHjz
+SVGxSbVsWS//IyNK1GrQ== gschoenb@gschoenb-X220""",
                             """ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAklOUpkDHrfHY17SbrmTIpNLTGK9Tjom/BWDSU
GPl+nafzlHDTYW7hdI4yZ5ew18JH4JW9jbhUFrviQzM7xlELEVf4h9lFX5QVkbPppSwg0cda3
Pbv7kOdJ/MTyBlWXFCR+HAo3FXRitBqxiX1nKhXpHAZsMciLq8V6RjsNAQwdsdMFvSlVK/7XA
t3FaoJoAsncM1Q9x5+3V0Ww68/eIFmb1zuUFljQJKprrX88XypNDvjYNby6vw/Pb0rwert/En
mZ+AW4OZPnTPI89ZPmVMLuayrD2cE86Z/il8b+gw3r3+1nKatmIkjn2so1d01QraTlMqVSsbx
NrRFi9wrf+M7Q== schacon@mylaptop.local"""]
Validator_invalid_ssh: list = ["lol.", "ssh-rsa lol."]

#Y-%m-%d %H:%M:%S
Validator_valid_datetime: list = ["2020-10-07 14:15:30"]

Validator_valid_checkname_names: list = ["HalloWelt"]
Validator_invalid_checkname_names: list = ["\\n", "\n\b"]