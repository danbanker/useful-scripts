#!/usr/bin/python

####################
# DESCRIPTION:
#              Takes a CSV or XLSX file, filters on certain column values, and pastes to a workbook
#              Additionally, can remove specific ranges of data from a workbook
# USAGE:
#
####################

import argparse
from subprocess import call
import sys
import os
import time
import datetime
import shutil
import glob
import xlsxwriter
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--source_file', dest='source_file', required=False)
parser.add_argument('--workbook_file', dest='workbook_file')
parser.add_argument('--input_delim', dest='input_delim', default=',')
parser.add_argument('--input_quotechar', action='store_true')
parser.add_argument('--filters', dest='filters', required=False)
parser.add_argument('--tab_name', dest='tab_name', required=False)
parser.add_argument('--starting_cell', dest='starting_cell', required=False)
args = parser.parse_args()

if args.input_delim == 'tab':
	delim=str(u'\t').encode('utf-8')
else:
	delim=args.input_delim

if args.input_quotechar == True:
	quote_char = '"'
else:
	quote_char = None

def main():
    dataset = get_csv_data(input_file, input_delim)
    write_excel_file(dataset, output_file)
    print('Job Complete!')

def write_excel_file(dataset, output_file):
    wb = xlsxwriter.Workbook(output_file)
    ws = wb.add_worksheet("Output")

    ## WRITE COLUMNS
    ws.write_row(0, 0, dataset['columns'])

    ## WRITE ROWS
    i = 1
    for row in dataset['results']:
        ws.write_row(i, 0, row)
        i += 1

    # import pdb; pdb.set_trace()
    wb.close()

    print('File Complete.')


def get_csv_data(input_file, input_delim):
    with open(input_file, 'r') as csvfile:
        table = csv.reader(input_file, delimiter=input_delim)
    return table


if __name__ == "__main__":
    main()