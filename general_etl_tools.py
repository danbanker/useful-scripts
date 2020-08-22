# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date : 2018-03-03
# @Author : Dan Banker

import re
import os
import csv
import sys
import argparse
import shutil
import glob
from collections import OrderedDict


def copy_file(from_path, to_path):
    from_path = from_path
    to_path = to_path
    print(from_path)
    print(to_path)
    shutil.copyfile(from_path, to_path)
    print('File copied!')


def get_rows_from_file(filename, one_line=False, remove_extra_spaces=False, remove_tabs=False):
    with open(filename, 'r') as f:
        if one_line is True:
            file_data = f.read().replace('\n', '')
        else:
            file_data = f.readlines()
            file_data = [x.strip() for x in file_data]

        if remove_extra_spaces is True:
            if one_line is False:
                new_list = []
                for line in file_data:
                    new_list.append(re.sub(' +', ' ', line))
                file_data = new_list
            else:
                file_data = re.sub(' +', ' ', file_data)

        if remove_tabs is True:
            if one_line is False:
                new_list = []
                for line in file_data:
                    new_list.append(line.replace('\t', ''))
                file_data = new_list
            else:
                file_data = file_data.replace('\t', '')
    # if filename != '../input/logins.dict':
        # import pdb; pdb.set_trace()
    return file_data


def get_credentials(credential_dict_file):
    return eval(get_rows_from_file(credential_dict_file, one_line=True))


def chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def convert_utf_8(file_path):
    targetfilename = file_path + '.tmp'

    try:
        os.remove(targetfilename)
    except OSError:
        pass

    # gets rid of BOM and ensure linux stype line-endings
    with open(file_path, 'rU', encoding='utf-8-sig') as infile, open(targetfilename, 'w', encoding="utf8",
                                                                     newline='\n') as outfile:
        outfile.writelines(infile.readlines())

    os.remove(file_path)
    os.rename(targetfilename, file_path)
    print('File converted to true UTF-8: ' + file_path)


def read_csv(file, delim=',', encap='"'):
    convert_utf_8(file)
    file_data = []
    with open(file, 'r') as csvfile:
        for row in csv.reader(csvfile, delimiter=delim, quotechar=encap):
            file_data.append(row)
    return file_data


def list_to_dict_list(list_data, header_file=None, header_list=None, filter_file=None, filter_list=None, filter_prefix=None):
    # import pdb; pdb.set_trace()
    if header_file:
        # import pdb; pdb.set_trace()
        header_list = eval(get_rows_from_file(
            header_file, one_line=True, remove_extra_spaces=True, remove_tabs=True))
    elif header_list is None:
        print('ERROR: list_to_dict requires either header_file or header_list')
        sys.exit()

    if filter_file:
        filter_list = eval(get_rows_from_file(
            filter_file, one_line=True, remove_extra_spaces=True, remove_tabs=True))

    # import pdb; pdb.set_trace()

    if filter_prefix:
        filter_list = [filter_prefix + x for x in filter_list]

    # import pdb; pdb.set_trace()

    new_list = []
    for row in list_data:
        # print(row)
        new_entry = OrderedDict()
        for col_num, col in enumerate(row):
            col_name = header_list[col_num]
            if filter_list:
                if col_name in filter_list:
                    new_entry[remove_prefix(col_name, filter_prefix)] = col
            else:
                new_entry[col_name] = col
        new_list.append(new_entry)
        # import pdb; pdb.set_trace()
    return new_list


def filter_dict(input_dict, filter_file=None, filter_list=None, filter_prefix=None):
    if filter_file:
        filter_list = eval(get_rows_from_file(
            filter_file, one_line=True, remove_extra_spaces=True, remove_tabs=True))

    if filter_prefix:
        filter_list = [filter_prefix + x for x in filter_list]

    new_filtered_dict = OrderedDict()
    keys = list(input_dict.keys())
    for key in keys:
        if key in filter_list:
            new_filtered_dict[key] = input_dict[key]

    if filter_prefix:
        new_dict = remove_dict_key_prefix(new_filtered_dict, filter_prefix)
    else:
        new_dict = new_filtered_dict

    return new_dict


def remove_dict_key_prefix(prefixed_dict, prefix):
    new_unprefixed_dict = OrderedDict()
    prefixed_dict_keys = list(prefixed_dict.keys())
    for key in prefixed_dict_keys:
        new_unprefixed_dict[remove_prefix(key, prefix)] = prefixed_dict[key]
    return new_unprefixed_dict


# template example zuora_subscribe_template.dict
def dict_list_to_template(dict_list, template_dict_file, string_format=False):
    template_list = get_rows_from_file(template_dict_file, remove_extra_spaces=True, remove_tabs=True)

    new_dict_list = []
    for entry in dict_list:
        keys = list(entry.keys())
        templated_entry = list(template_list)
        for key in keys:
            for e, row in enumerate(templated_entry):
                param = re.search('<(.*)>', row)
                if param:
                    if key == param.group(1):
                        templated_entry[e] = templated_entry[e].replace(param.group(0), entry[key])
        #import pdb; pdb.set_trace()
        new_entry = ''.join(templated_entry)
        if string_format is False:
            new_entry = eval(new_entry)
        new_dict_list.append(new_entry)
    return new_dict_list


def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


#  usage:
#  general_tools.rename_files('D:\\Users\\dbanker\\PycharmProjects\\Repositories\\output', '(.*)(__)(.*\.CSV)', '\g<1>_--CATCHUP--_\g<3>')
def rename_files(path, pattern, replacement):
    for filename in os.listdir(path):
        if re.search(pattern, filename):
            new_filename = re.sub(pattern, replacement, filename)
            new_fullname = os.path.join(path, new_filename)
            old_fullname = os.path.join(path, filename)
            os.rename(old_fullname, new_fullname)
            print('Renamed: ' + old_fullname + ' to ' + new_fullname)


def list_files(path,full_path=False):
    if full_path:
        return [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
    else:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
