#!/usr/bin/python3
#
# ./update_page_example1.py course_id page_name
#
# For example:
#    ./update_page_example1.py 11 test-page-for-updates
# should access the page:
#    https://kth.instructure.com/courses/11/pages/test-page-for-updates
# Do some change to the page and return it to Canvas.
# 
# G. Q: Maguire Jr.
#
# 2016.07.11
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

from copy import deepcopy

from textatistic import Textatistic
#############################
###### EDIT THIS STUFF ######
#############################

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


def create_module(course_id, module_name):
    url = baseUrl + '%s/modules?module[name]=%s' %(course_id,module_name)
    if Verbose_Flag:
           write_to_log(course_id + module_name)
    r = requests.post(url, headers = header, data = payload)
    if Verbose_Flag:
           write_to_log(r.text)    

def check_for_module(course_id,  module_name):
    url = baseUrl + '%s/modules' %(course_id)
    if Verbose_Flag:
           write_to_log("modules of " + course_id)

    # this will do a partial match against the module_name
    # This reducing the number of responses returned

    payload = {'search_term': module_name} 
    r = requests.get(url, headers = header, data = payload)
    if Verbose_Flag:
           write_to_log(r.text)    

    modules_response=r.json()

    name_to_match='%s' % (module_name)
    if Verbose_Flag:
           print("name" + "\t" + "id" + "\t" + "matching: "+ name_to_match)
    for m in modules_response:
       if (m["name"]  ==  name_to_match):
              if Verbose_Flag:
                     print(m["name"] + "\t" + str(m["id"]) + "\ttrue")
              return True
       else:
              if Verbose_Flag:
                     print(m["name"] + "\t" + str(m["id"]))

    return False

# page has the structure
#{
#  //the unique locator for the page
#  "url": "my-page-title",
#  //the title of the page
#  "title": "My Page Title",
#  //the creation date for the page
#  "created_at": "2012-08-06T16:46:33-06:00",
#  //the date the page was last updated
#  "updated_at": "2012-08-08T14:25:20-06:00",
#  //(DEPRECATED) whether this page is hidden from students (note: this is always
#  //reflected as the inverse of the published value)
#  "hide_from_students": false,
#  //roles allowed to edit the page; comma-separated list comprising a combination of
#  //'teachers', 'students', 'members', and/or 'public' if not supplied, course
#  //defaults are used
#  "editing_roles": "teachers,students",
#  //the User who last edited the page (this may not be present if the page was
#  //imported from another system)
#  "last_edited_by": null,
#  //the page content, in HTML (present when requesting a single page; omitted when
#  //listing pages)
#  "body": "<p>Page Content</p>",
#  //whether the page is published (true) or draft state (false).
#  "published": true,
#  //whether this page is the front page for the wiki
#  "front_page": false,
#  //Whether or not this is locked for the user.
#  "locked_for_user": false,
#  //(Optional) Information for the user about the lock. Present when locked_for_user
#  //is true.
#  "lock_info": null,
#  //(Optional) An explanation of why this is locked for the user. Present when
#  //locked_for_user is true.
#  "lock_explanation": "This page is locked until September 1 at 12:00am"
#}


def update_page_info_module(course_id, page_name):
    # Use the Canvas API to GET the page
    #GET /api/v1/courses/:course_id/pages/:url

       url = baseUrl + '%s/pages/%s' % (course_id, page_name)
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
              print("raw_text: {}".format(raw_text))

              title=page_response["title"]
       else:
              print("No page {}".format(page_name))
              return False

       # transform page

       GQMContent=document.xpath('//p[@class="GQMContent"]')
       if len(GQMContent) > 0:
              text_of_GQMContent = GQMContent[0].text
              print("Existing information as text is {}".format(text_of_GQMContent))

              information_for_on_page=json.loads(text_of_GQMContent)
              print("Existing information is {}".format(information_for_on_page))

              document2 = deepcopy(document)
              # trim off GQMContent paragraph before processing the raw_text
              for elem in document2.xpath( '//p[@class="GQMContent"]' ) :
                     elem.getparent().remove(elem)

              raw_text = document2.text_content()
              print("raw_text: {}".format(raw_text))

       information_for_on_page["Words"]=len(raw_text.split())
       information_for_on_page["Characters"]=len(raw_text)
       # see http://www.erinhengel.com/software/textatistic/
       information_for_on_page["Textatistic.counts"]=Textatistic(raw_text).counts
       information_for_on_page["Textatistic.statistics"]=Textatistic(raw_text).dict()

       if len(GQMContent) == 0:
              #no GQMContent found on this page so add some
              print("No GQMContent found - adding some")
              body = document.find('.//body')
              if body == None:
                     print("page has no <body>")
              else:
                     GQMContent_string='<p class="GQMContent">' + json.dumps(information_for_on_page) + "</p>"
              body.append(html.etree.XML(GQMContent_string))
              print("initial updated document {}", format(html.tostring(document)))
       else:       
              GQMContent[0].text=json.dumps(information_for_on_page)
              print("updated document {}", format(html.tostring(document)))



       # Use the Canvas API to insert the page
       #PUT /api/v1/courses/:course_id/pages/:uid
       #    wiki_page[title]
       #    wiki_page[published]
       #    wiki_page[body]


       url = baseUrl + '%s/pages/%s' % (course_id, page_name)
       if Verbose_Flag:
              print(url)
       payload={'wiki_page[title]': title, 'wiki_page[published]': False, 'wiki_page[body]': str(html.tostring(document, pretty_print=True, method="html"), 'utf-8')}
       r = requests.put(url, headers = header, data=payload)
       write_to_log(r.text)    
       print ("status code {}". format(r.status_code))
       if r.status_code == requests.codes.ok:
              return True
       else:
              print("Unable to update page {}".format(page_name))
              return False


def insert_page_info_module(course_id, course_code, module_name, filename):
    global Verbose_Flag
    module_found=check_for_module(course_id,  module_name)
    if (module_found == False):
        create_module(course_id,module_name)

    with open(filename, 'r') as file_handle:          # get existing HTML page
        page_contents = file_handle.read()
    file_handle.closed

    tree = html.parse(StringIO(page_contents), html.HTMLParser())
    if Verbose_Flag:
        print(html.tostring(tree.getroot(), pretty_print=True, method="html"))

    mainContent=tree.xpath('//div[@class="mainContent"]')
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

    # Use the Canvas API to insert the page
    #PUT /api/v1/courses/:course_id/pages
    #    wiki_page[title]
    #    wiki_page[body]
    #    wiki_page[published]

    title=course_code+"-"+course_title[0]
    url = baseUrl + '%s/pages' % (course_id)
    if Verbose_Flag:
           print(url)
    payload={'wiki_page[title]': title, 'wiki_page[published]': False, 'wiki_page[body]': str(html.tostring(paragraphs[0], pretty_print=True, method="html"), 'utf-8')}
    r = requests.post(url, headers = header, data=payload)
    write_to_log(r.text)    

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

    if (len(remainder) == 2):
        output=update_page_info_module(remainder[0], remainder[1])
        if (output):
            print(output)
    else:
        print("Inusffient arguments\n must provide course_id page_name\n")

    
    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   
    write_to_log("\n--DONE--\n\n")
   



if __name__ == "__main__": main()

