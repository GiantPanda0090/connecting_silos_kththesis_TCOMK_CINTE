#!/usr/bin/python3
#
# ./list_sections_in_course.py course_id
#
# outputs a spreadsheet of the section in a course as an xlsx file of the form: sections-in-189.xlsx
# the second sheet "Students" lists students
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
              r = requests.put(url, headers = header, data=payload)

       r = requests.put(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of putting sections: " + r.text)

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

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide course_id\n")
        return

    course_id=remainder[0]

    sections_df=pd.io.json.json_normalize(sections_in_course(course_id))
    sections_df.rename(columns = {'id':'course_section_id', 'name':'section_name'}, inplace = True)
    columns_to_drop=['course_id', 'end_at', 'integration_id', 'nonxlist_course_id', 'sis_course_id', 'sis_section_id', 'start_at']
    sections_df.drop(columns_to_drop,inplace=True,axis=1)
    headers = sections_df.columns.tolist()
    if Verbose_Flag:
        print('sections_df columns: ', headers)

    students=students_in_course(course_id)
    students_df1=pd.io.json.json_normalize(students)

    headers = sections_df.columns.tolist()
    if Verbose_Flag:
        print('sections_df columns: ', headers)

    students_df = pd.merge(sections_df, students_df1, on='course_section_id')
    columns_to_drop=['associated_user_id', 'course_integration_id', 'grades.current_grade', 'grades.current_score', 'grades.final_grade',
                     'grades.final_score', 'grades.html_url', 'html_url', 'start_at', 'user.integration_id' ]
    students_df.drop(columns_to_drop,inplace=True,axis=1)


    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter('sections-in-'+str(course_id)+'.xlsx', engine='xlsxwriter')
    sections_df.to_excel(writer, sheet_name='Sections')
    students_df.to_excel(writer, sheet_name='Students')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   
    write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

