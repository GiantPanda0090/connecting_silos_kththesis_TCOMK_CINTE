#!/usr/bin/python3
#
# ./augument_gradebook.py course_id 29_Dec_13-32_Grades-II2202.csv
#
# reads in a file custom-column-entries-xxx-column-all.xlsx,  where xxx is course_id
# reads in CSV file exported from gradebook
#
# outputs an augmented gradebook for a course as an xlsx file of the form: augmented-gradebook-xxx.xlsx
# adds the columns from the CSV file to the spreadsheet
#
# Extensive use is made of Python Pandas merge operations.
# 
# G. Q. Maguire Jr.
#
# 2016.12.29
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

import json
import xlrd

# Use Python Pandas to create XLSX files
import pandas as pd

#############################
###### EDIT THIS STUFF ######
#############################

log_file = 'log.txt' # a log file. it will log things

##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

def write_to_log(message):

       with open(log_file, 'a') as log:
              log.write(message + "\n")
              pprint(message)



def main():
       global Verbose_Flag

       parser = optparse.OptionParser()

       parser.add_option('-v', '--verbose',
                         dest="verbose",
                         default=False,
                         action="store_true",
                         help="Print lots of output to stdout"
       )

       options, remainder = parser.parse_args()

       Verbose_Flag=options.verbose
       if Verbose_Flag:
              print('ARGV      :', sys.argv[1:])
              print('VERBOSE   :', options.verbose)
              print('REMAINING :', remainder)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   

       if (len(remainder) < 2):
               print("Insuffient arguments\n must provide course_id xxxx.csv\n")
       else:
              course_id=remainder[0]
              csv_file=remainder[1]

              if Verbose_Flag:
                     print('course_id: ', course_id)
                     print('csv_file: ', csv_file)

              # read the sheet of  in custom-column-entries-xxx-column-all.xlsx
              custom_columns_df = pd.read_excel(open('custom-column-entries-'+str(course_id)+'-column-all.xlsx', 'rb'), sheet_name='Custom_Columns')

              # read in the CSV entries from exported gradebook
              gradebook_df=pd.read_csv(csv_file, sep=',')
              gradebook_df.rename(columns = {'ID':'user_id'}, inplace = True)

              augmented_gradebook_df = pd.merge(custom_columns_df, gradebook_df, on='user_id', how='outer')

              # set up the output write
              writer = pd.ExcelWriter('augmented-gradebook-'+str(course_id)+'.xlsx', engine='xlsxwriter')

              augmented_gradebook_df.to_excel(writer, sheet_name='Gradebook')

              # Close the Pandas Excel writer and output the Excel file.
              writer.save()


       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

