#!/usr/bin/python3
#
# ./insert_formula_questions.py course_id [quiz_id]
#
# inserts a calculated_question into a quiz for the indicated course.
#
# G. Q. Maguire Jr.
#
# 2017.06.19
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

#from io import StringIO, BytesIO

import json

# for regular expression processing
import re

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

def list_quizzes(course_id):
       global Verbose_Flag

       quizzes_found_thus_far=[]

       #List quizzes in a course
       # GET /api/v1/courses/:course_id/quizzes
       url = baseUrl + '%s/quizzes' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting quizzes: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              quizzes_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     quizzes_found_thus_far.append(p_response)

       return quizzes_found_thus_far

def create_quiz(course_id, name):
       global Verbose_Flag

       #Create a quiz
       # POST /api/v1/courses/:course_id/quizzes
       url = baseUrl + '%s/quizzes' % (course_id)
       if Verbose_Flag:
              print("url: " + url)
       payload={'quiz[title]': name}
       r = requests.post(url, headers = header, data=payload)
       write_to_log("result of post creating quiz: " + r.text)
       if r.status_code == requests.codes.ok:
              write_to_log("result of creating quiz in the course: " + r.text)
              page_response=r.json()
              print("inserted quiz")
              return page_response['id']
       return 0

def create_quiz_question(course_id, quiz_id, question):
       global Verbose_Flag

       global quiz_question_groups
       print("in create_quiz_question")

       question_category=question['question_category']
       print("question_category={}".format(question_category))
       quiz_group_id=quiz_question_groups.get(question_category)
       # if the group already exists for this category, then use the quiz_group_id, else create the quesiton group
       if quiz_group_id is None:
              quiz_group_id=create_quiz_question_group(course_id, quiz_id, question_category, question)

       print("quiz_group_id={}".format(quiz_group_id))



       # Create a single quiz question - Create a new quiz question for this quiz
       # POST /api/v1/courses/:course_id/quizzes/:quiz_id/questions
       url = baseUrl + '%s/quizzes/%s/questions' % (course_id, quiz_id)

       if Verbose_Flag:
              print("url: " + url)
       payload={'question':
                {
                       'question_name': question['question_name'],
                       'points_possible': question['points_possible'],
                       'question_type': question['question_type'],
                       'question_text': question['question_text'],
                }
       }
       
       ans=question.get('answers')
       if ans:
              payload['question']['answers']= ans

       gid=question.get('quiz_group_id')
       if gid:
              payload['question']['quiz_group_id']= gid

       v=question.get('variables')
       if v:
              payload['question']['variables']= v

       f=question.get('formulas')
       if f:
              payload['question']['formulas']= f

       tol=question.get('answer_tolerance')
       if tol:
              payload['question']['answer_tolerance']= tol


       digs=question.get('formula_decimal_places')
       if digs:
              payload['question']['formula_decimal_places']= digs


       #if question.get('correct_comments'):
       #       payload.update({'question[correct_comments]': question['correct_comments']})
       #if question.get('incorrect_comments'):
       #       payload.update({'question[incorrect_comments]': question['incorrect_comments']})
       #if question.get('neutral_comments'):
       #       payload.update({'question[neutral_comments]': question['neutral_comments']})
       #if question.get('text_after_answers'):
       #       payload.update({'question[text_after_answers]': question['text_after_answers']})

       print("payload={}".format(payload))
       r = requests.post(url, headers = header, json=payload)

       write_to_log("result of post creating question: " + r.text)
       if r.status_code == requests.codes.ok:
              write_to_log("result of creating question in the course: " + r.text)
              page_response=r.json()
              print("inserted question")
              return page_response['id']
       return 0



def create_quiz_question_group(course_id, quiz_id, question_group_name, question):
       # return the quiz_group_id

       global Verbose_Flag

       # quiz_groups will be a dictionary of question_category and corresponding quiz_group_id
       # we learn the quiz_group_id when we put the first question into the question group
       global quiz_question_groups

       print("course_id={0}, quiz_id={1}, question_group_name={2}".format(course_id, quiz_id, question_group_name))

       quiz_group_id=quiz_question_groups.get(question_group_name)
       # if the group already exists for this category, then simply return the quiz_group_id
       if quiz_group_id is not None:
              return quiz_group_id

       # Create a question group
       # POST /api/v1/courses/:course_id/quizzes/:quiz_id/groups
       url = baseUrl + '%s/quizzes/%s/groups' % (course_id, quiz_id)

       if Verbose_Flag:
              print("url: " + url)
       payload={'quiz_groups':
                [
                {
                       'name': question_group_name,
                       'pick_count': 1,
                       'question_points': question['points_possible']
                       #'question_points': question['points_possible']
                }
                ]
       }

       print("payload={}".format(payload))
       r = requests.post(url, headers = header, json=payload)

       write_to_log("result of post creating question group: " + r.text)
       print("r.status_code={}".format(r.status_code))
       if (r.status_code == requests.codes.ok) or (r.status_code == 201):
              write_to_log("result of creating question group in the course: " + r.text)
              page_response=r.json()
              if Verbose_Flag:
                     print("page_response={}".format(page_response))
              # store the new id in the dictionary
              if Verbose_Flag:
                     print("inserted question group={}".format(question_group_name))
              # '{"quiz_groups":[{"id":541,"quiz_id":2280,"name":"Newgroup","pick_count":1,"question_points":1.0,"position":2,"assessment_question_bank_id":null}]}')
              quiz_group_id=page_response['quiz_groups'][0]['id']
              quiz_question_groups[question_group_name]=quiz_group_id
              if Verbose_Flag:
                     print("quiz_group_id={}".format(quiz_group_id))
              return quiz_group_id

       return 0

def main():
       global Verbose_Flag
       global quiz_question_groups

       # constant(s)

       # assumed upper limit of number of alternatives in multiple choice questions
       max_choices=10

       # assumed upper limit on number of question fields that are common
       max_question_fields=10


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
              print("Insuffient arguments\n must provide course_id quiz_id\n")
              return

       if (len(remainder) >= 1):
              course_id=remainder[0]
              if Verbose_Flag:
                     print("course_id={}".format(course_id))

       quiz_id_valid=False
       question_group_name='Newgroup'
       quiz_question_groups=dict()
       question=dict()
       quiz_name='sample multiple answer quiz'


       if (len(remainder) >= 2):
              quiz_id=remainder[1]
              if Verbose_Flag:
                     print("quiz_id={}".format(quiz_id))
              #check that this quiz_id is valid
              quizzes=list_quizzes(course_id)

              for q in quizzes:
                     if Verbose_Flag:
                            print("valid q['id']={}".format(q['id']))
                     if q['id'] == int(quiz_id):
                            if Verbose_Flag:
                                   print("valid quiz_id={}".format(quiz_id))
                            quiz_id_valid=True
                            break
       else:
              # need to create a quiz
              quiz_id=create_quiz(course_id, quiz_name)
              quiz_id_valid=True
              if Verbose_Flag:
                     print("quiz_id={}".format(quiz_id))


       # if the qiuz_id is not valid then there is nothing to do
       if not quiz_id_valid:
              print("quiz_id={} is not valid".format(quiz_id))
              return

       # now do question type specific processing
       question=dict()
       question['question_type']="calculated_question"
       question['question_name']="Q6"
       question['points_possible']=1
       question['question_text']="<p>Simple formula question. <span>What is 5 plus [x]?</span></p>"
       question['question_category']='Unknown'

       question['answers']=[
              {'answer_weight': 100, "variables": [{"name": "x", "value": "0"}], "answer_text": 5 },
              {'answer_weight': 100, "variables": [{"name": "x", "value": "1"}], "answer_text": 6 },
              {'answer_weight': 100, "variables": [{"name": "x", "value": "2"}], "answer_text": 7 },
              {'answer_weight': 100, "variables": [{"name": "x", "value": "3"}], "answer_text": 8 },
              {'answer_weight': 100, "variables": [{"name": "x", "value": "4"}], "answer_text": 9 },
              {'answer_weight': 100, "variables": [{"name": "x", "value": "5"}], "answer_text": 10},
              {'answer_weight': 100, "variables": [{"name": "x", "value": "6"}], "answer_text": 11},
              {'answer_weight': 100, "variables": [{"name": "x", "value": "7"}], "answer_text": 12},
              {'answer_weight': 100, "variables": [{"name": "x", "value": "8"}], "answer_text": 13},
              {'answer_weight': 100, "variables": [{"name": "x", "value": "9"}], "answer_text": 14},
              {'answer_weight': 100, "variables": [{"name": "x", "value": "10"}], "answer_text": 15}]
       question['variables']=[{"name": "x", "min": 0, "max": 10, "scale": 0}]

       #question['formulas']=[{"formula": "5+x"}]
       # note that the above does not work, you have to do it as below:
       question['formulas']=["5+x"]

       question['answer_tolerance']="0"
       question['formula_decimal_places']=0


       question_id=create_quiz_question(course_id, quiz_id, question)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()
