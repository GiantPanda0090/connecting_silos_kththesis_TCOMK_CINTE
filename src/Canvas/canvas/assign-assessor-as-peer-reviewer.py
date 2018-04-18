#!/usr/bin/python3
#
# ./assign-assessor-as-peer-reviewer.py course_id assignment_id assessor_id user_id
#
# This program assigns the user with the assessor_id to review the submisison of the user (user_id) to be reviewed
# for the course with the course_id and for the specific assignment with the assignment_id
#
# This means that we have to look up which submission_id is associated with this this user_id.
#
# Example:
#  ./assign-assessor-as-peer-reviewer.py 189 314 1283 3365
# 'Sat Dec 10 16:32:54 2016'
# ('result of post assigning peer reviwer: '
#  '{"id":2845,"user_id":3365,"asset_id":11059,"asset_type":"Submission","workflow_state":"assigned","assessor_id":1283}')
# assigned reviewer
# 'Sat Dec 10 16:32:56 2016'
# '\n--DONE--\n\n'
# 
#
# G. Q. Maguire Jr.
#
# 2016.12.10
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

def submission_for_assignment_by_user(course_id, assignment_id, user_id):
       # return the submission information for a single user's assignment for a specific course as a dict
       #
       # Use the Canvas API to get a user's submission for a course for a specific assignment
       # GET /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id
       url = baseUrl + '%s/assignments/%s/submissions/%s' % (course_id, assignment_id, user_id)
       if Verbose_Flag:
              print("url: " + url)

       #extra_parameters={'student_ids[]': 'all'}
       #r = requests.get(url, params=extra_parameters, headers = header)
       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting submissions: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              if Verbose_Flag:
                     print("page_response: " + str(page_response))
              return page_response
       else:
              return dict()

def assign_peer_reviewer(course_id, assignment_id, user_id, submission_id):
    global Verbose_Flag

    # Use the Canvas API 
    #POST /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:submission_id/peer_reviews
    # Request Parameters:
    #Parameter		Type	Description
    # user_id	Required	integer	 user_id to assign as reviewer on this assignment
    #
    # from https://github.com/matematikk-mooc/frontend/blob/master/src/js/api/api.js
    # createPeerReview: function(courseID, assignmentID, submissionID, userID, callback, error) {
    #       this._post({
    #              "callback": callback,
    #              "error":    error,
    #              "uri":      "/courses/" + courseID + "/assignments/" + assignmentID + "/submissions/" + submissionID + "/peer_reviews",
    #              "params":   { user_id: userID }
    #       });
    #    },
   
    url = baseUrl + '%s/assignments/%s/submissions/%s/peer_reviews' % (course_id, assignment_id, submission_id)

    if Verbose_Flag:
       print("url: " + url)

    payload={'user_id': user_id}

    r = requests.post(url, headers = header, data=payload)
    if Verbose_Flag:
           write_to_log("result of post assigning peer reviwer: " + r.text)
    if r.status_code == requests.codes.ok:
       write_to_log("result of post assigning peer reviwer: " + r.text)
       if r.status_code == requests.codes.ok:
           page_response=r.json()
           print("assigned reviewer")
           return True
    return False

def assign_assessor_as_peer_reviewer(course_id, assignment_id, assessor_id, user_id):
       submission=submission_for_assignment_by_user(course_id, assignment_id, user_id)
       if Verbose_Flag:
              print("submission: " + str(submission))

       if Verbose_Flag:
              print("user_id: " + str(submission['user_id']))

       if submission['user_id'] == int(user_id):
              if Verbose_Flag:
                     print("matching submission: " + str(submission))
              output=assign_peer_reviewer(course_id, assignment_id, assessor_id, submission['id'])
              return output
       return "no match found"

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

       if (len(remainder) < 4):
              print("Insuffient arguments\n must provide course_id assignment_id assessor_id user_id\n")
       else:
              course_id=remainder[0]
              assignment_id=remainder[1]
              assessor_id=remainder[2]
              user_id=remainder[3]

              output=assign_assessor_as_peer_reviewer(course_id, assignment_id, assessor_id, user_id)
              if (output):
                     if Verbose_Flag:
                            print(output)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

