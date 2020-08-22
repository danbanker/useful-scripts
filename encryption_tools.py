#!/usr/bin/python

####################
# Dan Banker
# 2019-03-25
#
# USAGE:
#
####################

import argparse
import gnupg
import os
import tempfile
import shutil
import zip_tools_class
import tempfile
# import fs
import gzip
#import sys
#import time
#import datetime
# import glob
# import xlsxwriter
# import csv
# import io


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path', dest='file_path')
    parser.add_argument('--destination_path', dest='destination_path', required=False)
    parser.add_argument('--to_memory', action='store_true')
    parser.add_argument('--key_path', dest='key_path')
    parser.add_argument('--encrypt', action='store_true')
    parser.add_argument('--decrypt', action='store_true')
    parser.add_argument('--delete_original', action='store_true')
    parser.add_argument('--move_original_path', dest='move_original_path', required=False)
    parser.add_argument('--gpg_exe_path', dest='gpg_exe_path', required=False)
    parser.add_argument('--zip', dest='zip', action='store_true', default=False)
    args = parser.parse_args()

    # if args.destination_path and args.encrypt is True and args.to_memory is False:
    #     destination_path = args.destination_path.replace('.' + os.path.split(args.file_path)[1].split('.')[1], '.gpg')
    # elif args.encrypt is True and args.to_memory is False:
    #     destination_path = args.file_path.replace('.' + os.path.split(args.file_path)[1].split('.')[1], '.gpg')
    # elif args.decrypt is True and args.to_memory is False:
    #     destination_path = args.file_path.replace('.' + os.path.split(args.file_path)[1].split('.')[1], '.txt')

    basename = os.path.basename(args.file_path)

    if args.destination_path and args.encrypt is True and args.to_memory is False:
        if args.zip is True:
            destination_path = os.path.join(args.destination_path, basename) + '.zip.gpg'
        else:
            destination_path = os.path.join(args.destination_path, basename) + '.gpg'
    elif args.encrypt is True and args.to_memory is False:
        if args.zip:
            destination_path = args.file_path + '.zip.gpg'
        else:
            destination_path = args.file_path + '.gpg'
    elif args.destination_path and args.decrypt is True and args.to_memory is False:
        destination_path = os.path.join(args.destination_path, basename).replace('.gpg','')
    elif args.decrypt is True and args.to_memory is False:
        destination_path = args.file_path.replace('.gpg','')

    f = encryptionToolsFile(
        file_path=args.file_path,
        gpg_exe_path=args.gpg_exe_path
    )

    if args.encrypt:
        f.encrypt(key_path=args.key_path, destination_path=destination_path, to_memory=args.to_memory, delete_original=args.delete_original, move_original_path=args.move_original_path, zip_file=args.zip)
    elif args.decrypt:
        f.decrypt(key_path=args.key_path, destination_path=destination_path, to_memory=args.to_memory, delete_original=args.delete_original)

class encryptionToolsFile:
    def __init__(self,
                 file_path,
                 gpg_exe_path
                 ):
        self.file_path = file_path

        # home = tempfile.mkdtemp()

        if gpg_exe_path is None:
            self.gpg_exe_path = "D:\\\\Program_Files\\\\GnuPG1.4\\\\gpg.exe"
            self.gnupghome = os.path.dirname(self.gpg_exe_path)
        else:
            self.gpg_exe_path = gpg_exe_path

        print('file_path: ' + str(self.file_path))
        print('gpg_exe_path: ' + str(self.gpg_exe_path))

        self.gpg = gnupg.GPG(binary=self.gpg_exe_path, homedir=self.gnupghome, ignore_homedir_permissions=True, options=['--lock-never'])

    def import_key(self, key):
        with open(key, "rb") as f:
            keys = self.gpg.import_keys(f.read())
        return keys

    def encrypt(self, key_path, destination_path=None, to_memory=False, delete_original=False, move_original_path=None, zip_file=True):
        keys = self.import_key(key_path)

        if destination_path:
            if zip_file is True:
                # dir = fs.open_fs('mem://')
                # dir.makedirs('temp')
                target_dir = os.path.join(os.path.dirname(self.file_path), os.path.basename(self.file_path).replace('.','_'))
                target_file_path = os.path.join(target_dir, os.path.basename(self.file_path))
                try:
                    shutil.rmtree(target_dir)
                except:
                    pass

                os.mkdir(target_dir)
                shutil.move(self.file_path, target_file_path)
                zt = zip_tools_class.ZipTools()
                new_target_path_name  = target_file_path + '.zip'
                zt.zip(zip_path_name=new_target_path_name, file_path_list=[target_file_path])
               # with open(target_file_path, 'rb') as f_in, gzip.open(new_target_path_name, 'wb') as f_out:
                    # shutil.copyfileobj(f_in, f_out)
            else:
                new_target_path_name = self.file_path

            with open(new_target_path_name, "rb") as f:
                self.gpg.create_trustdb()
                result = self.gpg.encrypt(f, keys.fingerprints[0], output=destination_path, always_trust=True, armor=True)
            if not result:
                raise RuntimeError(result.status)
        elif to_memory is True:
            print('to memory variable logic goes here')

        if move_original_path:
            shutil.move(new_target_path_name, move_original_path)

        if delete_original is True:
            os.remove(target_file_path)
        elif move_original_path and new_target_path_name != self.file_path:
            shutil.move(self.file_path, move_original_path)

        print('Encrypted!')

    def decrypt(self, key_path, destination_path=None, to_memory=False, delete_original=False,move_original_path=None):
        keys = self.import_key(key_path)

        if destination_path:
            with open(self.file_path, "rb") as f:
                self.gpg.create_trustdb()
                result = self.gpg.decrypt_file(f, always_trust=True, output=destination_path)
            if not result:
                raise RuntimeError(result.status)
        elif to_memory is True:
            print('to memory variable logic goes here')

        if move_original_path:
            shutil.move(self.file_path, move_original_path)

        if delete_original is True:
            os.remove(self.file_path)

        print('Decrypted!')

if __name__ == "__main__":
    main()
    print('Done!')