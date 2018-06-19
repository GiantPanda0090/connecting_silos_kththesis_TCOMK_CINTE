#!/usr/bin/python
#
# ./list-assignments.py course_id
#
# outputs a summary of assignment id and name
# also outputs an xlsx file of the form: assignments-course_id.xlsx
# This spreadsheet contains all of the information about each of the assignments (i.e., the assignment itself, but not submissions for this assignment).
# One of the columns is submissions_download_url that can be used to download all of the submissions for an assignment.
#
# based upon insert-column.py
# 
# G. Q. Maguire Jr.
#
# 2016.11.26
# 2017.08.02 updated to add information for each of the assignments
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

import json

# Use Python Pandas to create XLSX files
import pandas as pd

#############################
###### EDIT THIS STUFF ######
#############################

# https://kth.instructure.com/api/v1/courses?
# access_token=8779~eWGDM0sKJajiOdcoQYgh2OSJzCXR0ujYvj9FE5wrKTNMDOc3Nlhhf1aOLAEc7b3E

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       access_token=configuration["canvas"]["access_token"]
       baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/courses/"
      #  pprint(json_data_file)

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

def summarize_assignments(list_of_assignments):
       summary_of_assignments={}
       for assignm in list_of_assignments:
              summary_of_assignments[assignm['id']]=assignm['name']

       print("summary_of_assignments={}".format(summary_of_assignments))

def list_assignments(course_id):
       assignments_found_thus_far=[]

       # Use the Canvas API to get the list of assignments for the course
       #GET /api/v1/courses/:course_id/assignments

       # 1585

       url = baseUrl + '%s/assignments' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting assignments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              assignments_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     assignments_found_thus_far.append(p_response)

       return assignments_found_thus_far


def get_assignment_details(course_id, assignment_id):
       # Use the Canvas API to get a specific assignments for the course
       #GET /api/v1/courses/:course_id/assignments/:id

       url = baseUrl + '%s/assignments/%s' % (course_id, assignment_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting assignment: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return  page_response
       else:
              return None
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
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting custom_gradebook_columns: " + r.text)

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
    payload={'column[title]': column_name}
    r = requests.post(url, headers = header, data=payload)
    write_to_log("result of post creating custom column: " + r.text)
    if r.status_code == requests.codes.ok:
       write_to_log("result of inserting the item into the module: " + r.text)
       if r.status_code == requests.codes.ok:
           page_response=r.json()
           print("inserted column")
           return True
    return False

def creat_assignment_list(course_id,document_type):
       global Verbose_Flag
       Verbose_Flag=False
       remainder =[]
       remainder.append(course_id)
       remainder.append(document_type)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   

       if (len(remainder) < 1):
              print("Insuffient arguments\n must provide course_id\n")
       else:
              course_id=remainder[0]
              output=list_assignments(course_id)
              summarize_assignments(output)
              keyword=''
              print(remainder[1])
              #filter keyword specificatin
              if remainder[1]==0:
                     keyword='Thesis'
              elif remainder[1]==1:
                     keyword='Proposal'
              elif remainder[1] == 2:
                     keyword = 'Beta'
              else:
                     print ("err remainder 1 unavailable value")
              out_list=[]
              if (output):
                     if Verbose_Flag:
                            print(output)
                     for assignement in output:
                            if keyword in assignement['name']:
                                   out_list.append([assignement['id'],assignement['name'],assignement['html_url']])

              return out_list
       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

