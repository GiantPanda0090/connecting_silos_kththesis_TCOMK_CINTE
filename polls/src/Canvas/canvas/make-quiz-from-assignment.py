#!/usr/bin/python3
#
# ./make-quiz-from-assignment.py course_id assignment_to_migrate
#
# Creates a new quiz with the information from a specified assignment
# based upon list-assignments.py
# 
# G. Q. Maguire Jr.
#
# 2017.08.02
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

def create_quiz(course_id, name, description):
       global Verbose_Flag

       #Create a quiz
       # POST /api/v1/courses/:course_id/quizzes
       url = baseUrl + '%s/quizzes' % (course_id)
       if Verbose_Flag:
              print("url: " + url)
       payload={'quiz[title]': name,
                'quiz[description]': description
       }
       r = requests.post(url, headers = header, data=payload)
       if r.status_code == requests.codes.ok:
              page_response=r.json()
              if Verbose_Flag:
                     print("inserted quiz")
              return page_response['id']
       elif r.status_code == 503:
              print("Canvas is unable to process url={}, because the service is unavailable".format(url))
              return 0
       else:
              print("failed to insert quiz for reason: {}".format(r))
              return 0

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
              print("Insuffient arguments\n must provide course_id assignment_to_migrate\n")
       else:
              course_id=remainder[0]
              assignment_to_migrate=remainder[1]

              assignments_in_course=list_assignments(course_id)
              # check that the selected assignment exists in this course
              for a in assignments_in_course:
                     if Verbose_Flag:
                            print("a={}".format(a))
                     if a['id'] == int(assignment_to_migrate):
                            create_quiz(course_id, a['name'], a['description'])

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

