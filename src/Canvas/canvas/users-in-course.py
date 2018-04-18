#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./users-in-course.py course_id
# 
# outputs a CSV file with column headings = ['user_id', 'role', 'course section', 'sort last_name', 'sort first_name', 'e-mail', 'html_url', 'picture']
#
# Import (using the Text IMport Wizard)  into a blank Excel spreadsheet using the Data->Get External Data->From Text.
#  Make sure to specify that the import and specify that the File Origin is "UTF-8".
#
# If you want to sort by section number or some other fields, do so now.
#
# In Excel one can selected the column of picture (actually the URL to the user's icon/picture, then you can select this column and they use the following Vistual Basic
# subroutine:
#  Sub InsertPicturesViaURL()
#    For Each cel In Selection
#        cel.Offset(0, 1).Select
#        ActiveSheet.Pictures.Insert(cel.Value).Select
#    Next cel
#  End Sub
#
# The above will insert the pictures. Now you can use the Excel menu "Find & Select" -> "Go To Special" choose "Object". This selects all of the picture objects,
# now you can use the "Picture Tools" menu to set the size of the images (for example to 1 cm). Now use the Cells Format menu to set the row height to 75.
# You now have small versions of the picture in spreadsheet.
#
# Note that since the actual graphical images are in an overlay, they will _not_ sort with the entries in the spreadsheet.
#
# G. Q. Maguire Jr.
#
# 2016.11.26
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
       baseUrluser="https://"+configuration["canvas"]["host"]+"/api/v1/users/"

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

# create the following dict to use as an associate directory about users
selected_user_data={}

user_found_thus_far=[]

def users_in_course(course_id):
       global user_found_thus_far

       # Use the Canvas API to get the list of users enrolled in this course
       #GET /api/v1/courses/:course_id/enrollments

       url = baseUrl + '%s/enrollments' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              user_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     user_found_thus_far.append(p_response)
       return user_found_thus_far

def user_profile_url(user_id):
       # Use the Canvas API to get the profile of a user
       #GET /api/v1/users/:user_id/profile

       url = baseUrluser + '%s/profile' % (user_id)
       if Verbose_Flag:
              print("user url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       return page_response

sections_info=[]
def section_name_from_section_id(section_id): 
       global sections_info
       for i in sections_info:
            if i['id'] == section_id:
                   return i['name']


def output_spreadsheet_of_users_in_a_course(course_id):
       global sections_info
       sections_info=sections_in_course(course_id)
       if Verbose_Flag:
              print("sections_info: {}".format(sections_info))

       users=users_in_course(course_id)
       output_file  = open('enrollment-in-'+course_id+'.csv', "wb")
       print ("Name of the file: ", output_file.name)

       #output column headings
       headings = ['user_id', 'role', 'course section', 'sort last_name', 'sort first_name', 'e-mail', 'html_url', 'picture']
       for h in headings:
              output_file.write(h.encode())
              output_file.write(",".encode())
       output_file.write("\n".encode())

       if Verbose_Flag:
              print("user_found_thus_far: {}".format(users))

       for user in users:
              if Verbose_Flag:
                     print("user: {}".format(user))
                     print("user: {}".format(user['user_id']))

              user_id=user['user_id']
              if Verbose_Flag:
                     print("user_id: {}".format(user_id))

              output_file.write(str(user['user_id']).encode())
              output_file.write(",".encode())
              output_file.write(user['role'].encode())
              output_file.write(",".encode())
              output_file.write(section_name_from_section_id(user['course_section_id']).encode())
              output_file.write(",".encode())
              output_file.write(user['user']['sortable_name'].encode())
              output_file.write(",".encode())
              output_file.write(user['user']['login_id'].encode())
              output_file.write(",".encode())
              output_file.write(user['html_url'].encode())
              output_file.write(",".encode())
              profiles=user_profile_url(user_id)
              if Verbose_Flag:
                     print("profiles: {}".format(profiles['avatar_url']))
              output_file.write(profiles['avatar_url'].encode())
              output_file.write("\n".encode())

       output_file.close()


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

       if (len(remainder) < 1):
              print("Insuffient arguments\n must provide course_id\n")
       else:
              output=output_spreadsheet_of_users_in_a_course(remainder[0])
              if (output):
                     print(output)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

