#!/usr/bin/python3
#
# ./delete_page.py  course_id page_title
# 
# G. Q: Maguire Jr.
#
# 2016.06.30
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

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


def delete_page(course_id, page_title):
       global page_titles_urls
       list_of_all_deleted_pages=[]

       # Use the Canvas API to get the list of pages for this course
       # DELETE /api/v1/courses/:course_id/pages/:url

       page_url=page_titles_urls[page_title]
       url = baseUrl + '%s/pages/%s' % (course_id,page_url)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.delete(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of deleting page: " + r.text)
       if r.status_code == requests.codes.ok:
              page_response=r.json()

              print("{} deleted".format(page_title))



def list_pages(course_id):
    global page_titles_urls
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
       page_titles_urls[p["title"]]=p["url"]
       if Verbose_Flag:
              print("url: {}".format(page_titles_urls[p["title"]]))


def main():
       global Verbose_Flag
       global page_titles_urls

       page_titles_urls={}      # a list of page title and URL for each page

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

       if (len(remainder) < 2):
              print("Inusffient arguments\n must provide course_id page_title\n")
       else:
              list_pages(remainder[0])
              output=delete_page(remainder[0],remainder[1])
              if (output):
                     print(output)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       if Verbose_Flag:
              write_to_log(log_time)   
              write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

