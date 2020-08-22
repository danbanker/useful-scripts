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
from distutils.dir_util import copy_tree
import datetime
import calendar
from dateutil.relativedelta import relativedelta
import random

def copy_file(from_path, to_path, dir_contents=False):
    from_path = from_path
    to_path = to_path
    print(from_path)
    print(to_path)
    if dir_contents:
        copy_tree(from_path, to_path)
    else:
        if os.path.isdir(to_path):
            new_to_path = os.path.join(to_path, os.path.basename(from_path))
        else:
            new_to_path = to_path
        shutil.copyfile(from_path, new_to_path)
    print('File copied!')

def move_file(from_path, to_path):
    print(from_path)
    print(to_path)
    shutil.move(from_path, to_path)
    print('File moved!')

def delete_dir_objects(dir, dirs_fully=False, recursive=False):
    for the_file in os.listdir(dir):
        file_path = os.path.join(dir, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                if dirs_fully:
                    shutil.rmtree(file_path)
                elif recursive:
                    delete_dir_objects(file_path, recursive=True)
        except Exception as e:
            print(e)

def move_all_dir_files(from_path, to_path, keep_dirs=False):
    copy_file(from_path, to_path, dir_contents=True)
    if keep_dirs:
        dirs_fully = False
        recursive = True
    else:
        dirs_fully = True
        recursive = False
    delete_dir_objects(from_path, dirs_fully=dirs_fully, recursive=recursive)

def get_rows_from_file(filename, one_line=False, remove_extra_spaces=False, remove_tabs=False, binary=False, start_from_line=None, remove_blank_lines=False, remove_nulls=False):
    if binary:
        read_type = 'rb'
    else:
        read_type = 'r'

    with open(filename, read_type) as f:
        if one_line is True:
            file_data = f.read().replace('\n', '')
        else:
            file_data = f.readlines()
            file_data = [x.strip() for x in file_data]

        if start_from_line:
            file_date = file_data[start_from_line-1:]

        if remove_extra_spaces is True:
            if one_line is False:
                new_list = []
                for line in file_data:
                    new_list.append(re.sub(' +', ' ', line))
                file_data = new_list
            else:
                file_data = re.sub(' +', ' ', file_data)

        if remove_nulls is True:
            new_list = []
            for line in file_data:
                new_list.append(line.replace('\x00',''))
            file_data = new_list

        if remove_blank_lines is True:
            new_list = []
            for line in file_data:
                if len(line.strip()) != 0:
                    new_list.append(line)
            file_data = new_list

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


def get_dict_from_file(dict_file):
    return eval(get_rows_from_file(dict_file, one_line=True))


def chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def convert_utf_8(file_path):
    targetfilename = file_path + '.tmp'

    try:
        os.remove(targetfilename)
    except OSError:
        pass

    # gets rid of BOM and ensure linux stype line-endings
    with open(file_path, 'rU', encoding='utf-8-sig', errors='ignore') as infile, open(targetfilename, 'w', encoding="utf8",
                                                                     newline='\n') as outfile:
        outfile.writelines(infile.readlines())

    os.remove(file_path)
    os.rename(targetfilename, file_path)
    print('File converted to true UTF-8: ' + file_path)


def read_csv(file, delim=',', encap='"', remove_header_row=False, top_row_is_header=False, single_list=False, remove_blank_lines=False):
    convert_utf_8(file)
    file_data = []
    with open(file, 'r') as csvfile:
        for r, row in enumerate(csv.reader(csvfile, delimiter=delim, quotechar=encap, skipinitialspace=True)):
            if remove_header_row is True and r == 0:
                pass
            elif remove_blank_lines:
                if any(field.strip() for field in row):
                    file_data.append(row)
            else:
                file_data.append(row)
    if top_row_is_header:
        f_data = list_to_dict_list(file_data[1:],header_list=file_data[0])
    else:
        f_data = file_data

    new_list = []
    if single_list:
        for row in f_data:
            for val in row:
                new_list.append(val)

        old_f_data = list(f_data)
        f_data = list(new_list)

    return f_data

def check_dict_for_key_match(input_dict, input_key_list):
    for col in input_key_list:
        dict_valid = True
        if col not in input_dict.keys():
            print(str(col) + ' not in input file.')
            dict_valid = False
            break

    return dict_valid

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

#def filter_dict_list_values():

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
                param = re.search('<([^<|>]*)>', row)
                if param:
                    if key == param.group(1):
                        templated_entry[e] = templated_entry[e].replace(param.group(0), entry[key])
        # import pdb; pdb.set_trace()
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


def capitalize_keys(d):
    result = {k.upper(): v for k, v in d.items()}
    return result


def alpha_only(input_string):
    return ' '.join(e for e in input_string if e.isalnum())

def remove_special_characters(input_string):
    return re.sub('[^A-Za-z0-9,\-@\._]+', ' ', input_string)

def create_dir(directory, replace=False):
    if replace:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    try:
        if os.path.exists(directory) is False:
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

# col_list also forces the order of the columns
def dict_list_to_file(dict_list, file_name, col_list=None, supress_col_list=None, headers=False,
                      quote_all=None, quote_minimal=None, quote_nonnumeric=None, delimiter=',', lineterminator='\n'):

    if quote_all:
        quoting = csv.QUOTE_ALL
    elif quote_minimal:
        quoting = csv.QUOTE_MINIMAL
    elif quote_nonnumeric:
        quoting = csv.QUOTE_NONNUMERIC
    else:
        quoting = csv.QUOTE_NONE

    f = open(file_name, 'w')

    if col_list and supress_col_list is False:
        keys = col_list
        new_dict_list = []
        for row in dict_list:
            new_dict = {}
            for col in col_list:
                new_dict[col] = row[col]
            new_dict_list.append(new_dict)
    elif supress_col_list:
        valid_keys = []
        for key in list(dict_list[0].keys()):
            if key not in supress_col_list:
                valid_keys.append(key)
        new_dict_list = []
        for row in dict_list:
            new_dict = {}
            for col in valid_keys:
                new_dict[col] = row[col]
            new_dict_list.append(new_dict)
        keys = list(new_dict_list[0].keys())
    else:
        keys = list(dict_list[0].keys())
        new_dict_list = dict_list.copy()

    writer = csv.DictWriter(f, delimiter=delimiter, fieldnames=keys, quoting=quoting, lineterminator=lineterminator)

    if headers:
        writer.writeheader()

    writer.writerows(new_dict_list)
    f.close()
    r = str(len(dict_list))
    return {'file_name': file_name, 'rows': r}


def list_files(path,full_path=False):
    if full_path:
        return [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
    else:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

# returns list of tuples with min and max applicable start dates per each year
def segment_range_by(startdate, enddate, segment_range=None):
   start_date = datetime.datetime.strptime(startdate,'%Y-%m-%d').date()
   end_date = datetime.datetime.strptime(enddate,'%Y-%m-%d').date()

   if segment_range == 'years':
       date_ranges = [(
           datetime.date(year, 1, 1).strftime('%Y-%m-%d'),
           datetime.date(year, 12, 31).strftime('%Y-%m-%d')
           ) for year in range(start_date.year, end_date.year+1) ]

       if len(date_ranges) > 1:
           date_ranges[0] = (startdate, date_ranges[0][1])
           if startdate != enddate:
               date_ranges[-1] = (date_ranges[-1][0], enddate)
       else:
           date_ranges = (startdate, enddate)

   elif segment_range == 'months':
       date_ranges = []
       for year in range(start_date.year, end_date.year + 1):
           if year == start_date.year:
               s = start_date.month
           else:
               s = 1

           if year == end_date.year:
               e = end_date.month
           else:
               e = 12

           for month in range(s, e + 1, 1):
               if year == start_date.year and month == start_date.month:
                   start_day = start_date.day
               else:
                   start_day = 1

               if year == end_date.year and month == end_date.month:
                   end_day = end_date.day
               else:
                   end_day = calendar.monthrange(year=year, month=month)[1]

               s = datetime.date(year, month, start_day).strftime('%Y-%m-%d')
               e = datetime.date(year, month, end_day).strftime('%Y-%m-%d')
               date_ranges.append([s, e])

   return date_ranges

def inttohex(number, digits):
    # there must be at least one character:
    fullhex = 16**(digits - 1)*6
    assert number < fullhex
    partialnumber, remainder = divmod(number, digits*6)
    charposition, charindex = divmod(remainder, digits)
    char = ['a', 'b', 'c', 'd', 'e', 'f'][charposition]
    hexconversion = list("{0:0{1}x}".format(partialnumber, digits-1))
    hexconversion.insert(charposition, char)

    return ''.join(hexconversion)

def random_hex(length=6):
    return inttohex(random.randint(0, length*16**(digits-1)), digits)