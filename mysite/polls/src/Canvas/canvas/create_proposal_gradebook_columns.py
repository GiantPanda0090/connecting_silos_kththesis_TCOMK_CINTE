import csv, requests, time
from pprint import pprint
import optparse
import sys
import json
from io import StringIO, BytesIO
from lxml import html
import json

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       access_token=configuration["canvas"]["access_token"]
       baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/courses/"

modules_csv = 'modules.csv' # name of file storing module names
log_file = 'log.txt' # a log file. it will log things
header = {'Authorization' : 'Bearer ' + access_token}
payload = {}

def insert_column_name(course_id, column_name):
    url = baseUrl + '%s/custom_gradebook_columns' % (course_id)
    print("url: " + url)

    payload={'column[title]': column_name}
    r = requests.post(url, headers = header, data=payload)
    fileName = column_name + ".txt"
    print (fileName)

    with open(fileName ,"w+") as columnData:
        json.dump(r.json(), columnData)

def main():
       global Verbose_Flag
       column_names = ["Epost" , "Title" , "associations" , "keyterms" , "handledare" , "examinator" ]

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

       if (len(remainder) < 1):
              print("Inusffient arguments\n must provide course_id custom_column_name\n")
       else:
           for column in column_names:
               insert_column_name(remainder[0] , column)

       print("\n--DONE--\n\n")

if __name__ == "__main__": main()

