#!/usr/bin/python3
#
# ./insert_appointment.py course_id appointment_group appointment_spreadsheet.csv
#
# Take in a CSV with a list of the format:
# local_start_time,login_id
#  ...
#
# Insert these appointments into the calander as appointments
#
# G. Q. Maguire Jr.
#
# 2017.01.04
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
import isodate			# for parsing ISO 8601 dates and times
import pytz			# for time zones
import os			# to make OS calls, here to get time zone info
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
    if Verbose_Flag:
        write_to_log("result of post making an appointment: " + r.text)
    if r.status_code == requests.codes.ok:
        if Verbose_Flag:
            write_to_log("result of making an appointment: " + r.text)
        page_response=r.json()
        if Verbose_Flag:
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

def convert_local_times_to_utc(input_df, list_of_columns_to_convert):
    for c in list_of_columns_to_convert:
        working_list=[]
        for row in input_df[c]:
            if row is None:
                working_list.append("")
            else:
                t1=datetime.datetime.strptime(row, "%Y-%m-%d %H:%M")
                t1=t1.replace(tzinfo=tzlocal())
                t2=t1.astimezone(pytz.utc)
                working_list.append(isodate.datetime_isoformat(t2))
        input_df['utc_'+c]=working_list

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
    global Force_appointment_flag

    Use_local_time_for_output_flag=True

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
		      dest="verbose",
		      default=False,
		      action="store_true",
		      help="Print lots of output to stdout"
    )

    parser.add_option('-f', '--force',
                      dest="force_appointment",
                      default=False,
                      action="store_true",
                      help="Force the appointment to be made - deleting the student from another appointment in this appointment group"
    )


    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    Force_appointment_flag=options.force_appointment
    if Verbose_Flag:
        print('ARGV	 :', sys.argv[1:])
        print('VERBOSE	 :', options.verbose)
        print('REMAINING :', remainder)
        print('Force_appointment_flag: ', Force_appointment_flag)

    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   

    if (len(remainder) < 3):
        print("Inusffient arguments\n must provide course_id appointment_group appointment_spreadsheet.csv\n")
        return

    course_id=remainder[0]
    appointment_group=remainder[1]
    appointment_spreadsheet=remainder[2]

    if Verbose_Flag:
        print('course_id: ', course_id)
        print('appointment_group: ', appointment_group)
        print('appointment_spreadsheet: ', appointment_spreadsheet)


    # read in the CSV entries from exported gradebook
    appointments_to_make_df=pd.read_csv(appointment_spreadsheet, sep=',')
    convert_local_times_to_utc(appointments_to_make_df, ['local_start_time'])
    appointments_to_make_df.rename(columns = {'utc_local_start_time':'start_at'}, inplace = True)

    students=students_in_course(course_id)
    students_df=pd.io.json.json_normalize(students)

    if Verbose_Flag:
        print('appointments_to_make_df: ', appointments_to_make_df.columns)
        print('students_df: ', students_df.columns)

    merge_df = pd.merge(appointments_to_make_df, students_df, on='login_id')


    ag_info=get_appointment_group(appointment_group)
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

    merged_new_appointments_df=pd.merge(merge_df, ag_df, on='start_at')
    merged_new_appointments_df.rename(columns = {'id_x':'user_id', 'id_y': 'calendar_event_id'}, inplace = True)

    for index, row in  merged_new_appointments_df.iterrows():
        make_appointment_with_comment(row['calendar_event_id'], row['user_id'],  "appointment made by instructor")

    if Verbose_Flag:
        # set up the output write
        writer = pd.ExcelWriter('appointments_to_add-'+str(course_id)+'.xlsx', engine='xlsxwriter')

        appointments_to_make_df.to_excel(writer, sheet_name='Appointments')
        students_df.to_excel(writer, sheet_name='Students')
        merge_df.to_excel(writer, sheet_name='MergedAppointments')
        ag_df.to_excel(writer, sheet_name='Appointmentgroup')
        merged_new_appointments_df.to_excel(writer, sheet_name='NewAppointments')

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()
		    
    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   
    write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()
