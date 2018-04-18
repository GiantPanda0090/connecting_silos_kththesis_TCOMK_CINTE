#!/usr/bin/python3
#
# ./delete_section_by_id.py [section_id]+
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

def delete_section_by_id(section_id):
       # Use the Canvas API to delete the identified section
       #DELETE /api/v1/sections/:id

       url="https://"+configuration["canvas"]["host"]+"/api/v1/sections/" + '%s' % (section_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.delete(url, headers = header)

       if Verbose_Flag:
              write_to_log("result of deleting section: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return page_response
       return None


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
        print("Insuffient arguments\n must provide [section_id]+\n")
        return

    for i in range(0, len(remainder)):
           if Verbose_Flag:
                  print("argument[{0}]={1}".format(i, remainder[i]))
           delete_section_by_id(remainder[i])

    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   
    write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

