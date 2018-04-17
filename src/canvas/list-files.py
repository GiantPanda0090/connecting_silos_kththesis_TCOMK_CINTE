#!/usr/bin/python3
#
# ./list-files.py course_id
#
# outputs a summary of the files in a course
# also outputs an xlsx file of the form: files-course_id.xlsx
#
# 
# G. Q. Maguire Jr.
#
# 2017.06.21
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

# Use Python Pandas to create XLSX files
import pandas as pd

#############################
###### EDIT THIS STUFF ######
#############################

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       access_token=configuration["canvas"]["access_token"]
       baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/courses/"

modules_csv = 'modules.csv' # name of file storing module names
log_file = 'log.txt' # a log file. it will log things
header = {'Authorization' : 'Bearer ' + access_token}
payload = {}


##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################

def write_to_log(message):

       with open(log_file, 'a') as log:
              log.write(message + "\n")
              pprint(message)

def list_files(course_id):
       files_found_thus_far=[]

       # Use the Canvas API to get the list of files for the course
       #GET /api/v1/courses/:course_id/files

       url = baseUrl + '%s/files' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting files: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              files_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of files
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     files_found_thus_far.append(p_response)

       return files_found_thus_far

def list_modules(course_id):
       modules_found_thus_far=[]

       # Use the Canvas API to get the list of modules for the course
       #GET /api/v1/courses/:course_id/modules

       url = baseUrl + '%s/modules' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting assignments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              modules_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     modules_found_thus_far.append(p_response)

       return modules_found_thus_far

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

       if (len(remainder) < 1):
              print("Insuffient arguments\n must provide course_id\n")
       else:
              course_id=remainder[0]
              output=list_files(course_id)

              if (output):
                     if Verbose_Flag:
                            print(output)

                     # the following was inspired by pbreach's answer on Jan 21 '14 at 18:17 in http://stackoverflow.com/questions/21104592/json-to-pandas-dataframe
                     # create a Panda dataframe from the output
                     df=pd.io.json.json_normalize(output)

                     # note that it is necessary to drop the thumbnail_urls as many exceed Excel's URL limit for the length of URLs
                     columns_to_drop=['thumbnail_url']
                     df.drop(columns_to_drop,inplace=True,axis=1)


                     # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
                     # set up the output write
                     writer = pd.ExcelWriter('files-'+str(course_id)+'.xlsx', engine='xlsxwriter')
                     # Convert the dataframe to an XlsxWriter Excel object.
                     df.to_excel(writer, sheet_name='Modules')
                     # Close the Pandas Excel writer and output the Excel file.
                     writer.save()

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

