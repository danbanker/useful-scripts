#!/usr/bin/python

####################
# Dan Banker
# 2017-10-03
#
# USAGE:
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
parser.add_argument('--filename', dest='filename')
parser.add_argument('--destination', dest='destination')
parser.add_argument('--input_delim', dest='input_delim', default=',')
parser.add_argument('--input_quotechar', action='store_true')
parser.add_argument('--destination_is_dir', action='store_true')
parser.add_argument('--output_ext', dest='output_ext')
parser.add_argument('--delete_original', action='store_true')
parser.add_argument('--header', dest='header')
parser.add_argument('--text_cols', dest='text_cols')
parser.add_argument('--col_width', dest='col_width')
args = parser.parse_args()

print(args.filename)
print(args.destination)
print(args.input_delim)

if args.input_delim == 'tab':
	delim=str(u'\t').encode('utf-8')
else:
	delim=args.input_delim

if args.input_quotechar == True:
	quote_char = '"'
else:
	quote_char = None
	
with open(args.filename, 'rb') as csvfile:
	filereader = csv.reader(csvfile, delimiter=delim, quotechar=quote_char)
	filedata = []
	for row in filereader:
		filedata.append(row)

raw_filedata = list(filedata)

if args.output_ext:
	outfile = os.path.basename(args.filename).split('.')[0]+'.'+args.output_ext
else:	
	outfile = os.path.basename(args.filename)
	
if args.destination_is_dir == True:
	dest_path = os.path.join(args.destination, outfile)
else:
	dest_path = args.destination

try:
	if(os.path.isfile(dest_path) == True):
		print("Deleting old file from converted folder if applicable..")
		os.remove(dest_path)
except OSError:
    pass
	
wb = xlsxwriter.Workbook(dest_path)
ws = wb.add_worksheet("Output")    # your worksheet title here

#import pdb; pdb.set_trace()
	
if args.header:
		header_format = wb.add_format({'bold': True, 'num_format': '@'})
		ws.set_row(0,None,header_format)
		hl = list(args.header.strip().replace(' ','_').split(','))
		ht = tuple([cell.strip('_') for cell in hl])
		header_status = 1
else:
	header_status = 0

for row_counter, row in enumerate(raw_filedata):
	if row_counter == 0 and args.header:
		ws.write_row(row_counter, 0, ht)
	else:
		ws.write_row(row_counter, 0, row)

if args.col_width:
	column_width = int(args.col_width)
else:
	column_width = 20

ws.set_column(0, len(raw_filedata[0])-1, column_width, None)		
		
if args.text_cols:
	text_format = wb.add_format({'num_format': '@'})
	txt_cols = list(eval(args.text_cols))
	
	# assumes that the input starts from column 1 instead of 0
	for col in txt_cols:
		ws.set_column(col-1, col-1, None, text_format)
		
#import pdb; pdb.set_trace()
wb.close()
print("Workbook created!: "+dest_path)

if args.delete_original == True:
	os.remove(args.filename)