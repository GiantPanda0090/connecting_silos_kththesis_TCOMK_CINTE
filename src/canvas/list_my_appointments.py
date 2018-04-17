#!/usr/bin/python3
#
# ./list_my_appointments.py start_date end_date
#
# outputs a spreadsheet of appointments as an xlsx file of the form: appointments.xlsx
#
# Extensive use is made of Python Pandas merge operations.
#
# The dates from Canvas are in ISO 8601 format.
# Therefore I have used start_date and end_date in UTC, so that (except for the logging operation) all datetimes are in UTC
# and output in local time format if the Use_local_time_for_output_flag is True (the default).
# 
# G. Q. Maguire Jr.
#
# 2016.12.13
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
    global Use_local_time_for_output_flag

    Use_local_time_for_output_flag=True

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

    # from amorphic Sep 2 '14 at 23:54 in http://stackoverflow.com/questions/2720319/python-figure-out-local-timezone
    my_tz_name = '/'.join(os.path.realpath('/etc/localtime').split('/')[-2:])
    my_tz = pytz.timezone(my_tz_name)

    if (len(remainder) == 2):
        start_date=datetime.datetime.combine(isodate.parse_date(remainder[0]), datetime.time.min).replace(tzinfo=my_tz)
        end_date=datetime.datetime.combine(isodate.parse_date(remainder[1]), datetime.time.min).replace(tzinfo=my_tz)
        output_file='appointments-'+remainder[0]+'-'+remainder[1]+'.xlsx'
    elif (len(remainder) == 1):
        start_date=datetime.datetime.combine(isodate.parse_date(remainder[0]), datetime.time.min).replace(tzinfo=my_tz)
        end_date=datetime.datetime(3000, 1, 1, 0, 0, 0, 0).replace(tzinfo=my_tz)               # use 3000-01-01 as default end date to get "all" appointments
        output_file='appointments-'+remainder[0]+'.xlsx'
    else:
        start_date=datetime.datetime(1900, 1, 1, 0, 0, 0, 0).replace(tzinfo=my_tz)             # use 1900-01-01 as default start date to get "all" appointments
        end_date=datetime.datetime(3000, 1, 1, 0, 0, 0, 0).replace(tzinfo=my_tz)               # use 3000-01-01 as default end date to get "all" appointments
        output_file='appointments.xlsx'

    if Verbose_Flag:
        print("start date: ", start_date.isoformat())
        print("end date: ", end_date.isoformat())

    appointments=list_of_appointment(start_date, end_date)
    if Verbose_Flag:
        print("appointments: " + str(appointments))

    appointments_df=pd.io.json.json_normalize(appointments)

    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    convert_to_local_times(appointments_df, ['created_at', 'updated_at', 'start_at', 'end_at'])

    appointments_df.to_excel(writer, sheet_name='Appointments')

    sheet_index=0
    for ag in appointments:
        if Verbose_Flag:
            print("ag: " + str(ag))
            print("ag id: ", ag['id'])

        ag_info=get_appointment_group(ag['id'])
        if ag_info['appointments_count'] > 0:
            agi_list=[]
            for agi in ag_info['appointments']:
                cal_event=get_calendar_event(agi['id'])
                if cal_event['child_events_count'] > 0:
                    gmem={}
                    index=0
                    for child in cal_event['child_events']:
                        gmem['member_'+str(index)+'_id']=child['user']['id']
                        gmem['member_'+str(index)+'_name']=child['user']['name']
                        index += 1
                        agi.update(gmem)
                agi_list.append(agi)

            ag_df=pd.io.json.json_normalize(agi_list)
            sheet_name=ag['title']
            if sheet_name is None:
                sheet_index =+ 1
                sheet_name='Unknown_'+str(sheet_index)
            if len(sheet_name) > 31: # truncate to 31 characters
                sheet_name=sheet_name.strip() # strip spaces out of name
                sheet_name=sheet_name[:30]
            convert_to_local_times(ag_df, ['created_at', 'updated_at', 'start_at', 'end_at'])
            #
            # to delete unwanted columns just add the to the list below
            columns_to_drop=['duplicates', 'html_url', 'hidden', 'reserve_url', 'url' ]
            if len(columns_to_drop) > 0:
                ag_df.drop(columns_to_drop,inplace=True,axis=1)

            ag_df.to_excel(writer, sheet_name=sheet_name)
              
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   
    write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()
