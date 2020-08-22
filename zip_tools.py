# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date : 2018-08-02
# @Author : Dan Banker

######################################################################################
# LIBRARIES
######################################################################################

import argparse
import zipfile
import bz2
import binascii
import os

######################################################################################
# GLOBALS
#####################################################################################

# parser = argparse.ArgumentParser()
# parser.add_argument('-z','--zip_path', dest='zip_path', nargs='?',default=None)
# parser.add_argument('-d','--dir_path', dest='dir_path', nargs='?',default=None)
# parser.add_argument('-f','--file_path_list', dest='file_path_list', nargs='?', default=None)
# parser.add_argument('-r','--remove_files', dest='remove_files', action='store_true', default=False)
# parser.add_argument('-k','--keep_structure', dest='keep_structure', action='store_true', default=False)
# args = parser.parse_args()
# zip_path = args.zip_path
# dir_path = args.dir_path
# file_path_list = args.file_path_list
# remove_files = args.remove_files
# keep_structure = args.keep_structure

######################################################################################
# FUNCTIONS
######################################################################################


def list_files(path, recursive=False, full_path=False):
    if full_path and recursive is False:
        return [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
    elif recursive is False:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    else:
        [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path)) for f in fn]


def zip(zip_path_name, dir_path=None, file_path_list=None, remove_files=False, keep_structure=False, single_file=False):
    if single_file:
        zip_path_name_new = zip_path_name + '.zip'
        file_path_list = [zip_path_name]
    else:
        zip_path_name_new = zip_path_name

    with zipfile.ZipFile(zip_path_name_new, 'w') as zip_file:
        if dir_path:
            file_path_list = list_files(dir_path, full_path=True)

        for file in file_path_list:
            if keep_structure:
                name_in_zip = None
            else:
                name_in_zip = os.path.basename(file)

            zip_file.write(file, name_in_zip)

    if remove_files:
        for file in file_path_list:
            os.remove(file)

    return {'zip_path': zip_path_name_new, 'file_count': len(file_path_list)}

def unzip(file,destination=None, delete_file=False, to_memory=False):
    zip_ref = zipfile.ZipFile(file, 'r')
    if destination:
        zip_ref.extractall(destination)
        if to_memory is False:
            zip_ref.close()
    if delete_file:
        os.remove(file)
    if to_memory:
        return {name: zip_ref.read(name) for name in zip_ref.namelist()}

######################################################################################
# MAIN
######################################################################################


# def main():
#     print('Creating Zip..')
#     results = zip(zip_path_name=zip_path, dir_path=dir_path, file_path_list=file_path_list, remove_files=remove_files, keep_structure=keep_structure)
#     print(str(results))
#     print('Zip created!')
#     return results
#
#
# if __name__ == "__main__":
#     job_result = main()