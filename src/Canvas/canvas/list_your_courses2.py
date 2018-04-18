#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./list_your_courses2.py
# 
# to illustrate the use of the per_page parameter to get multiple answers per call to the API
#
# G. Q. Maguire Jr.
#
# 2017.02.27
#

import csv, requests, time
import pprint
import optparse
import sys

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
              pprint.pprint(message)


def list_your_courses():
       courses_found_thus_far=[]
       # Use the Canvas API to get the list of all of your courses
       # GET /api/v1/courses

       url = baseUrl
       if Verbose_Flag:
              print("url: " + url)

       extra_parameters={'per_page': '100'}
       r = requests.get(url, params=extra_parameters, headers = header)

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
              if Verbose_Flag:
                     write_to_log("result of getting courses for a paginated response: " + r.text)
              page_response = r.json()  
              for p_response in page_response:  
                     courses_found_thus_far.append(p_response)

       return courses_found_thus_far

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

       output=list_your_courses()
       if (output):
              pprint.pprint(output, indent=4)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

