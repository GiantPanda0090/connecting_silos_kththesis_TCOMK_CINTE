#!/usr/bin/python3
#
# ./insert_quiz_from_spreadsheet.py course_id filename.xlsx [quiz_id]
#
# reads the spreadsheet and inserts the questions into a quiz for the indicated course.
#
# G. Q. Maguire Jr.
#
# 2017.05.13
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

def parent_account_name(id, x):
       for i in x:
              if (id==i['id']):
                     return i['name']


def info_about_account(account_id):
       accountBaseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/accounts/"
       accounts_found_thus_far=[]

       #get information about a single account
       #GET /v1/accounts/{id}

       url = accountBaseUrl + "%s" % (account_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting account info: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return page_response
       return


def list_courses_in_account(account_id):
       accountBaseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/accounts/"
       courses_found_thus_far=[]

       #List active courses in an account
       #GET /api/v1/accounts/:account_id/courses

       url = accountBaseUrl + '%s/courses' % (account_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting courses: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              courses_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     courses_found_thus_far.append(p_response)

       return courses_found_thus_far



def list_announcements_date_range(course_id, start_date, end_date):
       announcementsUrl="https://"+configuration["canvas"]["host"]+"/api/v1/announcements"
       announcements_found_thus_far=[]

       # Use the Canvas API to get the list of annoucements for the course
       #GET /api/v1/announcements
       # https://kth.instructure.com:443/api/v1/announcements?context_codes[]=course_11&start_date=2017-01-01&end_date=2017-03-25

       #url = announcementsUrl + '?context_codes[]=course_%s&start_date=2017-01-01&end_date=2017-03-25' % (course_id)
       url = announcementsUrl + '?context_codes[]=course_%s&start_date=%s&end_date=%s' % (course_id, start_date, end_date)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting announcements: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              announcements_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     announcements_found_thus_far.append(p_response)

       return announcements_found_thus_far



def list_announcements(course_id):
       announcementsUrl="https://"+configuration["canvas"]["host"]+"/api/v1/announcements"
       announcements_found_thus_far=[]

       # Use the Canvas API to get the list of announcements for the course
       #GET /api/v1/courses/:course_id/assignments
       url = announcementsUrl + '?context_codes[]=course_%s' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting announcements: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              announcements_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     announcements_found_thus_far.append(p_response)

       return announcements_found_thus_far

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
              page_response=r.json()
              print("inserted column")
              return True
       return False

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

def create_quiz_question1(course_id, quiz_id, question):
       global Verbose_Flag

       global quiz_question_groups
       print("in create_quiz_question1")

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
       payload={}
       if question.get('question_name'):
              payload.update({'question[question_name]': question['question_name']})
       if question.get('question_text'):
              payload.update({'question[question_text]': question['question_text']})
       if question.get('question_type'):
              payload.update({'question[question_type]': question['question_type']})
       if question.get('points_possible'):
              payload.update({'question[points_possible]': question['points_possible']})
       if question.get('correct_comments'):
              payload.update({'question[correct_comments]': question['correct_comments']})
       if question.get('incorrect_comments'):
              payload.update({'question[incorrect_comments]': question['incorrect_comments']})
       if question.get('neutral_comments'):
              payload.update({'question[neutral_comments]': question['neutral_comments']})
       if question.get('text_after_answers'):
              payload.update({'question[text_after_answers]': question['text_after_answers']})

       payload.update({'question[quiz_group_id]': quiz_group_id})

       if question.get('answers'):
              payload.update({'question[answers]': question['answers']})

       r = requests.post(url, headers = header, data=payload)
       print("payload={}".format(payload))

       write_to_log("result of post creating question: " + r.text)
       if r.status_code == requests.codes.ok:
              write_to_log("result of creating question in the course: " + r.text)
              page_response=r.json()
              print("inserted question")
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
                       'answers': question['answers'],
                       'question_text': question['question_text'],
                       'quiz_group_id': quiz_group_id
                }
       }

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



def number_of_blanks(question_text):
       global Verbose_Flag

       # the blanks are to be placed where there is a value in square brackets, such as [string]
       # examples:
       # Ungefär hur många timmar (inklusive ev schemalagda timmar) har du lagt på MATEMATIK idag? [1,2,3,4,5,6,7,8,9]
       # [2]h Lyssnat på föreläsning<br/>[2]h Läst i boken<br/>[2]h Gjort uppgifter i boken<br/>[2]h Jobbat med test i Bilda<br/>[2]h Jobbat med gamla tentor<br/>[2]h Förberett/bearbetat lab<br/>[2]h Annat, nämligen vad? [lekt polis]
       # Ev egna kommentarer till dagens arbetsinsats: [lkklllklklklklkkadadadadadadadfafafafafa]                                     
       output_string=''
       number_of_left_brackets=question_text.count('[')
       number_of_right_brackets=question_text.count(']')
       if Verbose_Flag:
              print("fill_in_blank_text - {}".format(question_text))
              print("left {0}, right {1}".format(number_of_left_brackets, number_of_right_brackets))

       if (number_of_left_brackets == number_of_right_brackets):
              return number_of_left_brackets

       print("misbalanced square brackets in text={}".format(question_text))
       return 0

def check_type_of_blank(question_text_fill_in):
       offset_to_opening_bracket=question_text_fill_in.find('[')
       if question_text_fill_in.find('[1,2,3,4,5,6,7,8,9]') >= 0:
              return "1to9"
       elif not (question_text_fill_in[offset_to_opening_bracket+1]).isdigit():
              return "text"
       else:
              return "unknown"

def fill_in_blank_text(question_text):
       global Verbose_Flag

       # the blanks are to be placed where there is a value in square brackets, such as [string]
       # examples:
       # Ungefär hur många timmar (inklusive ev schemalagda timmar) har du lagt på MATEMATIK idag? [1,2,3,4,5,6,7,8,9]
       # [2]h Lyssnat på föreläsning<br/>[2]h Läst i boken<br/>[2]h Gjort uppgifter i boken<br/>[2]h Jobbat med test i Bilda<br/>[2]h Jobbat med gamla tentor<br/>[2]h Förberett/bearbetat lab<br/>[2]h Annat, nämligen vad? [lekt polis]
       # Ev egna kommentarer till dagens arbetsinsats: [lkklllklklklklkkadadadadadadadfafafafafa]                                     
       output_string=''
       number_of_left_brackets=question_text.count('[')
       number_of_right_brackets=question_text.count(']')
       if Verbose_Flag:
              print("fill_in_blank_text - {}".format(question_text))
              print("left {0}, right {1}".format(number_of_left_brackets, number_of_right_brackets))

       if number_of_left_brackets == number_of_right_brackets:
              if number_of_left_brackets == 0:
                     return question_text
              for blank_number in range(0,number_of_left_brackets):
                     prefix=question_text.find('[')
                     if prefix >=0:
                            output_string=output_string+question_text[:prefix]+'[a'+str(blank_number)+']'
                     if Verbose_Flag:
                            print("output_string={}".format(output_string))

                     suffix=question_text.find(']')
                     question_text=question_text[suffix+1:]
                     if Verbose_Flag:
                            print("output_string={}".format(output_string))
                     if len(question_text) > 0:
                            continue
                     else:
                            return output_string+question_text
              return output_string+question_text


       else:
              print("misbalanced square brackets in text={}".format(question_text))
              return question_text

def fill_in_single_blank_text(question_text_fill_in):
       prefix=question_text_fill_in.find('[')
       suffix=question_text_fill_in.find(']')
       if suffix > prefix:
              return question_text_fill_in[:prefix-1]+question_text_fill_in[suffix+1:]

       print("Error in fill_in_single_blank_text, suffix is before prefix")
       return question_text_fill_in

# look at the letter following the right bracket, if it is "h" then the blank is about hours
# for example: [2]h Lyssnat på föreläsning<br/>
# from ./app/models/quizzes/quiz_question/answer_parsers/fill_in_multiple_blanks.rb
#
#       answer = Quizzes::QuizQuestion::AnswerGroup::Answer.new({
#          id: fields.fetch_any(:id, nil),
#          text: fields.fetch_with_enforced_length([:answer_text, :text]),
#          comments: fields.fetch_with_enforced_length([:answer_comment, :comments]),
#          comments_html: fields.fetch_with_enforced_length([:answer_comment_html, :comments_html]),
#          weight: fields.fetch_any([:answer_weight, :weight]).to_f,
#          blank_id: fields.fetch_with_enforced_length(:blank_id)
#        })
def guess_type_of_blank(number_of_blanks, question_text_fill_in):
       chunks_of_text=question_text_fill_in.split(']')

       possible_answers=[]
       for blank_number in range(0,number_of_blanks):
              blank_id='a'+str(blank_number)

              current_chunk=chunks_of_text[blank_number]
              if Verbose_Flag:
                     print("current_chunk={}".format(current_chunk))

              # if len(current_chunk) > 0 and (current_chunk[-1]).isdigit():
              #        try:
              #               chunk=chunks_of_text[blank_number+1]
              #        except IndexError:
              #               chunk = "".join[u'\U0001f630', u'\U0001f631']

              #        print("chunk length={0} string={1}".format(len(chunk), chunk))
              #        if len(chunk) > 0 and chunk[0] == 'h':
              #               hours_answers=[
              #                      {'answer_text': "0", 'answer_weight': 100, 'blank_id': blank_id},
              #                      {'answer_text': "1", 'answer_weight': 100, 'blank_id': blank_id},
              #                      {'answer_text': "2", 'answer_weight': 100, 'blank_id': blank_id},
              #                      {'answer_text': "3", 'answer_weight': 100, 'blank_id': blank_id},
              #                      {'answer_text': "4", 'answer_weight': 100, 'blank_id': blank_id},
              #                      {'answer_text': "5", 'answer_weight': 100, 'blank_id': blank_id},
              #                      {'answer_text': "6", 'answer_weight': 100, 'blank_id': blank_id},
              #                      {'answer_text': "7", 'answer_weight': 100, 'blank_id': blank_id},
              #                      {'answer_text': "8", 'answer_weight': 100, 'blank_id': blank_id},
              #                      {'answer_text': "9", 'answer_weight': 100, 'blank_id': blank_id}
              #               ]
              #               possible_answers.extend(hours_answers)
              # else:
              poss_answers=[
                     {'answer_text': " ", 'answer_weight': 100, 'blank_id': blank_id},
              ]
              possible_answers.extend(poss_answers)

       return possible_answers


def clean_text(t1):
       # remove trailing "<br>"
       regex = r'(.*)%s$' % re.escape('<br>')
       return re.sub(regex, r'\1', t1)

def clean_question_category(qc):
       return qc.replace(':', '-')

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
              print("Insuffient arguments\n must provide course_id filename.xlsx [quiz_id]\n")
              return

       if (len(remainder) >= 1):
              course_id=remainder[0]
              if Verbose_Flag:
                     print("course_id={}".format(course_id))

       if (len(remainder) >= 2):
              question_spreadsheet=remainder[1]
              if Verbose_Flag:
                     print("question_spreadsheet={}".format(question_spreadsheet))
       else:
              print("Nothing to do, no spreatsheet provided")
              return

       spread_sheet = pd.ExcelFile(question_spreadsheet)
       sheet_name=spread_sheet.sheet_names[0] # take first spreadsheet name as the name for the quiz
       quiz_name=question_spreadsheet[:-5]
       if Verbose_Flag:
              print("quiz_name={}".format(quiz_name))


       # read the contents of the named sheet into a Panda data frame
       df = spread_sheet.parse(sheet_name)

       # check that it is an exported question bank, in which case the top cell is "Exported from the questionbank in PING PONG"
       if df.columns[0].find("Exported from the questionbank in PING PONG") >= 0:
              print("question bank exported from PING PONG")
       else:
              print("not a question bank exported from PING PONG")
              return

       shape=df.shape
       print("number of columns is {}".format(shape[1]))
       print("number of rows is {}".format(shape[0]))

       # rename the columns c1 ... cn
       new_column_names=[]
       for i in range(1,shape[1] + 1):
              new_column_names.append('c'+str(i))

       # name the columns
       df.columns = new_column_names

       if Verbose_Flag:
              print("new_column_names={}".format(new_column_names))

       quiz_id_valid=False

       if (len(remainder) >= 3):
              quiz_id=remainder[2]
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

       # question_indexes will contain the starting index of the questions
       # questions are separated from each other by enpty rows and start with a cell containing "Question"
       question_indexes=[]
       last_rows_is_blank=False
       rows_is_blank=False

       for index, row in  df.iterrows():
              if Verbose_Flag:
                     print("row {}".format(index))

              last_rows_is_blank=rows_is_blank

              # row[c1]=Format, row[c2]:=QI625
              if index == 0:
                     if (row['c1'].find("Format") >= 0) and (row['c2'].find("QI625") >= 0):
                            print("question bank in format {}".format(row['c2']))
                            continue
                     else:
                            print("question bank format not understoond")
                            return

              # if there are three columns in the spread sheet then use the following comparison, otherwise use the one below it
              if shape[1] >= 3:
                     if pd.isnull(row['c1']) and pd.isnull(row['c2']) and pd.isnull(row['c3']):
                            print("row {} is blank".format(index))
                            rows_is_blank=True
                            continue
              if shape[1] == 2:
                     if pd.isnull(row['c1']) and pd.isnull(row['c2']):
                            print("row {} is blank".format(index))
                            rows_is_blank=True
                            continue


              rows_is_blank=False
              if last_rows_is_blank and (row['c1'].find("Question") >= 0):
                     question_indexes.append(index)


              if Verbose_Flag:
                        if shape[1] >= 3:
                               print('index: {0}, row[c1]={1}, row[c2]:={2}, row[c3]={3}'.format(index, row['c1'], row['c2'], row['c3']))
                        else:
                               print('index: {0}, row[c1]={1}, row[c2]:={2}, row[c3]={3}'.format(index, row['c1'], row['c2']))

       print("question_indexes={}".format(question_indexes))
       print("number of questions={}".format(len(question_indexes)))

       question_group_name='Newgroup'
       question=dict()

       quiz_question_groups=dict()

       # now process each question
       # examples of questions:
       #Question	
       #Category	tid1
       #Name	tidredovisning p3:mtid
       #Text	
       #Max points	0.0
       #Type	Fill in the blanks
       #Fill in the blanks	Ungefär hur många timmar (inklusive ev schemalagda timmar) har du lagt på MATEMATIK idag? [1,2,3,4,5,6,7,8,9]

       list_of_questions=[]
       list_of_questionIDs=[]
       # to process only a limited subset of questions add the range, scuh as [15:20]
       for question_index in question_indexes:
              # the following variables are used to collect the fields of the questions; reinitialize
              question_category=None
              question_description=None
              question_id=None
              question_max_points=None
              question_name=None
              question_text=None
              question_type=None

              # get some of the basic material that is part of each question (or most questions)
              # then remember the offset from the last of these and use it in the subsequent question type specific processing
              last_offset=0
              for f in range(1,max_question_fields):
                     current_field=df.get_value(question_index+f, 'c1')
                     print("current_field={}".format(current_field))

                     if isinstance(current_field, str):
                            if current_field.find("Category") >=0:
                                   question_category=df.get_value(question_index+f, 'c2')
                                   print("question_category={}".format(question_category))
                                   last_offset=f
                                   continue

                            if current_field.find("Name") >=0:
                                   question_name=df.get_value(question_index+f, 'c2')
                                   print("question_name={}".format(question_name))
                                   last_offset=f
                                   continue

                            if current_field.find("Description") >=0:
                                   question_description=df.get_value(question_index+f, 'c2')
                                   print("question_description={}".format(question_description))
                                   last_offset=f
                                   continue

                            if current_field.find("Text") >=0:
                                   question_text=df.get_value(question_index+f, 'c2')
                                   if pd.isnull(question_text):
                                          question_text=''
                                   print("question_text={}".format(question_text))
                                   last_offset=f
                                   continue

                            if current_field.find("Max points") >=0:
                                   question_max_points=df.get_value(question_index+f, 'c2')
                                   print("question_max_points={}".format(question_max_points))
                                   last_offset=f
                                   continue

                            if current_field.find("Type") >=0:
                                   question_type=df.get_value(question_index+f, 'c2')
                                   print("question_type={}".format(question_type))
                                   last_offset=f
                                   break

              # to make it easier to sort the questions into question banks, prefix the question_name with the question_category
              question_name=clean_question_category(question_category)+'-'+question_name

              # now do question type specific processing
              if question_type.find("Fill in the blanks") >= 0:
                     question_type="fill_in_multiple_blanks_question"
                     question=dict()
                     question['question_name']=question_name
                     question['points_possible']=question_max_points
                     question['question_category']=question_category

                     if (df.get_value(question_index+last_offset+1, 'c1')).find("Fill in the blanks") >=0:
                            question_text_fill_in=df.get_value(question_index+last_offset+1, 'c2')
                            print("question_text_fill_in={}".format(question_text_fill_in))

                            actual_number_of_blanks=number_of_blanks(question_text_fill_in)
                            if actual_number_of_blanks == 1:
                                   type_of_blank=check_type_of_blank(question_text_fill_in)
                                   if type_of_blank == 'text':
                                          question_type="essay_question"
                                          question['question_type']=question_type
                                          question['question_text']=question_text+fill_in_single_blank_text(question_text_fill_in)
                                          if Verbose_Flag:
                                                 print("single text blank question={}".format(question))
                                          question_id=create_quiz_question1(course_id, quiz_id, question)
                                          list_of_questionIDs.append(question_id)
                                          continue


                                   if type_of_blank == "1to9":
                                          question_type="numerical_question"
                                          question['question_type']=question_type

                                          question['question_text']=question_text+fill_in_single_blank_text(question_text_fill_in)
                                          if Verbose_Flag:
                                                 print("1 to 9 blank question={}".format(question))
                                          question['answers']=[{'answer_text': '', 'numerical_answer_type': 'range_answer', 'answer_weight': 100, 'answer_range_end': 24.0, 'answer_range_start': 0.0, 'answer_comments_html': '', 'answer_comments': ''}]

                                          question_id=create_quiz_question(course_id, quiz_id, question)
                                          list_of_questionIDs.append(question_id)
                                          continue

                            else:
                                   question['question_text']=question_text+fill_in_blank_text(question_text_fill_in)
                                   question['question_type']=question_type

                                   # if the category begins with "tid" it is probably a question asking about the hours that a student
                                   # has spent doing something for the course, hence we can gets some numbers for the different fields
                                   if question_category.find("tid") == 0:
                                          possible_choices=guess_type_of_blank(actual_number_of_blanks, question_text_fill_in)
                                          question['answers']=possible_choices

                                   if Verbose_Flag:
                                          print("question={}".format(question))
                                   question_id=create_quiz_question(course_id, quiz_id, question)
                                   list_of_questionIDs.append(question_id)
                                   continue

              #Is Ping Pong 'Free writing' == Canvas 'essay_question'?
              elif question_type.find("Free writing") >= 0:
                     question_type="essay_question"
                     question=dict()
                     question['question_name']=question_name
                     question['points_possible']=question_max_points
                     question['question_text']=question_text
                     question['question_type']=question_type
                     question['question_category']=question_category
                     print("question={}".format(question))
                     question_id=create_quiz_question1(course_id, quiz_id, question)
                     list_of_questionIDs.append(question_id)
                     continue

              elif question_type.find("Multiple choice") >= 0:
                     question_type="multiple_choice_question"

                     if (df.get_value(question_index+last_offset+1, 'c1')).find("Max choices") >=0:
                            question_max_choices=df.get_value(question_index+last_offset+1, 'c2')
                            if Verbose_Flag:
                                   print("question_max_choices={}".format(question_max_choices))
                     # if there are multiple answers permitted, the the Canvas question type must be multiple_answers_question
                     if question_max_choices > 1:
                            question_type="multiple_answers_question"


                     possible_choices=[]
                     for choice in range(0,max_choices):
                            if question_index+last_offset+2+choice >= shape[0]:
                                   break
                            if pd.isnull(df.get_value(question_index+last_offset+2+choice, 'c1')):
                                   break

                            if (df.get_value(question_index+last_offset+2+choice, 'c1')).find("Correct") >=0:
                                   current_choice={'answer_comments': '', 'answer_weight': 100, 'answer_text': clean_text(df.get_value(question_index+last_offset+2+choice, 'c2')) }
                                   print("correct choice[{0}]={1}".format(choice, current_choice))
                                   possible_choices.append(current_choice)

                            if (df.get_value(question_index+last_offset+2+choice, 'c1')).find("Incorrect") >=0:
                                   current_choice={'answer_comments': '', 'answer_weight': 0, 'answer_text': clean_text(df.get_value(question_index+last_offset+2+choice, 'c2')) }
                                   print("incorrect choice[{0}]={1}".format(choice, current_choice))
                                   possible_choices.append(current_choice)


                     question=dict()
                     question['question_name']=question_name
                     question['points_possible']=question_max_points
                     question['question_text']=question_text
                     question['question_type']=question_type
                     question['question_category']=question_category
                     #question['matches'] = None
                     question['answers']=possible_choices


                     if Verbose_Flag:
                            print("question={}".format(question))
                     question_id=create_quiz_question(course_id, quiz_id, question)
                     list_of_questionIDs.append(question_id)
                     continue
              else:
                     print("******* question_index={} not processed".format(question_index))


              # elements of a Canvas question
              #question[question_name]		string	The name of the question.
              # question[question_text]		string	The text of the question.
              #question[quiz_group_id]		integer	The id of the quiz group to assign the question to.
              #question[question_type]		string	The type of question. Multiple optional fields depend upon the type of question to be used.
              #Allowed values:                     calculated_question, essay_question, file_upload_question, fill_in_multiple_blanks_question, matching_question, multiple_answers_question, multiple_choice_question, multiple_dropdowns_question, numerical_question, short_answer_question, text_only_question, true_false_question
              #question[position]		integer	The order in which the question will be displayed in the quiz in relation to other questions.
              #question[points_possible]		integer	The maximum amount of points received for answering this question correctly.
              #question[correct_comments]		string	The comment to display if the student answers the question correctly.
              #question[incorrect_comments]		string	The comment to display if the student answers incorrectly.
              #question[neutral_comments]		string	The comment to display regardless of how the student answered.
              #question[text_after_answers]		string	no description
              #question[answers]		[Answer]	no description

       print("number of questionIDs={0}list_of_questionIDs={1}".format(len(list_of_questionIDs), list_of_questionIDs))

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()
