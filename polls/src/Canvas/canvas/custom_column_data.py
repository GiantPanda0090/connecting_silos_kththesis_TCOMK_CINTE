#!/usr/bin/python3
#
# ./insert-custom-columns-from-spreadsheet.py  course_id column_name_1 column_name_2 ...
# 
# Inserts a custom column with the indicated name using the data from this column of the spreadsheet
# it will create the column as necessary
#
# G. Q. Maguire Jr.
#
# 2016.11.28
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

# Use Python Pandas to work with XLSX files
import pandas as pd

# to use math.isnan(x) function
import math
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

def lookup_column_number(column_name, list_of_exiting_columns):
       for column in list_of_exiting_columns:
              if Verbose_Flag:
                     print('column: ', column)
              if column['title'] == column_name: 
                     return column['id']
       return -1
       

def add_column_if_necessary(course_id, new_column_name, list_of_exiting_columns):
       column_number=lookup_column_number(new_column_name, list_of_exiting_columns)
       if column_number > 0:
              return column_number
       # otherwise insert the new column
       insert_column_name(course_id, new_column_name)
       return lookup_column_number(new_column_name, list_custom_columns(course_id))


def put_custom_column_entries(course_id, column_number, user_id, data_to_store):
       entries_found_thus_far=[]

       # Use the Canvas API to get the list of custom column entries for a specific column for the course
       #PUT /api/v1/courses/:course_id/custom_gradebook_columns/:id/data/:user_id

       url = baseUrl + '%s/custom_gradebook_columns/%s/data/%s' % (course_id, column_number,user_id)
       if Verbose_Flag:
              print("url: " + url)

       payload={'column_data[content]': data_to_store,}
       r = requests.put(url, headers = header, data=payload)

       if Verbose_Flag:
              write_to_log("result of putting data into custom_gradebook_column: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              entries_found_thus_far.append(p_response)

       return entries_found_thus_far




def list_custom_column_entries(course_id, column_number):
       entries_found_thus_far=[]

       # Use the Canvas API to get the list of custom column entries for a specific column for the course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns/:id/data

       url = baseUrl + '%s/custom_gradebook_columns/%s/data' % (course_id, column_number)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting custom_gradebook_columns: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              entries_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     entries_found_thus_far.append(p_response)

       return entries_found_thus_far




def list_custom_columns(course_id):
       columns_found_thus_far=[]

       # Use the Canvas API to get the list of custom column for this course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns

       url = baseUrl + '%s/custom_gradebook_columns' % (course_id)
       r = requests.get(url, headers = header)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              columns_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     columns_found_thus_far.append(p_response)

       return columns_found_thus_far

def insert_column_name(course_id, column_name):
       global Verbose_Flag

       # Use the Canvas API to Create a custom gradebook column
       # POST /api/v1/courses/:course_id/custom_gradebook_columns
       #   Create a custom gradebook column
       # Request Parameters:
       #Parameter		Type	Description
       #column[title]	Required	string	no description
       #column[position]		integer	The position of the column relative to other custom columns
       #column[hidden]		boolean	Hidden columns are not displayed in the gradebook
       # column[teacher_notes]		boolean	 Set this if the column is created by a teacher. The gradebook only supports one teacher_notes column.

       url = baseUrl + '%s/custom_gradebook_columns' % (course_id)
       if Verbose_Flag:
              print("url: " + url)
       payload={'column[title]': column_name,"column[position]":position}
       r = requests.post(url, headers = header, data=payload)
       if Verbose_Flag:
              write_to_log("result of post creating custom column: " + r.text)
       if r.status_code == requests.codes.ok:
              if Verbose_Flag:
                     write_to_log("result of inserting the item into the module: " + r.text)
              page_response=r.json()
              print("inserted column")
              return True
       return False

def main(course_id, column_number, user_id, value,position_data):
       global Verbose_Flag
       global position
       position=position_data
       Verbose_Flag=False

       parser = optparse.OptionParser()

       parser.add_option('-v', '--verbose',
                         dest="verbose",
                         default=False,
                         action="store_true",
                         help="Print lots of output to stdout"
       )

       remainder=[]
       remainder.append(course_id)
       remainder.append(column_number)
       remainder.append(user_id)
       remainder.append(value)


       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)

       if (len(remainder) < 2):
              print("Inusffient arguments\n must provide course_id column_name_1 column_name_2 ...\n")
              return

       course_id=remainder[0]
       list_of_columns=list_custom_columns(course_id)


       column_name=remainder[1]
       column_number=add_column_if_necessary(course_id, column_name, list_of_columns)
       print('column number: ', column_number)

       put_custom_column_entries(course_id, column_number, remainder[2], remainder[3])

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

