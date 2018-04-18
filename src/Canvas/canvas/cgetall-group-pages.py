#!  /usr/bin/env python3
#
# ./cgetall-group-pages.py  canvas_page_url or group_id
# 
# get all of the Canvas group pages with a given base URL or for a given group_id
#
#
# Example:
#   cgetall-group-pages.py 5815
#
#  both get all of the group pages for group 5815 
#
# G. Q: Maguire Jr.
#
# 2017.03.16
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from lxml import html

import json
#############################
###### EDIT THIS STUFF ######
#############################

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       canvas = configuration['canvas']
       access_token= canvas["access_token"]
       # access_token=configuration["canvas"]["access_token"]
       #baseUrl = 'https://kth.instructure.com/api/v1/courses/' # changed to KTH domain
       baseUrl = 'https://%s/api/v1/groups/' % canvas.get('host', 'kth.instructure.com')
       header = {'Authorization' : 'Bearer ' + access_token}



#modules_csv = 'modules.csv' # name of file storing module names
log_file = 'log.txt' # a log file. it will log things


def write_to_log(message):
       with open(log_file, 'a') as log:
              log.write(message + "\n")
              pprint(message)

def list_pages(group_id):
       list_of_all_pages=[]

       # Use the Canvas API to get the list of pages for this course
       #GET /api/v1/courses/:group_id/pages

       url = baseUrl + '%s/pages' % (group_id)
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

       if Verbose_Flag:
              for p in list_of_all_pages:
                     print("{}".format(p["title"]))

       return list_of_all_pages

def getall_group_pages(group_id):
       for p in list_pages(group_id):
              url = baseUrl + '%s/pages/%s' % (group_id, p["url"])
              if Verbose_Flag:
                     print(url)
              payload={}
              r = requests.get(url, headers = header, data=payload)
              if Verbose_Flag:
                     print("r.status_code: {}".format(r.status_code))
              if r.status_code == requests.codes.ok:
                     page_response = r.json()

                     type_of_contents=type(page_response["body"])
                     if Verbose_Flag:
                            print("type_of_contents: {}".format(type_of_contents))
                     if type_of_contents == type(None):
                            continue
                     new_file_name=p["url"][p["url"].rfind("/")+1:]+'.html'
                     if Verbose_Flag:
                            print("new_file_name: {}".format(new_file_name))

                     # write out body of response as a .html page
                     with open(new_file_name, 'wb') as f:
                            encoded_output = bytes(page_response["body"], 'UTF-8')
                            f.write(encoded_output)
                     continue
              else:
                     print("No such page: {}".format(canvas_group_page_url))
                     continue

       return True


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
              print("Insuffient arguments\n must provide url or group_id\n")
       else:
              canvas_group_page_url=remainder[0]

       if canvas_group_page_url.find("http") >= 0:
              #extract group_id from URL
              group_id=canvas_group_page_url[canvas_group_page_url.find("groups/")+7:canvas_group_page_url.find("pages/")-1]
       else:
              group_id=remainder[0]
              
       if Verbose_Flag:
              print("group_id: {}".format(group_id))

       output=getall_group_pages(group_id)
       if (output):
              if Verbose_Flag:
                     pprint(output)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       if Verbose_Flag:
              write_to_log(log_time)   
              write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

