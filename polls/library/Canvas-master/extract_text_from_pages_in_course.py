#!/usr/bin/python3
#
# ./extract_text_from_pages_in_course.py  course_id
# 
# output text for each page in a course, the output file will be the name of the page with suffix ".txt"
#
# G. Q: Maguire Jr.
#
# 2016.07.14
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from lxml import html

import json
from textatistic import Textatistic
#############################
###### EDIT THIS STUFF ######
#############################

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       access_token=configuration["canvas"]["access_token"]


modules_csv = 'modules.csv' # name of file storing module names
log_file = 'log.txt' # a log file. it will log things
baseUrl = 'https://kth.instructure.com/api/v1/courses/' # changed to KTH domain
header = {'Authorization' : 'Bearer ' + access_token}
payload = {}


##############################################################################
## ONLY update the code below if you are experimenting with other API calls ##
##############################################################################


def write_to_log(message):
       with open(log_file, 'a') as log:
              log.write(message + "\n")
              pprint(message)


def extract_text_from_pages_in_course(course_id):
       list_of_all_pages=[]

       # Use the Canvas API to get the list of pages for this course
       #GET /api/v1/courses/:course_id/pages

       url = baseUrl + '%s/pages' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting pages: " + r.text)
       if r.status_code == requests.codes.ok:
              page_response=r.json()
       else:
              print("No pages for course_id: {}".format(course_id))
              return False


       for p_response in page_response:  
              list_of_all_pages.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     list_of_all_pages.append(p_response)

       for p in list_of_all_pages:
              print("{}".format(p["title"]))
              # Use the Canvas API to GET the page
              #GET /api/v1/courses/:course_id/pages/:url

              url = baseUrl + '%s/pages/%s' % (course_id, p["url"])
              if Verbose_Flag:
                     print(url)
              payload={}
              r = requests.get(url, headers = header, data=payload)
              if r.status_code == requests.codes.ok:
                     page_response = r.json()  
                     if Verbose_Flag:
                            print("body: {}".format(page_response["body"]))

                     document = html.document_fromstring(page_response["body"])
                     raw_text = document.text_content()
                     if Verbose_Flag:
                            print("raw_text: {}".format(raw_text))
              else:
                     print("No pages for course_id: {}".format(course_id))
                     return False

              # see http://www.erinhengel.com/software/textatistic/
              # there is no sense processing files that do not have text in them
              if len(raw_text) > 0:
                     try:
                            page_url=page_response["url"]
                            tail_of_page_url=page_url[page_url.rfind("/")+1:]
                            with open('extractedtext'+course_id+'-'+tail_of_page_url+'.txt', "wb") as writer:
                                   # put a distinct header line in so that one can concatinate all of the extracted text and feed it to Word or other systems for spelling and grammar checking
                                   header_line="\n<<<<<<<<<<"+course_id+'-'+tail_of_page_url+'>>>>>>>>>>\n'
                                   encoded_output=bytes(header_line, 'UTF-8')
                                   writer.write(encoded_output)
                                   #
                                   # now output the text that came from the page
                                   #
                                   encoded_output=bytes(raw_text, 'UTF-8')
                                   writer.write(encoded_output)
                                   writer.close()
                            continue
                     except IOError as e:
                            print("for filename: {0} I/O error({1}): {2}".format(fixed_title, e.errno, e.strerror))
                            continue
              else:
                     continue
       return True

def list_pages(course_id):
    list_of_all_pages=[]

    # Use the Canvas API to get the list of pages for this course
    #GET /api/v1/courses/:course_id/pages

    url = baseUrl + '%s/pages' % (course_id)
    if Verbose_Flag:
       print("url: " + url)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
           write_to_log("result of getting pages: " + r.text)
    if r.status_code == requests.codes.ok:
       page_response=r.json()

    for p_response in page_response:  
       list_of_all_pages.append(p_response)

    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
    while r.links['current']['url'] != r.links['last']['url']:  
       r = requests.get(r.links['next']['url'], headers=header)  
       page_response = r.json()  
       for p_response in page_response:  
           list_of_all_pages.append(p_response)

    for p in list_of_all_pages:
       print("{}".format(p["title"]))


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
       if Verbose_Flag:
              write_to_log(log_time)   

       if (len(remainder) < 1):
              print("Inusffient arguments\n must provide course_id\n")
       else:
              course_id=remainder[0]
              output=extract_text_from_pages_in_course(course_id)

              if (output):
                     if Verbose_Flag:
                            print(output)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       if Verbose_Flag:
              write_to_log(log_time)   
              write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

