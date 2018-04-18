#!/usr/bin/python3
#
# ./list_users_in_course_with_students_email.py course_id
#
# outputs a list of users in a course as an xlsx file of the form: users-in-189.xlsx
# the second sheet "Students" lists students together with their e-mail address
#
# Based on list_users_in_course.py
#
# Extensive use is made of Python Pandas merge operations.
# 
# G. Q. Maguire Jr.
#
# 2017.01.09
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
       baseUrlUsers="https://"+configuration["canvas"]["host"]+"/api/v1/users/"

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


def list_peer_review_assignments(course_id, assignment_id):
       peer_review_assignments_found_thus_far=[]

       # Use the Canvas API to get the list of peer reviewing assignments
       # a given assignment for a course:
       #GET /api/v1/courses/:course_id/assignments/:assignment_id/peer_reviews
       
       url = baseUrl + '%s/assignments/%s/peer_reviews' % (course_id, assignment_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting peer review assignments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              peer_review_assignments_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            peer_review_assignments_found_thus_far.append(p_response)

       return peer_review_assignments_found_thus_far

def sections_in_course(course_id):
       sections_found_thus_far=[]
       # Use the Canvas API to get the list of sections for this course
       #GET /api/v1/courses/:course_id/sections

       url = baseUrl + '%s/sections' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting sections: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              sections_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     sections_found_thus_far.append(p_response)

       return sections_found_thus_far



def summarize_assignments(list_of_assignments):
       summary_of_assignments={}
       for assignm in list_of_assignments:
              summary_of_assignments[assignm['id']]=assignm['name']

       print("summary_of_assignments={}".format(summary_of_assignments))

def list_assignments(course_id):
       assignments_found_thus_far=[]

       # Use the Canvas API to get the list of assignments for the course
       #GET /api/v1/courses/:course_id/assignments

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

def users_in_course(course_id):
       user_found_thus_far=[]

       # Use the Canvas API to get the list of users enrolled in this course
       #GET /api/v1/courses/:course_id/enrollments

       url = baseUrl + '%s/enrollments' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       extra_parameters={'enrollment_type[]': 'student', 'include[]': 'email'}
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              user_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            user_found_thus_far.append(p_response)
       return user_found_thus_far

def students_in_course2(course_id):
       user_found_thus_far=[]

       # Use the Canvas API to get the list of users enrolled in this course
       #GET /api/v1/courses/:course_id/users

       url = baseUrl + '%s/users' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       extra_parameters={'enrollment_type[]': 'student', 'include[]': 'email'}
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              user_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            user_found_thus_far.append(p_response)
       return user_found_thus_far

def users_communication_channel(user_id):
       page_response=[]
       # Use the Canvas API to get the user's communication channel(s)
       #GET /api/v1/users/:user_id/communication_channels

       url = baseUrlUsers + '%s/communication_channels' % (user_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting communication_channels: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       return page_response

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

              users=users_in_course(course_id)
              users_df=pd.io.json.json_normalize(users)

              for index, row in  users_df.iterrows():
                     if Verbose_Flag:
                            print('index: ', index, 'row[user_id]: ', row['user_id'])
                                
                     #"address":"chip.maguire@gmail.com","type":"email"}]
                     comm_channel=users_communication_channel(row['user_id'])
                     if Verbose_Flag:
                            print('comm channels: ', len(comm_channel))

                     for commchannel in comm_channel:
                            if Verbose_Flag:
                                   print('commchannel: ', commchannel)
                                   print('commchannel[position]: ', commchannel['position'])
                                   print('commchannel[address]: ', commchannel['address'])
                                   print('commchannel[type]: ', commchannel['type'])
                                   print('commchannel[workflow_state]: ', commchannel['workflow_state'])
                            users_df.set_value(index, 'comm_channel_address'+str(commchannel['position']), commchannel['address'])
                            users_df.set_value(index, 'comm_channel_type'+str(commchannel['position']), commchannel['type'])
                            users_df.set_value(index, 'comm_channel_workflow_state'+str(commchannel['position']), commchannel['workflow_state'])

              students=students_in_course2(course_id)
              students_df=pd.io.json.json_normalize(students)

              students_df['comm_channel_address']=""
              students_df['comm_channel_type']=""

              for index, row in  students_df.iterrows():
                     if Verbose_Flag:
                            print('index: ', index, 'row[id]: ', row['id'])
                                
                     #"address":"chip.maguire@gmail.com","type":"email"}]
                     comm_channel=users_communication_channel(row['id'])
                     for commchannel in comm_channel:
                            if Verbose_Flag:
                                   print('commchannel: ', commchannel)
                                   print('commchannel[position]: ', commchannel['position'])
                                   print('commchannel[address]: ', commchannel['address'])
                                   print('commchannel[type]: ', commchannel['type'])
                                   print('commchannel[workflow_state]: ', commchannel['workflow_state'])
                            students_df.set_value(index, 'comm_channel_address'+str(commchannel['position']), commchannel['address'])
                            students_df.set_value(index, 'comm_channel_type'+str(commchannel['position']), commchannel['type'])
                            students_df.set_value(index, 'comm_channel_workflow_state'+str(commchannel['position']), commchannel['workflow_state'])

              if Verbose_Flag:
                     print(users)
              # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
              # set up the output write
              writer = pd.ExcelWriter('users-in-'+str(course_id)+'.xlsx', engine='xlsxwriter')

              users_df.to_excel(writer, sheet_name='Users')
              students_df.to_excel(writer, sheet_name='Students')

              # Close the Pandas Excel writer and output the Excel file.
              writer.save()

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

