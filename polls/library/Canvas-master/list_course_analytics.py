#!/usr/bin/python3
#
# ./list_course_analytics.py course_id
#
# create a spread sheet of the course analytics information
#
# G. Q. Maguire Jr.
#
# 2017.01.05
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

import datetime
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
import os                       # to make OS calls, here to get time zone info
from dateutil.tz import tzlocal

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

#############################
###### EDIT THIS STUFF ######
#############################

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       access_token=configuration["canvas"]["access_token"]
       baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/courses/"
       baseUrlgroups="https://"+configuration["canvas"]["host"]+"/api/v1/groups/"
       baseUrlappointment_groups="https://"+configuration["canvas"]["host"]+"/api/v1/appointment_groups/"
       baseUrlcalendar_event="https://"+configuration["canvas"]["host"]+"/api/v1/calendar_events/"


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

def gqm_prnt_list(list1):
    index=0
    for i in list1:
        print(index, i)
        index = index+1

def list_course_analytics_student_summary_data(course_id):
    analytics_found_thus_far = []
    # GET /api/v1/courses/:course_id/analytics/student_summaries
    url = baseUrl + '%s/analytics/student_summaries' % (course_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        write_to_log("result of getting analytics/student_summaries: " + r.text)

    if r.status_code == requests.codes.ok:
        page_response=r.json()
    else:
        return analytics_found_thus_far

    for p_response in page_response:  
        analytics_found_thus_far.append(p_response)

    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
    if 'link' in r.headers:
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                analytics_found_thus_far.append(p_response)

    return analytics_found_thus_far


def list_course_analytics_assignment_data(course_id):
    analytics_found_thus_far = []
    # GET /api/v1/courses/:course_id/analytics/assignments
    # Parameter		Type	Description
    # async		boolean	
    url = baseUrl + '%s/analytics/assignments' % (course_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        write_to_log("result of getting analytics/assignments: " + r.text)

    if r.status_code == requests.codes.ok:
        page_response=r.json()
    else:
        return analytics_found_thus_far

    for p_response in page_response:  
        analytics_found_thus_far.append(p_response)

    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
    if 'link' in r.headers:
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                analytics_found_thus_far.append(p_response)

    return analytics_found_thus_far



def list_course_analytics_participation_data(course_id):
    analytics_found_thus_far = []
    # GET /api/v1/courses/:course_id/analytics/activity
    url = baseUrl + '%s/analytics/activity' % (course_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        write_to_log("result of getting analytics/activity: " + r.text)

    if r.status_code == requests.codes.ok:
        page_response=r.json()
    else:
        return analytics_found_thus_far

    for p_response in page_response:  
        analytics_found_thus_far.append(p_response)

    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
    if 'link' in r.headers:
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                analytics_found_thus_far.append(p_response)

    return analytics_found_thus_far


def list_course_analytics_user_participation_data(course_id, user_id):
    # GET /api/v1/courses/:course_id/analytics/users/:student_id/activity
    url = baseUrl + '%s/analytics/users/%s/activity' % (course_id, user_id)
    if Verbose_Flag:
        print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
        write_to_log("result of getting analytics/activity: " + r.text)

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response

    return []

def make_appointment_with_comment(calendar_event_id, participant_id, comment):
    global Force_appointment_flag

    # Use the Canvas API to make an appointment
    # POST /api/v1/calendar_events/:id/reservations/:participant_id
    # Request Parameters:
    #Parameter		Type	Description
    #participant_id	string	User or group id for whom you are making the reservation (depends on the participant type). Defaults to the current user (or user's candidate group).
    # comments		string	Comments to associate with this reservation
    # cancel_existing	boolean	Defaults to false. If true, cancel any previous reservation(s) for this participant and appointment group.

    url = baseUrlcalendar_event + '%s/reservations/%s' % (calendar_event_id, participant_id)
    if Verbose_Flag:
       print("url: " + url)
    payload={'participant_id': participant_id, 'comments': comment }

    if Force_appointment_flag:
        payload['cancel_existing']=True

    r = requests.post(url, headers = header, data=payload)
    write_to_log("result of post making an appointment: " + r.text)
    if r.status_code == requests.codes.ok:
       write_to_log("result of making an appointment: " + r.text)
       if r.status_code == requests.codes.ok:
           page_response=r.json()
           print("inserted appointment")
           return True
    return False

def convert_to_local_times(input_df, list_of_columns_to_convert):
    global Use_local_time_for_output_flag

    for c in list_of_columns_to_convert:
        working_list=[]
        for row in input_df[c]:
            if row is None:
                working_list.append("")
            else:
                t1=isodate.parse_datetime(row)
                if Use_local_time_for_output_flag:
                    t2=t1.astimezone()
                    working_list.append(t2.strftime("%Y-%m-%d %H:%M"))
                else:
                    working_list.append(t1.strftime("%Y-%m-%d %H:%M"))
        input_df['local_'+c]=working_list


def get_calendar_event(calendar_event_id):
       # Use the Canvas API to get the calendar event
       #GET /api/v1/calendar_events/:id
       url = baseUrlcalendar_event + '%s' % (calendar_event_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting a single calendar event: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return page_response

       return None



def list_of_appointment(start_date, end_date):
    appointments_found_thus_far=[]

    # Use the Canvas API to get the list of appointments for the current user
    # GET /api/v1/appointment_groups
       
    url = baseUrlappointment_groups
    if Verbose_Flag:
        print("url: " + url)

    extra_parameters={'scope': 'manageable', 'include_past_appointments': 'true', 'include[]': 'appointments'}
    r = requests.get(url, params=extra_parameters, headers = header)
    if Verbose_Flag:
        write_to_log("result of getting appointment: " + r.text)

    if r.status_code == requests.codes.ok:
        page_response=r.json()
    else:
        return appointments_found_thus_far

    for p_response in page_response:  
        if p_response['start_at'] is not None:
            if (isodate.parse_datetime(p_response['start_at']) >= start_date) and (isodate.parse_datetime(p_response['start_at']) <= end_date):
                appointments_found_thus_far.append(p_response)
        else:
            appointments_found_thus_far.append(p_response)
    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
    if 'link' in r.headers:
        while r.links['current']['url'] != r.links['last']['url']:  
            r = requests.get(r.links['next']['url'], headers=header)  
            page_response = r.json()  
            for p_response in page_response:  
                if p_response['start_at'] is not None:
                    if (isodate.parse_datetime(p_response['start_at']) >= start_date) and (isodate.parse_datetime(p_response['end_at']) <= end_date):
                        appointments_found_thus_far.append(p_response)
                else:
                    appointments_found_thus_far.append(p_response)

        return appointments_found_thus_far

def get_appointment_group(appointment_group_id):
       appointment_groups_found_thus_far=dict()

       # Use the Canvas API to get the list of appointments for the current user
       # GET /api/v1/appointment_groups/:id

       url = baseUrlappointment_groups + '%s' % (appointment_group_id)
       if Verbose_Flag:
              print("url: " + url)

       extra_parameters={'include[]': 'appointments'}
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting a single appointment group: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return page_response

       return appointment_groups_found_thus_far


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

def students_in_course(course_id):
       students_found_thus_far=[]

       # Use the Canvas API to get the list of students in this course
       # GET /api/v1/courses/:course_id/users

       url = baseUrl + '%s/users' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       # enrollment_type[] should be set to 'student'
       # include[] perhaps include email, enrollments, avatar_url
       extra_parameters={'enrollment_type[]': 'student', 'include[]': 'email, enrollments, avatar_url'}
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting student enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              students_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            students_found_thus_far.append(p_response)
       return students_found_thus_far

def members_of_groups(group_id):
       members_found_thus_far=[]

       # Use the Canvas API to get the list of members of group
       # GET /api/v1/groups/:group_id/users

       url = baseUrlgroups + '%s/users' % (group_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting group info: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              members_found_thus_far.append(p_response['id'])

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            members_found_thus_far.append(p_response['id'])
       return members_found_thus_far



def list_groups_in_course(course_id):
       groups_found_thus_far=[]

       # Use the Canvas API to get the list of groups in this course
       # GET /api/v1/courses/:course_id/groups

       url = baseUrl + '%s/groups' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting groups: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              groups_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            groups_found_thus_far.append(p_response)
       return groups_found_thus_far


def main():
    global Verbose_Flag

    Use_local_time_for_output_flag=True
    sheet_per_user=False

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
        print("Inusffient arguments\n must provide course_id\n")
        return

    course_id=remainder[0]

    students=students_in_course(course_id)
    students_df=pd.io.json.json_normalize(students)
    if Verbose_Flag:
        print('students_df columns: ', students_df.columns)


    student_summary = list_course_analytics_student_summary_data(course_id)
    student_summary_df=pd.io.json.json_normalize(student_summary)
    if Verbose_Flag:
        print('student_summary_df columns: ', student_summary_df.columns)

    student_summary_merge_df = pd.merge(student_summary_df, students_df, on='id')

    assignment_data=list_course_analytics_assignment_data(course_id)
    assignment_data_df=pd.io.json.json_normalize(assignment_data)
    if Verbose_Flag:
        print('assignment_data_df columns: ', assignment_data_df.columns)

    participation=list_course_analytics_participation_data(course_id)
    participation_df=pd.io.json.json_normalize(participation)

    # set up the output write
    writer = pd.ExcelWriter('course_analytics-'+str(course_id)+'.xlsx', engine='xlsxwriter')

    student_summary_merge_df.to_excel(writer, sheet_name='Summary')
    assignment_data_df.to_excel(writer, sheet_name='Submissions')
    participation_df.to_excel(writer, sheet_name='Activity')

    all_pageviews={}
    all_participations={}
    for index, row in  students_df.iterrows():
        if Verbose_Flag:
            print('index: ', index, 'row[id]: ', row['id'])
            
        user_participation=list_course_analytics_user_participation_data(course_id, row['id'])
        if Verbose_Flag:
            print('length: ', len(user_participation), 'user_participation: ', user_participation)

        if len(user_participation) == 0:		# nothing to process
            continue

        # for testing - only loop a few times
        #if index > 5:
        #    break

        # store all of the date about each user's counts for a given time
        # in a dictionary index by times
        for k, v in user_participation['page_views'].items():
            new_entry={row['id']: v}
            existing_entries=all_pageviews.get(k)
            if existing_entries is None:
                all_pageviews[k]=new_entry
            else:
                all_pageviews[k].update(new_entry)
            
        if sheet_per_user:
            user_page_views_series=pd.Series(user_participation['page_views'], name='count')
            user_page_views_series.index.name = 'Timestamp'
            #user_page_views_series.reset_index()
            user_page_views_df=user_page_views_series.to_frame()
            user_page_views_df.to_excel(writer, sheet_name='User pageviews_'+str(row['id']))

        for item in user_participation['participations']:
            new_entry={row['id']: item['created_at']}
            existing_entries=all_participations.get(item['url'])
            if existing_entries is None:
                all_participations[item['url']]=new_entry
            else:
                all_participations[item['url']].update(new_entry)


        if sheet_per_user:
            user_participations_df=pd.DataFrame(user_participation['participations'])
            user_participations_df.to_excel(writer, sheet_name='User Participation_'+str(row['id']))


    
    if Verbose_Flag:
        for k, v in sorted(all_pageviews.items()):
            print(k, v)

    all_pageviews_df=pd.DataFrame(all_pageviews)
    transposed_all_pageviews_df=all_pageviews_df.transpose()
    transposed_all_pageviews_df.index.name = 'Timestamp'
    # now convert from ISO8601 with time zone offset to local times
    transposed_all_pageviews_df.index = pd.to_datetime(transposed_all_pageviews_df.index)

    transposed_all_pageviews_df.to_excel(writer, sheet_name='All user pageviews')

    all_participations_df=pd.DataFrame(all_participations)
    transposed_all_participations=all_participations_df.transpose()

    list_of_columns=transposed_all_participations.columns.values.tolist()
    columns_to_convert=list_of_columns[1:]                 #skip the first column which is a URL
    for c in columns_to_convert:                           # convert each of the columns to local times
        transposed_all_participations[c]=pd.to_datetime(transposed_all_participations[c])

    transposed_all_participations.to_excel(writer, sheet_name='All participations')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   
    write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()
