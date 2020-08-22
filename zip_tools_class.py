# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date : 2018-08-02
# @Author : Dan Banker

######################################################################################
# LIBRARIES
######################################################################################

import zipfile
import os

######################################################################################
# FUNCTIONS
######################################################################################
class ZipTools:
    def __init__(self):
        print('Zip Tools Initiated.')

    def list_files(self, path, recursive=False, full_path=False):
        if full_path and recursive is False:
            return [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
        elif recursive is False:
            return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        else:
            [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path)) for f in fn]


    def zip(self, zip_path_name, dir_path=None, file_path_list=None, remove_files=False, keep_structure=False):
        with zipfile.ZipFile(zip_path_name, 'w') as zip_file:
            if dir_path:
                file_path_list = self.list_files(dir_path, full_path=True)

            for file in file_path_list:
                if keep_structure:
                    name_in_zip = None
                else:
                    name_in_zip = os.path.basename(file)

                zip_file.write(file, name_in_zip)

        if remove_files:
            for file in file_path_list:
                os.remove(file)

        return {'zip_path': zip_path_name, 'file_count': len(file_path_list)}
