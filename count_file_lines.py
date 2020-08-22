# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date : 2018-04-10
# @Author : Dan Banker

import argparse
import general_etl_tools
import gzip
import os

parser = argparse.ArgumentParser()
parser.add_argument('--files', dest='files', required=False)  # Example: --files "test1.txt,test2.txt"
parser.add_argument('--directory', dest='files', required=False)  # Example: --directory "\\home\user"
parser.add_argument('--gzip', dest='gzip', action='store_true')  # add this flag if .gz files should be unzipped when detected
args = parser.parse_args()

if args.files:
    file_list = args.files.split(',')
elif args.directory:
    file_list = general_etl_tools.list_files(os.path.realpath(args.directory))

total_rowcount = 0

for file in file_list:
    file_name, file_ext = os.path.splitext(file)
    if args.gzip is True and file_ext == '.gz':
        with gzip.open(file, 'rb') as f:
            rows = f.read().split(b'\n')
    else:
        rows = general_etl_tools.get_rows_from_file(file)
    file_length = len(rows)
    total_rowcount += file_length
    print('File: %s, Count: %s' % (file, str(file_length)))

print('Total Row Count: %s' % total_rowcount)
