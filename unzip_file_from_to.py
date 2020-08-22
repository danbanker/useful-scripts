# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:14:16 2018

@author: dbanker
"""

import argparse, shutil, zipfile, os

def unzip(source_filename, dest_dir, delete=False):
    zf = zipfile.ZipFile(source_filename)
        #zf.extract(source_filename, member_name, dest_dir)
    zf.extractall(dest_dir)
    zf.close()
    if delete:
        os.remove(source_filename)

parser = argparse.ArgumentParser()
parser.add_argument('--from_path', dest='from_path')
parser.add_argument('--dest_dir', dest='dest_dir')
parser.add_argument('--delete', action='store_true')
args = parser.parse_args()
from_path = args.from_path
dest_dir = args.dest_dir
delete = args.delete
print(from_path)
print(dest_dir)
print(delete)

unzip(from_path, dest_dir, delete)

#shutil.copyfile(from_path, to_path)
print('File extracted!')