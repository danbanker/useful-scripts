# must add .local/share/python_keyring/keyringrc.cfg
# [backend]
# default-keyring=keyrings.alt.file.PlaintextKeyring

import getpass
import base64
import keyring.backend
from keyrings.alt.file import PlaintextKeyring
import argparse
import socket

keyring.set_keyring(PlaintextKeyring())

parser = argparse.ArgumentParser()
parser.add_argument('--username', dest='username')
parser.add_argument('--service', dest='service', default=None)
args = parser.parse_args()

username = args.username

# the service is just a namespace for your app
if args.service:
    service_id = args.service
else:
    service_id = username

# print('Username: ' + username + '\n\n')
pswd = getpass.getpass('GNOME Keyring Input\n----------------\nUsername: ' + username + '\nPassword: ')

pswd_encoded = base64.b64encode(pswd.encode("utf-8")).decode("utf-8")

# save password
keyring.set_password(service_id, username, pswd_encoded)

print('Saved password for %s to GNOME keyring of %s@%s. (AES-128/base64)' % (username,getpass.getuser(), socket.gethostname()))

# decode example
# password_encoded = keyring.get_password(service_id, username)
# password_decoded = base64.b64decode(password_encoded).decode("utf-8")

print('Done')

