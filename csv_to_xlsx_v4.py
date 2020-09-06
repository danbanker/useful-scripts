#!/usr/bin/python

import argparse
import xlsxwriter
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--csv_file', dest='csv_file', required=False)
parser.add_argument('--xlsx_file', dest='xlsx_file')
parser.add_argument('--delim', dest='delim', default=',')
parser.add_argument('--quotechar', action='store_true')
parser.add_argument('--target_map', dest='target_map', default=[])
args = parser.parse_args()

'''
target_map = [col_name: 'Total Amount', xlsx_tab_name: 'Sales', xlxs_col_location: 'A4', format: {}]

format options:
- integer
- decimal
- text

'''

class csv_to_xlsx:
    def __init__(self, delim):
        if delim == 'tab':
            self.delim = str(u'\t').encode('utf-8')
        else:
            delim = args.input_delim

        if args.input_quotechar == True:
            quote_char = '"'
        else:
            quote_char = None

def main():
    dataset = get_csv_data(source_file, input_delim)
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
    with open(input_file, 'rb') as csvfile:
        table = csv.reader(input_file, delimiter=input_delim)
    return table


if __name__ == "__main__":
    main()