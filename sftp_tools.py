# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date : 2018-07-18
# @Author : Dan Banker


######################################################################################
# LIBRARIES
######################################################################################

import paramiko
import argparse
import keyring.backend
import base64
from stat import S_ISDIR
import sys
import os
import posixpath
from pathlib import PurePosixPath


######################################################################################
# CLASS
######################################################################################


class SFTPSession:
    def __init__(self, host, username, password=None, rsa_key_path=None, rsa_key_password=None, port=22):

        self.transport = paramiko.Transport((host, port))
        self.transport.start_client(event=None)
        self.transport.get_remote_server_key()

        if rsa_key_path and rsa_key_password:
            self.sftp_key = paramiko.RSAKey.from_private_key_file(rsa_key_path, password=rsa_key_password)
            self.transport.auth_publickey(username, self.sftp_key, event=None)
        elif rsa_key_path:
            self.sftp_key = paramiko.RSAKey.from_private_key_file(rsa_key_path)
            self.transport.auth_publickey(username, self.sftp_key, event=None)
        elif password:
            self.transport.auth_password(username, password, event=None)
        else:
            self.transport.auth_none(username)

        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        self.host = host

    def listdir(self, remote_path='.'):
        if remote_path:
            result = self.sftp.listdir(remote_path)
        else:
            result = self.sftp.listdir()
        return result

    ls = listdir

    def get(self, remote_path, local_path):
        self.sftp.get(remote_path, local_path)
        result = local_path
        return result

    def put(self, local_path, remote_path, new_file_name=None, delete_local=False):
        if new_file_name:
            remote_path = posixpath.join(remote_path, new_file_name)
        else:
            remote_path = posixpath.join(remote_path, os.path.basename(local_path))
        print('SFTP> put {} to {} on {}'.format(local_path, remote_path, self.host))
        result = self.sftp.put(local_path, remote_path, confirm=True)
        if delete_local:
            os.remove(local_path)
        print('SFTP> Result: {}'.format(result))
        return result

    def remove_file(self, remote_path):
        return self.sftp.remove(remote_path)

    def chmod(self, path, mode=None, full=None):
        if full:
            mode = 777
        return self.sftp.chmod(path, mode)

    def move(self, old_remote_path, new_remote_path):
        self.sftp.posix_rename(old_remote_path, new_remote_path)
        result = new_remote_path
        return result

    def close_connection(self):
        return self.sftp.close()

    def isdir(self, remote_path):
        try:
            return S_ISDIR(self.sftp.stat(remote_path).st_mode)
        except IOError:
            # Path does not exist, so by definition not a directory
            return False

    def get_dir_contents(self, remote_path, local_path, archive_dir=None):
        file_list = self.listdir(remote_path)
        results = []
        for item in file_list:
            i = str(PurePosixPath(remote_path, item))
            l = str(PurePosixPath(local_path, item))
            if self.isdir(i) is False:
                result = self.get(i, l)
                results.append(result)
                if archive_dir:
                    a = str(PurePosixPath(archive_dir, item))
                    self.move(i, a)
        return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--listdir', '--ls', dest='listdir', action='store_true')
    parser.add_argument('--get', '--download', dest='get', action='store_true')
    parser.add_argument('--put', dest='put', action='store_true')
    parser.add_argument('--remove_file', '--rm', dest='remove_file', action='store_true')
    parser.add_argument('--chmod', dest='chmod', action='store_true')
    parser.add_argument('--move', '--mv', dest='move', action='store_true')
    parser.add_argument('--get_dir_contents', dest='get_dir_contents', action='store_true')
    parser.add_argument('--host', dest='host', required=True)
    parser.add_argument('--action', dest='action', required=False)
    parser.add_argument('--sftp_keyring_service', '--keyring_service', dest='sftp_keyring_service', required=False)
    parser.add_argument('--sftp_keyring_username', '--keyring_username', dest='sftp_keyring_username', required=False)
    parser.add_argument('--rsa_keyring_service', dest='rsa_keyring_service', required=False)
    parser.add_argument('--rsa_keyring_username', dest='rsa_keyring_username', required=False)
    parser.add_argument('--rsa_key_path', dest='rsa_key_path', required=False)
    parser.add_argument('--rsa_key_password', dest='rsa_key_password', required=False)
    parser.add_argument('--username','--sftp_username', dest='sftp_username', required=False)
    parser.add_argument('--password', '--sftp_password', dest='sftp_password', required=False)
    parser.add_argument('--local_path', dest='local_path', required=False)
    parser.add_argument('--port', dest='port', required=False)
    parser.add_argument('--remote_path', dest='remote_path', required=False)
    parser.add_argument('--mode', dest='mode', required=False)
    parser.add_argument('--full', dest='full', required=False)
    parser.add_argument('--old_remote_path', dest='old_remote_path', required=False)
    parser.add_argument('--new_remote_path', dest='new_remote_path', required=False)
    parser.add_argument('--archive_dir', dest='archive_dir', required=False)
    args = parser.parse_args()

    if args.sftp_keyring_service:
        sftp_password_encoded = keyring.get_password(args.sftp_keyring_service, args.sftp_keyring_username)
        if sftp_password_encoded:
            sftp_password = base64.b64decode(sftp_password_encoded).decode("utf-8")
        else:
            print('ERROR: Cannot find keyring entry')
            sys.exit()
    elif args.sftp_password:
        sftp_password = args.sftp_password
    else:
        sftp_password = None

    if args.rsa_keyring_service:
        rsa_password_encoded = keyring.get_password(args.rsa_keyring_service, args.rsa_keyring_username)
        if rsa_password_encoded:
            rsa_password = base64.b64decode(rsa_password_encoded).decode("utf-8")
        else:
            print('ERROR: Cannot find keyring entry')
            sys.exit()
    elif args.sftp_password:
        rsa_password = args.rsa_password
    else:
        rsa_password = None

    s = SFTPSession(args.host, username=args.sftp_username or 'Anonymous', password=sftp_password, rsa_key_path=args.rsa_key_path, rsa_key_password=rsa_password, port=args.port or 22)

    results = []

    if args.listdir or args.action == 'listdir':
        results.append(s.listdir(args.remote_path or '.'))

    if args.get or args.action == 'get':
        results.append(s.get(args.remote_path, args.local_path))

    if args.put or args.action == 'put':
        results.append(s.put(args.local_path, args.remote_path))

    if args.remove_file or args.action == 'remove_file':
        results.append(s.remove_file(args.remote_path))

    if args.chmod or args.action == 'chmod':
        results.append(s.chmod(args.remote_path))

    if args.move or args.action == 'move':
        results.append(s.move(args.old_remote_path, args.new_remote_path))

    if args.get_dir_contents or args.action == 'get_dir_contents':
        results.append(s.get_dir_contents(args.remote_path, args.local_path, args.archive_dir))

    print(str(results))

if __name__ == "__main__":
    main()
