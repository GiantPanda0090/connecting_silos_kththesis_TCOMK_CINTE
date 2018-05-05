#!/usr/bin/python3
#
# ./insert_page2.py  course_id course_code module filename.html
# 
# This version actively transforms the page, by dealing with the URLs imbedded in the page.
#
# G. Q: Maguire Jr.
#
# 2016.06.27
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

list_of_all_files=None


def get_list_of_files_for_course(course_id):
    global list_of_all_files
    list_of_all_files=[]
    url = baseUrl + '%s/files' %(course_id)
    if Verbose_Flag:
       write_to_log("list of files for course " + course_id)

    # this will do a partial match against the module_name
    # This reducing the number of responses returned

    #payload = {'search_term': partial_file_name} 
    #r = requests.get(url, headers = header, data = payload)

    r = requests.get(url, headers = header)
    if Verbose_Flag:
       write_to_log(r.text)    

    files_response=r.json()
    for f_response in files_response:  
       list_of_all_files.append(f_response)

    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
    while r.links['current']['url'] != r.links['last']['url']:  
       r = requests.get(r.links['next']['url'], headers=header)  
       files_response = r.json()  
       for f_response in files_response:  
           list_of_all_files.append(f_response)

def file_id_from_file_name(course_id, filename):
    global list_of_all_files
    if list_of_all_files is None:
           get_list_of_files_for_course(course_id)

    name_to_match='%s' % (filename)
    if Verbose_Flag:
       print("filename" + "\t" + "id" + "\t" + "matching: "+ name_to_match)
    for f in list_of_all_files:
       if (f["filename"]  ==  name_to_match):
           if Verbose_Flag:
              print(f["filename"] + "\t" + str(f["id"]) + "\ttrue")
           file_id=f["id"]
           if Verbose_Flag:
              print("file_id is {}".format(file_id))
           return file_id
       else:
           if Verbose_Flag:
              print(f["filename"] + "\t" + str(f["id"]))

    return file_id





def write_to_log(message):

       with open(log_file, 'a') as log:
              log.write(message + "\n")
              pprint(message)


with open('transformed_urls.json') as json_url_file:
       transformed_urls = json.load(json_url_file)


def list_of_a_elements_with_URLS_in_page(tree, input_page):
    global transformed_urls_for_this_course
    global current_course_id
    list_of_As=tree.xpath('//div[@class="mainContent"]//div[@class="paragraphs"]//a')
    print("list_of_<a>s_in_page:")
    for e in list_of_As:
           print(e)
           print(e.attrib['href'])
           # setting the class to "auto_open instructure_scribd_file" - will cause the file to automatically be opened!
           e.attrib['class']=" instructure_scribd_file instructure_file_link"
           print(e.attrib['class'])
           # if you add the attribute target="_blank" to the link and it will open a new tab (https://community.canvaslms.com/thread/7267)
           try:
                  old_url=e.attrib['href']
                  if transformed_urls_for_this_course[old_url]:
                         filename=transformed_urls_for_this_course[old_url]
                         print("filename: {} ".format(filename))
                         # store the filename in the title attribute for the page
                         e.attrib['title']=filename

           except KeyError:
                     if Verbose_Flag:
                            print("no transformed URLs for {}".format(old_url))

    return list_of_As


# find the URLs in the page
def list_of_URLS_in_page(tree, input_page):
    list_of_URLs=tree.xpath('//div[@class="mainContent"]//div[@class="paragraphs"]//a/@href')
    print("list_of_URLS_in_page:")
    for e in list_of_URLs:
           print(e)
    return list_of_URLs

#page_to_insert=transform_page(page_to_insert,course_id, course_code, module_name, filename)
def transform_page(page_to_insert,course_id, course_code, module_name, filename, tree):
       global transformed_urls_for_this_course
       global current_course_id

       current_course_id=course_id # to indirectly pass this information to the link replacement function

       # if there are no entries for this course, asking for these URLS  will generate a KeyError
       try:
              transformed_urls_for_this_course=transformed_urls[course_code]
       except KeyError:
              if Verbose_Flag:
                     print("no transformed URLs for course code={}".format(course_code))
              transformed_urls_for_this_course={}
              transformed_urls[course_code]=transformed_urls_for_this_course

       transformed_page=page_to_insert

       list_of_a_elements_with_URLS_in_page(tree, page_to_insert)

       for u in list_of_URLS_in_page(tree, page_to_insert):
              transformed_page.rewrite_links(link_repl_func, resolve_base_href=True, base_href=None)

       return transformed_page

def link_repl_func(link):
       global transformed_urls_for_this_course
       global current_course_id

       try:
              if transformed_urls_for_this_course[link]:
                     filename=transformed_urls_for_this_course[link]
                     file_id=file_id_from_file_name(current_course_id, filename)
                     print("filename: {} has id: {}".format(filename, file_id))
                     return "https://kth.instructure.com/courses/11/files/"+str(file_id)+"/download?wrap=1"

              else:
                     return link
       except KeyError:
              if Verbose_Flag:
                     print("no transformed URLs for {}".format(link))
              return link


def create_module(course_id, module_name):
    module_id=None              # will contain the moudle's ID if it exists
    url = baseUrl + '%s/modules?module[name]=%s' %(course_id,module_name)
    if Verbose_Flag:
           write_to_log(course_id + module_name)
    r = requests.post(url, headers = header, data = payload)
    if Verbose_Flag:
           write_to_log(r.text)    
    if r.status_code == requests.codes.ok:
           modules_response=r.json()
           module_id=modules_response["id"]
           return module_id
    return  module_id

def check_for_module(course_id,  module_name):
    list_of_all_modules=[]
    module_id=None              # will contain the moudle's ID if it exists
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
    for m_response in modules_response:  
       list_of_all_modules.append(m_response)

    # the following is needed when the reponse has been paginated
    # i.e., when the response is split into pieces - each returning only some of the list of modules
    # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
    while r.links['current']['url'] != r.links['last']['url']:  
       r = requests.get(r.links['next']['url'], headers=header)  
       modules_response = r.json()  
       for m_response in modules_response:  
           list_of_all_modules.append(m_response)

    name_to_match='%s' % (module_name)
    if Verbose_Flag:
       print("name" + "\t" + "id" + "\t" + "matching: "+ name_to_match)
    for m in list_of_all_modules:
       if (m["name"]  ==  name_to_match):
           if Verbose_Flag:
              print(m["name"] + "\t" + str(m["id"]) + "\ttrue")
           module_id=m["id"]
           if Verbose_Flag:
              print("module_id is {}".format(module_id))
           return module_id
       else:
           if Verbose_Flag:
              print(m["name"] + "\t" + str(m["id"]))

    return module_id


def insert_page_info_module(course_id, course_code, module_name, filename):
    global Verbose_Flag
    module_id=check_for_module(course_id,  module_name)
    if (module_id is None):
       module_id=create_module(course_id,module_name)
       if Verbose_Flag:
           print("Module was created with module_id = {}".format(module_id))
    else:
       if Verbose_Flag:
           print("Module exists and has module_id = {}".format(module_id))


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

    # need to transform the page - for example replacing URLs and inserting files
    page_to_insert=paragraphs[0]
    page_to_insert=transform_page(page_to_insert,course_id, course_code, module_name, filename, tree)

    # Use the Canvas API to insert the page
    #PUT /api/v1/courses/:course_id/pages
    #    wiki_page[title]
    #    wiki_page[body]
    #    wiki_page[published]

    title=course_code+"-"+course_title[0]
    url = baseUrl + '%s/pages' % (course_id)
    if Verbose_Flag:
       print("url: " + url)
    payload={'wiki_page[title]': title, 'wiki_page[published]': False, 'wiki_page[body]': str(html.tostring(page_to_insert, pretty_print=True, method="html"), 'utf-8')}
    r = requests.post(url, headers = header, data=payload)
    write_to_log("result of post creating page: " + r.text)
    if r.status_code == requests.codes.ok:
       page_response=r.json()

       page_url=page_response["url"]
       #insert the newly created page as item into a module item
       # POST /api/v1/courses/:course_id/modules/:module_id/items
       # module_item[title]		string	
       #                                   The name of the module item and associated content
       #module_item[type]	Required	string	
       #                                   The type of content linked to the item
       #Allowed values:
       #       File, Page, Discussion, Assignment, Quiz, SubHeader, ExternalUrl, ExternalTool
       #module_item[content_id]	Required	string	
       #                                   The id of the content to link to the module item. Required, except for 'ExternalUrl', 'Page', and 'SubHeader' types.
       #module_item[position]		integer	
       #                                   The position of this item in the module (1-based).
       #module_item[indent]		integer	
       #                                   0-based indent level; module items may be indented to show a hierarchy
       #module_item[page_url]		string	
       #                                   Suffix for the linked wiki page (e.g. 'front-page'). Required for 'Page' type.  
       url = baseUrl + '%s/modules/%s/items' % (course_id, module_id)
       payload={'module_item[title]': title,
                'module_item[type]': 'Page',
                'module_item[page_url]': page_url}
       r = requests.post(url, headers = header, data=payload)
       write_to_log("result of inserting the item into the module: " + r.text)
       if r.status_code == requests.codes.ok:
           page_response=r.json()
           print("inserted page")
           return True
    return False

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

       if (len(remainder) < 4):
              print("Inusffient arguments\n must provide course_id course_code module filename.html\n")
       else:
              output=insert_page_info_module(remainder[0], remainder[1], remainder[2], remainder[3])
              if (output):
                     print(output)

       # save the updated list of transformed URLs
       with open('transformed_urls.json', 'w') as json_url_file:
              json.dump(transformed_urls, json_url_file)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

