#!/usr/bin/python3
#
# ./place_students_in_sections_in_course.py course_id spreadshseet_name name_of_column_with_section_assignments
#
# inputs a spreadsheet of the section in a course as an xlsx file of the form: new_sections-in-189.xlsx
# then processes the column name_of_column_with_section_assignments on the second sheet "Students" (with the list of students):
#  1. collects the list of section names
#  2. if any section name does not yet exist for this course, create it
#  3. assign the student to the indicated section
#
# Note that the section names have to be strings
#
# Extensive use is made of Python Pandas merge operations.
# 
# G. Q. Maguire Jr.
#
# 2017.07.01
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

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
       baseUrlUsers="https://"+configuration["canvas"]["host"]+"/api/v1/users/"

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

def create_sections_in_course(course_id, section_names):
    sections_found_thus_far=[]

    # Use the Canvas API to create sections for this course
    #POST /api/v1/courses/:course_id/sections

    url = baseUrl + '%s/sections' % (course_id)
    if Verbose_Flag:
        print("url: " + url)

    for section_name in section_names:
        #course_section[name]
        payload={'course_section[name]': section_name}
        r = requests.post(url, headers = header, data=payload)

        if Verbose_Flag:
            write_to_log("result of creating section: " + r.text)

        if r.status_code == requests.codes.ok:
            page_response=r.json()

            for p_response in page_response:  
                sections_found_thus_far.append(p_response)

    return sections_found_thus_far

def students_in_course(course_id):
       students_found_thus_far=[]

       # Use the Canvas API to get the list of users enrolled as students in this course
       #GET /api/v1/courses/:course_id/enrollments

       url = baseUrl + '%s/enrollments' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       extra_parameters={'enrollment_type[]': 'student', 'include[]': 'email'}
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting enrollments: " + r.text)

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

def enroll_student_in_section(course_id, user_id, section_id):
    # POST /api/v1/courses/:course_id/enrollments
    # enrollment[user_id] = user_id
    # enrollment[type] = StudentEnrollment
    # enrollment[course_section_id] = section_id

    url = baseUrl + '%s/enrollments' % (course_id)
    if Verbose_Flag:
        print("url: " + url)

    payload={'enrollment[user_id]': user_id, 
             'enrollment[type]': 'StudentEnrollment',
             'enrollment[course_section_id]': section_id }
    r = requests.post(url, headers = header, data=payload)

    if Verbose_Flag:
        write_to_log("result of enrolling student in section: " + r.text)

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        return page_response

    return None


def main():
    global Verbose_Flag

    default_picture_size=128

    parser = optparse.OptionParser(usage="usage: %prog [options] filename")

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

    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   

    if (len(remainder) < 3):
        print("Insuffient arguments\n must provide course_id spreadshseet_name name_of_column_with_section_assignments\n")
        return

    course_id=remainder[0]
    spreadshseet_name=remainder[1]
    name_of_column_with_section_assignments=remainder[2]
    if Verbose_Flag:
        print("course_id={0}, spreadsheet={1}, column name={2}".format(course_id, spreadshseet_name, name_of_column_with_section_assignments))

    names_of_existing_sections=set()
    existing_sections_in_course=sections_in_course(course_id)
    for i in existing_sections_in_course:
        names_of_existing_sections.add(i['name'])

    if Verbose_Flag:
        print("names_of_existing_sections={}".format(names_of_existing_sections))

    spread_sheet = pd.ExcelFile(spreadshseet_name)
    sheet_names=spread_sheet.sheet_names
    if Verbose_Flag:
        print("sheet_names={0}".format(sheet_names))

    if 'Students' in sheet_names:
        print("Found sheet named {}".format('Students'))
        student_sheet_name='Students'
    else:
        print("Missing sheet named {}".format('Students'))
        return None
        
    # read the contents of the named sheet into a Panda data frame
    students_df = spread_sheet.parse(student_sheet_name)

    columns_on_sheet=students_df.columns
    if name_of_column_with_section_assignments in columns_on_sheet:
        if Verbose_Flag:
            print("desired column ({0}) exists".format(name_of_column_with_section_assignments))
        shape=students_df.shape
        if Verbose_Flag:
            print("number of columns is {}".format(shape[1]))
            print("number of rows is {}".format(shape[0]))
    else:
        print("desired column ({0}) does not exist".format(name_of_column_with_section_assignments))
        return None

    collected_section_names=set()
    for  index, row in students_df.iterrows():
        section_name=row[name_of_column_with_section_assignments]
        if type(section_name) is str:
            collected_section_names.add(section_name)

    missing_section_names=[]
    for i in collected_section_names:
        if i not in names_of_existing_sections:
            if Verbose_Flag:
                print("missing section: {}".format(i))
            missing_section_names.append(i)

    print("missing sections: {}".format(missing_section_names))

    create_sections_in_course(course_id, missing_section_names)

    # get the full list of all secttions in this course
    # each section has an id and name
    all_sections_in_course=sections_in_course(course_id)

    sections_by_name=dict()
    for s in all_sections_in_course:
        sections_by_name[s['name']]=s['id']

    for  index, row in students_df.iterrows():
        section_name=row[name_of_column_with_section_assignments]
        if type(section_name) is str:
            enroll_student_in_section(course_id, row['user_id'], sections_by_name[section_name])
    
    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   
    write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

