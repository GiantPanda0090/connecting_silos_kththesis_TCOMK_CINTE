#!/usr/bin/python3
#
# ./mine_for_urls_in_page.py course_id course_code module filename.html
# 
# Extract the URLs from the mainContent part of a saved KTH Social page.
#
# Given a set of save KTH files in the directory
# a config.json file and
# a transformed_urls.json file
# 
# The config.json file contains the access token:
# {
#    "canvas":{
#        "access_token": "8..K"
#    }
#}
#
# The transformed_urls.json file
# can contain simply {}
#
#
# The program processes a html file and fetches all of the KTH Social files with the course code as a prefix
#
# for example: 
#   for i in ../*.html; do ../mine_for_urls_in_page.py  11 IK1552 Internetworking "$i"; done
#
# will process each of the files in turn, and output some text as it works:
# list_of_URLS_in_page:
# https://www.kth.se/social/files/553a6ea9f276542b61f29a55/IK1550-1552-Acronyms-list-20150424.xlsx
# new filename: IK1552-53a6ea9f276542b61f29a55-IK1550-1552-Acronyms-list-20150424.xlsx
# wget_cmd: wget -O IK1552-53a6ea9f276542b61f29a55-IK1550-1552-Acronyms-list-20150424.xlsx https://www.kth.se/social/files/553a6ea9f276542b61f29a55/IK1550-1552-Acronyms-list-20150424.xlsx
# --2016-07-01 13:25:55--  https://www.kth.se/social/files/553a6ea9f276542b61f29a55/IK1550-1552-Acronyms-list-20150424.xlsx
#Resolving www.kth.se (www.kth.se)... 130.237.28.40, 2001:6b0:1:11c2::82ed:1c28
# Connecting to www.kth.se (www.kth.se)|130.237.28.40|:443... connected.
# HTTP request sent, awaiting response... 200 OK
# Length: 18304 (18K) [application/vnd.openxmlformats-officedocument.spreadsheetml.sheet]
# Saving to: ‘IK1552-53a6ea9f276542b61f29a55-IK1550-1552-Acronyms-list-20150424.xlsx’
#
# IK1552-53a6ea9f2765 100%[=====================>]  17.88K  --.-KB/s   in 0.001s 
#
# 2016-07-01 13:25:55 (24.9 MB/s) - ‘IK1552-53a6ea9f276542b61f29a55-IK1550-1552-Acronyms-list-20150424.xlsx’ saved [18304/18304]
# ...
#
# G. Q: Maguire Jr.
#
# 2016.07.01
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

import subprocess

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


def mine_page_info_for_URLs(course_id, course_code, module_name, filename):
    global Verbose_Flag
    global transformed_urls

    with open(filename, 'r') as file_handle:          # get existing HTML page
        page_contents = file_handle.read()
    file_handle.closed

    tree = html.parse(StringIO(page_contents), html.HTMLParser())
    if Verbose_Flag:
        print(html.tostring(tree.getroot(), pretty_print=True, method="html"))

    mainContent=tree.xpath('//div[@class="mainContent"]')
    if len(mainContent) == 0:
       if Verbose_Flag:
           print("No mainContent - file {} is not from KTH Social".format(filename))
       return False

    if Verbose_Flag:
       print("mainContent: ")
       print(html.tostring(mainContent[0], pretty_print=True, method="html"))

    # The title of the page can be found in the <div class="mainContent"> in the <h1 class="title">
    course_title = tree.xpath('//div[@class="mainContent"]//h1[@class="title"]/text()')
    if Verbose_Flag:
       print("course_title: "+ course_title[0])

    # The actual content of the page can be found in the <div class="mainContent"> in the <div class="paragraphs">
    paragraphs= tree.xpath('//div[@class="mainContent"]//div[@class="paragraphs"]')
    if Verbose_Flag:
        print("paragraphs: ")
        print(html.tostring(paragraphs[0], pretty_print=True, method="html"))

    list_of_URLs=tree.xpath('//div[@class="mainContent"]//div[@class="paragraphs"]//a/@href')

     # if there are no entries for this course, asking for these URLS  will generate a KeyError
    try:
           transformed_urls_for_this_course=transformed_urls[course_code]
    except KeyError:
            if Verbose_Flag:
                   print("no transformed URLs for course code={}".format(course_code))
            transformed_urls_for_this_course={}
            transformed_urls[course_code]=transformed_urls_for_this_course

    print("list_of_URLS_in_page:")
    for e in list_of_URLs:
           print(e)
           # copy URLs from within KTH Social
           # use as the name of the file, the string after the prefix with "/" turned into "-"
           KTH_social_file_prefix="https://www.kth.se/social/files/"
           if e.startswith(KTH_social_file_prefix):
                  filename_offset=len(KTH_social_file_prefix)+1
                  filename_for_download=course_code+"-"+e[filename_offset:].replace("/", "-")
                  print("new filename: {}".format(filename_for_download))
                  transformed_urls[course_code][e]=filename_for_download
                  wget_cmd="wget -O "+ filename_for_download + " " + e
                  print("wget_cmd: "+wget_cmd)
                  return_code = subprocess.call(wget_cmd, shell=True)

    return False



def main():
       global Verbose_Flag
       global transformed_urls

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

       if (len(remainder) < 4):
              print("Inusffient arguments\n must provide course_id course_code module filename.html\n")
       else:
              with open('transformed_urls.json') as json_url_file:
                     transformed_urls = json.load(json_url_file)

              output=mine_page_info_for_URLs(remainder[0], remainder[1], remainder[2], remainder[3])
              if (output):
                     print(output)

       # save the updated list of transformed URLs
       with open('transformed_urls.json', 'w') as json_url_file:
              json.dump(transformed_urls, json_url_file)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       if Verbose_Flag:
              write_to_log(log_time)   
              write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

