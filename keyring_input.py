# must run as _financialcontrols to add to the user's keyring
# arguments should be --username corp\_financialcontrols --service cf_automigration

import getpass
import base64
import keyring.backend
from keyrings.alt.file import PlaintextKeyring
import socket

keyring.set_keyring(PlaintextKeyring())

print('GNOME Keyring Input\n----------------\n')
print('Service: ')
service_id = input()

print('Username: ')
username = input()

pswd = getpass.getpass('Password: ')

pswd_encoded = base64.b64encode(pswd.encode("utf-8")).decode("utf-8")

# save password
keyring.set_password(service_id, username, pswd_encoded)

print('Saved password for %s to GNOME keyring of %s@%s. (AES-128/base64)' % (username,getpass.getuser(), socket.gethostname()))

print('Done')
