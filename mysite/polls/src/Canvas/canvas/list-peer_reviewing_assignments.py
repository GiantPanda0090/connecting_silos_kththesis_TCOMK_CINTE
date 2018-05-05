#!/usr/bin/python3
#
# ./list-peer_reviewing_assignments.py course_id assignment_id
#
# outputs a summary of peer reviewing assignments as an xlsx file of the form: peer_reviewing_assignments-189.xlsx
#
# This spreadsheet contains information about the peer review assignment, user, and a simplified set of assignments
#
# Extensive use is made of Python Pandas merge operations.
# 
# G. Q. Maguire Jr.
#
# 2016.12.02
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

## GET /api/v1/sections/:section_id/assignments/:assignment_id/peer_reviews

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

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              user_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     user_found_thus_far.append(p_response)
       return user_found_thus_far

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
              print("Insuffient arguments\n must provide course_id assignment_id\n")
       else:
              course_id=remainder[0]
              assignment_id=remainder[1]

              users=users_in_course(course_id)
              users_df1=pd.io.json.json_normalize(users)
              sections_df=pd.io.json.json_normalize(sections_in_course(course_id))
              sections_df.rename(columns = {'id':'course_section_id'}, inplace = True)
              columns_to_drop=['course_id', 'end_at', 'integration_id', 'nonxlist_course_id', 'sis_course_id', 'sis_section_id', 'start_at']
              sections_df.drop(columns_to_drop,inplace=True,axis=1)


              output=list_peer_review_assignments(course_id, assignment_id)
              if (output):
                     if Verbose_Flag:
                            print(output)
                     # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
                     # set up the output write
                     writer = pd.ExcelWriter('peer_reviewing_assignments-'+str(course_id)+'-assignment-'+str(assignment_id)+'.xlsx', engine='xlsxwriter')

                     sections_df.to_excel(writer, sheet_name='Sections')

                     # the following was inspired by pbreach's answer on Jan 21 '14 at 18:17 in http://stackoverflow.com/questions/21104592/json-to-pandas-dataframe
                     # create a Panda dataframe from the output
                     df=pd.io.json.json_normalize(output)
                     # Convert the dataframe to an XlsxWriter Excel object.
                     df.to_excel(writer, sheet_name='PeerAssignment')

                     users_df = pd.merge(sections_df, users_df1, on='course_section_id')
                     users_df.to_excel(writer, sheet_name='Users')

                     merge_df = pd.merge(df, users_df, on='user_id')
                     merge_df.to_excel(writer, sheet_name='Merged')

                     # change the user_id into an assessor_id and do another merge
                     assessors_df=users_df.copy(deep=True)
                     columns_to_drop=['course_section_id']
                     assessors_df.drop(columns_to_drop,inplace=True,axis=1)

                     assessors_df.rename(columns = {'user_id':'assessor_id'}, inplace = True)
                     merge2_df = pd.merge(merge_df, assessors_df, on='assessor_id')
                     columns_to_drop=['id', 'created_at_y', 'name_y']
                     merge2_df.drop(columns_to_drop,inplace=True,axis=1)

                     merge2_df.drop_duplicates(inplace=True)
                     merge2_df.to_excel(writer, sheet_name='Merged2')
                     
                     columns_to_drop=['asset_id', 'asset_type', 'id_x',
                                      'associated_user_id_x',
                                      'course_integration_id_x',
                                      'created_at_x',
                                      'end_at_x',
                                      'enrollment_state_x',
                                      'grades.current_grade_x',
                                      'grades.current_score_x',
                                      'grades.final_grade_x',
                                      'grades.final_score_x',
                                      'grades.html_url_x', 'html_url_x',
                                      'id_y', 'last_activity_at_x',
                                      'limit_privileges_to_course_section_x',
                                      'role_x', 'role_id_x',
                                      'root_account_id_x',
                                      'section_integration_id_x',
                                      'sis_account_id_x', 'sis_course_id_x',
                                      'sis_account_id_x', 'sis_course_id_x',
                                      'sis_section_id_x', 'sis_user_id_x',
                                      'start_at_x', 'total_activity_time_x',
                                      'type_x', 'updated_at_x', 'user.id_x',
                                      'associated_user_id_y', 'course_id_y',
                                      'course_integration_id_y',
                                      'end_at_y', 'enrollment_state_y',
                                      'grades.current_grade_y',
                                      'grades.current_score_y',
                                      'grades.final_grade_y',
                                      'grades.final_score_y',
                                      'grades.html_url_y', 'html_url_y',
                                      'last_activity_at_y',
                                      'limit_privileges_to_course_section_y',
                                      'role_y', 'role_id_y',
                                      'root_account_id_y',
                                      'section_integration_id_y',
                                      'sis_account_id_y', 'sis_course_id_y',
                                      'sis_section_id_y', 'sis_user_id_y',
                                      'start_at_y', 'total_activity_time_y',
                                      'type_y', 'updated_at_y',
                                      'user.short_name_x', 'user.sortable_name_x',
                                      'user.short_name_y', 'user.sortable_name_y'

                     ]
                     merge2_df.drop(columns_to_drop,inplace=True,axis=1)
                     
                     old_names = ['course_id_x_x', 'name_x'] 
                     new_names = ['course_id', 'section_name'] 
                     merge2_df.rename(columns=dict(zip(old_names, new_names)), inplace=True)


                     old_names = ['user.id_y', 'user.login_id_y', 'user.name_y'] 
                     new_names = ['user.id_assessor', 'user.login_id_assessor', 'user.name_assessor'] 
                     merge2_df.rename(columns=dict(zip(old_names, new_names)), inplace=True)
                     merge2_df.to_excel(writer, sheet_name='Reviewers')

                     # Close the Pandas Excel writer and output the Excel file.
                     writer.save()

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

