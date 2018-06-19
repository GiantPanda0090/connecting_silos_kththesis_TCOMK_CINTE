#!/usr/bin/python3
#
# ./get_submission_as_file.py course_id assignment_id user_id
#
# based upon list_submissions.py
# 
# G. Q. Maguire Jr.
#
# 2018.05.09
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

#############################
###### EDIT THIS STUFF ######
#############################

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       access_token=configuration["canvas"]["access_token"]
       baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/courses/"
       filebaseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/files/"

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

def get_file(file_id):
       files_found_thus_far=[]

       # Use the Canvas API to get the file
       #GET /api/v1/files/:id 
       url = '{0}{1}'.format(filebaseUrl, file_id)
       if Verbose_Flag:
              print("url: " + url)

       #extra_parameters={'student_ids[]': 'all'}
       #r = requests.get(url, params=extra_parameters, headers = header)
       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting file: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return r.json()
       else:
              return files_found_thus_far

def get_submission(course_id, assignment_id, user_id):
       # Use the Canvas API to get the submission of a uuser for a specifici assignment in a course
       #GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id
       url = '{0}{1}/assignments/{2}/submissions/{3}'.format(baseUrl,course_id, assignment_id, user_id)
       if Verbose_Flag:
              print("url: " + url)

       #extra_parameters={'student_ids[]': 'all'}
       #r = requests.get(url, params=extra_parameters, headers = header)
       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting submission: " + r.text)

       if r.status_code == requests.codes.ok:
              return r.json()
       else:
              return []

def list_submissions(course_id):
       submissions_found_thus_far=[]

       # Use the Canvas API to get the list of submissions for a course
       #GET /api/v1/courses/:course_id/students/submissions
       url = baseUrl + '%s/students/submissions' % (course_id)
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

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     submissions_found_thus_far.append(p_response)

       return submissions_found_thus_far



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

       if (len(remainder) < 1):
              print("Insuffient arguments\n must provide course_id\n")
       else:
              course_id=remainder[0]
              assignment_id=remainder[1]
              user_id=remainder[2]
              output=get_submission(course_id, assignment_id, user_id)
              if (output):
                     if Verbose_Flag:
                            print("output={0}".format(output))
                     attachments=output['attachments']
                     if Verbose_Flag:
                            print('attachments={0}'.format(attachments))

                     for i in attachments:
                            if Verbose_Flag:
                                   print('i={0}'.format(i))
                            url=i['url']
                            file_id=i['id']
                            display_name=i['display_name']
                            if url and url.find("verifier=") > 0:
                                   if Verbose_Flag:
                                          print('url={0}'.format(url))
                                   r = requests.get(url)
                                   if r.status_code == requests.codes.ok:
                                          if Verbose_Flag:
                                                 print('result of getting URL is={0}'.format(r.text))

                                          # write out body of response as a .html page
                                          new_file_name='file_{0}_{1}'.format(file_id, display_name)
                                          with open(new_file_name, 'wb') as f:
                                                 f.write(r.content)
                     print (new_file_name)
                            




if __name__ == "__main__": main()

