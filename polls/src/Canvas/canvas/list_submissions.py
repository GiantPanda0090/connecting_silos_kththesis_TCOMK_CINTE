#!/usr/bin/python3
#
# ./list_submissions course_id
# also outputs an xlsx file of the form: submissions-course_id.xlsx
#
# based upon insert-column.py
# 
# G. Q. Maguire Jr.
#
# 2016.11.26
#

import csv, requests, time
from pprint import pprint
import optparse
import sys



import os,sys
import time


from io import StringIO, BytesIO

from lxml import html

import json

# Use Python Pandas to create XLSX files
import pandas as pd

#############################
###### EDIT THIS STUFF ######
#############################

# https://kth.instructure.com/api/v1/courses?
#access_token="8779~eWGDM0sKJajiOdcoQYgh2OSJzCXR0ujYvj9FE5wrKTNMDOc3Nlhhf1aOLAEc7b3E"

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
              #pprint(message)

def list_submissions(course_id,assignment_id):
       Verbose_Flag = False

       submissions_found_thus_far=[]


       # Use the Canvas API to get the list of submissions for a course
       #GET /api/v1/courses/:course_id/students/submissions
       # /api/v1/courses/:course_id/assignments/:assignment_id/submissions
       url = baseUrl + '%s/assignments/%s/submissions/' % (course_id,assignment_id)
       if Verbose_Flag:
              print("url: " + url)

       extra_parameters={'student_ids[]': 'all'}
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting submissions: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()
       else:
              return submissions_found_thus_far

       for p_response in page_response:  
              submissions_found_thus_far.append(p_response)
       #print (r.json())

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       #print r
       # while r.links['current']['url'] != r.links['last']['url']:
       #        r = requests.get(r.links['next']['url'], headers=header)
       #        page_response = r.json()
       #        for p_response in page_response:
       #               submissions_found_thus_far.append(p_response)

       return page_response



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

def lunch(course_id,assignment_id):
       remainder=[]
       remainder.append(course_id)
       remainder.append(assignment_id)
       global Verbose_Flag
       Verbose_Flag=False

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       if (len(remainder) < 2):
              print("Insuffient arguments\n must provide course_id abd assignment id\n")
       else:
              course_id=remainder[0]
              assignment_id=remainder[1]
              submission_list=list_submissions(course_id,assignment_id)
              process_list=[]
              Verbose_Flag = True

              for submitted_student in submission_list:
                            user_id = submitted_student['user_id']
                            baseUrl_2 = "https://" + configuration["canvas"]["host"] + "/api/v1/users/"
                            extra_parameters = {'student_ids[]': 'all'}
                            url = baseUrl_2 + '%s/profile' % (user_id)  # GET /api/v1/users/:id
                            r = requests.get(url, params=extra_parameters, headers=header)
                            profil = r.json()
                            username=profil['name']
                            email=profil['login_id']
                            if submitted_student['grader_id'] != None:
                                   url = baseUrl_2 + '%s/profile' % (submitted_student['grader_id'])  # GET /api/v1/users/:id
                                   r = requests.get(url, params=extra_parameters, headers=header)
                                   profil = r.json()
                                   process_list.append([user_id,username,email,1,profil['primary_email']])

                            else:
                                   process_list.append([user_id,username,email,0,0])

              return process_list



              #print ('https://kth.instructure.com/courses/2139/assignments/24565/submissions/11185?download=890332') #FAKE
             # path = os.getcwd()

              #os.system("export PATH=$PATH:" + path + "/../../../ffdriver")
              #os.environ['PATH']=path + "/../../../ffdriver"
              #/home/lqschool/git/Connecting_silo/src/Canvas/canvas/../../../ffdriver
             # print ("export PATH=$PATH:" + path + "/../../../ffdriver")
              #time.sleep(5)
              #r = requests.get(output['submissions_download_url'], allow_redirects=True)
              #payload = {'username': 'qi5',
               #          'password': 'Richard0'}  ##fill in your user name and password
              #url = output['submissions_download_url']
              #url = 'https://kth.instructure.com/courses/2139/assignments/24565/submissions/11185?download=890332'



              # r=requests.Session()
              # get= r.get('https://login.kth.se/login', allow_redirects=True)
              # #print(get)
              # print('\n')
              #
              # post=r.post('https://login.kth.se/login', data=payload, allow_redirects=True)
              # #print(post.text)
              # get = r.post('https://www.kth.se', allow_redirects=True)
              #
              # get = r.post(url,data={'shib_idp_ls_success.shib_idp_session_ss':'true'}, allow_redirects=True)
              #
              # print(get.text)
              #
              # print('\n')
              # print('\n')
              # print('\n')
              #
              # print ("get response:")
              # print('\n')
              #
              # #print(get.text)
              # print('\n')




              # login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
              # login_attempt.submit()







              # if (output):
              #        if Verbose_Flag:
              #               print(output)
              #
              #        # the following was inspired by pbreach's answer on Jan 21 '14 at 18:17 in http://stackoverflow.com/questions/21104592/json-to-pandas-dataframe
              #        # create a Panda dataframe from the output
              #        df=pd.io.json.json_normalize(output)
              #
              #        # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
              #        # set up the output write
              #        writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
              #        # Convert the dataframe to an XlsxWriter Excel object.
              #        df.to_excel(writer, sheet_name='Sheet1')
              #        # Close the Pandas Excel writer and output the Excel file.
              #        writer.save()


