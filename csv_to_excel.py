import argparse, csv, xlsxwriter

## FLAT FILE INPUT ##
parser = argparse.ArgumentParser()
parser.add_argument('--input_file', dest='input_file', required=True)
parser.add_argument('--input_delim', dest='input_delim', default=',')

## OUTPUT FILE ##
parser.add_argument('--output_file', dest='output_file', required=True)

## GET ARGUMENTS
args = parser.parse_args()
input_file = args.input_file
input_delim = args.input_delim
output_file = args.output_file

## DISPLAY ARGS ##
print('Input File: '+input_file)
print('Input Delim: '+input_delim)
print('Output File: '+output_file)

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

        #import pdb; pdb.set_trace()
        wb.close()

        print('File Complete.')

def get_csv_data(input_file, input_delim):
        with open(input_file,'r') as csvfile:
                table = csv.reader(input_file, delimiter=input_delim)
                #import pdb; pdb.set_trace()
        return table

if __name__ == "__main__":
    main()
