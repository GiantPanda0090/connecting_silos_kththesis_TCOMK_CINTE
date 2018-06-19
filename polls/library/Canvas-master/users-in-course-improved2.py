#!/usr/bin/python3
#
# ./users-in-course-improved2.py course_id
#
# outputs a list of users in a course as an xlsx file of the form: users-in-189.xlsx
# the second sheet "Students" lists students together with their e-mail address
#
# Based on list_users_in_course_with_students_email.py
#
# Extensive use is made of Python Pandas merge operations.
# 
# G. Q. Maguire Jr.
#
# 2017.01.12
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

# Use Python Pandas to create XLSX files
import pandas as pd

# Import urlopen() for either Python 2 or 3.
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from PIL import Image

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


def list_peer_review_assignments(course_id, assignment_id):
       peer_review_assignments_found_thus_far=[]

       # Use the Canvas API to get the list of peer reviewing assignments
       # a given assignment for a course:
       #GET /api/v1/courses/:course_id/assignments/:assignment_id/peer_reviews
       
       url = baseUrl + '%s/assignments/%s/peer_reviews' % (course_id, assignment_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting peer review assignments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              peer_review_assignments_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            peer_review_assignments_found_thus_far.append(p_response)

       return peer_review_assignments_found_thus_far

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



def summarize_assignments(list_of_assignments):
       summary_of_assignments={}
       for assignm in list_of_assignments:
              summary_of_assignments[assignm['id']]=assignm['name']

       print("summary_of_assignments={}".format(summary_of_assignments))

def list_assignments(course_id):
       assignments_found_thus_far=[]

       # Use the Canvas API to get the list of assignments for the course
       #GET /api/v1/courses/:course_id/assignments

       url = baseUrl + '%s/assignments' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting assignments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              assignments_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     assignments_found_thus_far.append(p_response)

       return assignments_found_thus_far


def list_custom_column_entries(course_id, column_number):
       entries_found_thus_far=[]

       # Use the Canvas API to get the list of custom column entries for a specific column for the course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns/:id/data

       url = baseUrl + '%s/custom_gradebook_columns/%s/data' % (course_id, column_number)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting custom_gradebook_columns: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              entries_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     entries_found_thus_far.append(p_response)

       return entries_found_thus_far




def list_custom_columns(course_id):
       columns_found_thus_far=[]

       # Use the Canvas API to get the list of custom column for this course
       #GET /api/v1/courses/:course_id/custom_gradebook_columns

       url = baseUrl + '%s/custom_gradebook_columns' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting custom_gradebook_columns: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              columns_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              page_response = r.json()  
              for p_response in page_response:  
                     columns_found_thus_far.append(p_response)

       return columns_found_thus_far



def insert_column_name(course_id, column_name):
    global Verbose_Flag

    # Use the Canvas API to Create a custom gradebook column
    # POST /api/v1/courses/:course_id/custom_gradebook_columns
    #   Create a custom gradebook column
    # Request Parameters:
    #Parameter		Type	Description
    #column[title]	Required	string	no description
    #column[position]		integer	The position of the column relative to other custom columns
    #column[hidden]		boolean	Hidden columns are not displayed in the gradebook
    # column[teacher_notes]		boolean	 Set this if the column is created by a teacher. The gradebook only supports one teacher_notes column.

    url = baseUrl + '%s/custom_gradebook_columns' % (course_id)
    if Verbose_Flag:
       print("url: " + url)
    payload={'column[title]': column_name}
    r = requests.post(url, headers = header, data=payload)
    write_to_log("result of post creating custom column: " + r.text)
    if r.status_code == requests.codes.ok:
       write_to_log("result of inserting the item into the module: " + r.text)
       if r.status_code == requests.codes.ok:
           page_response=r.json()
           print("inserted column")
           return True
    return False

def users_in_course(course_id):
       user_found_thus_far=[]

       # Use the Canvas API to get the list of users enrolled in this course
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
              user_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            user_found_thus_far.append(p_response)
       return user_found_thus_far

def students_in_course2(course_id):
       user_found_thus_far=[]

       # Use the Canvas API to get the list of users enrolled in this course
       #GET /api/v1/courses/:course_id/users

       url = baseUrl + '%s/users' % (course_id)
       if Verbose_Flag:
              print("url: " + url)

       extra_parameters={'enrollment_type[]': 'student', 'include[]': 'email'}
       r = requests.get(url, params=extra_parameters, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              user_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       if 'link' in r.headers:
              while r.links['current']['url'] != r.links['last']['url']:  
                     r = requests.get(r.links['next']['url'], headers=header)  
                     page_response = r.json()  
                     for p_response in page_response:  
                            user_found_thus_far.append(p_response)
       return user_found_thus_far

def users_communication_channel(user_id):
       page_response=[]
       # Use the Canvas API to get the user's communication channel(s)
       #GET /api/v1/users/:user_id/communication_channels

       url = baseUrlUsers + '%s/communication_channels' % (user_id)
       if Verbose_Flag:
              print("url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting communication_channels: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       return page_response

def user_profile_url(user_id):
       # Use the Canvas API to get the profile of a user
       #GET /api/v1/users/:user_id/profile

       url = baseUrlUsers + '%s/profile' % (user_id)
       if Verbose_Flag:
              print("user url: " + url)

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              write_to_log("result of getting enrollments: " + r.text)

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       return page_response

# based upon answer by RoMA on Oct 8 '08 at 10:09 in http://stackoverflow.com/questions/181596/how-to-convert-a-column-number-eg-127-into-an-excel-column-eg-aa
def ColIdxToXlName(idx):
    if idx < 1:
        raise ValueError("Index is too small")
    result = ""
    while True:
        if idx > 26:
            idx, r = divmod(idx - 1, 26)
            result = chr(r + ord('A')) + result
        else:
            return chr(idx + ord('A') - 1) + result


# from KobeJohn on Nov 12 '15 at 15:36 at http://stackoverflow.com/questions/33672833/set-width-and-height-of-an-image-when-inserting-via-worksheet-insert-image

def calculate_scale(im_size, bound_size):
    original_width, original_height = im_size

    # calculate the resize factor, keeping original aspect and staying within boundary
    bound_width, bound_height = bound_size
    ratios = (float(bound_width) / original_width, float(bound_height) / original_height)
    return min(ratios)

def main():
    global Verbose_Flag
    global Picture_Flag

    default_picture_size=128

    parser = optparse.OptionParser(usage="usage: %prog [options] filename")

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
                  )

    parser.add_option('-p', '--pictures',
                      dest="pictures",
                      default=False,
                      action="store_true",
                      help="Include pictures from user's avatars"
                  )

    parser.add_option("-s", "--size",
                  action="store",
                  dest="picture_size",
                  default=default_picture_size,
                  help="size of picture in pixels",)

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    Picture_Flag=options.pictures
    Picture_size=int(options.picture_size)
    # if a size is specified, but the picture option is not set, then set it automatically
    if Picture_size > 1:
        Picture_Flag=True

    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)
        print('Pictures  :', Picture_Flag)
        print('Pictures  :', Picture_Flag)

    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide course_id\n")
        return

    course_id=remainder[0]

    users=users_in_course(course_id)
    users_df1=pd.io.json.json_normalize(users)

    sections_df=pd.io.json.json_normalize(sections_in_course(course_id))
    sections_df.rename(columns = {'id':'course_section_id', 'name':'section_name'}, inplace = True)
    columns_to_drop=['course_id', 'end_at', 'integration_id', 'nonxlist_course_id', 'sis_course_id', 'sis_section_id', 'start_at']
    sections_df.drop(columns_to_drop,inplace=True,axis=1)
    headers = sections_df.columns.tolist()
    if Verbose_Flag:
        print('sections_df columns: ', headers)

    users_df = pd.merge(sections_df, users_df1, on='course_section_id')


    for index, row in  users_df.iterrows():
        if Verbose_Flag:
            print('index: ', index, 'row[user_id]: ', row['user_id'])
                                
        profiles=user_profile_url(row['user_id'])
        users_df.set_value(index, 'avatar_url', profiles['avatar_url'])

        #"address":"chip.maguire@gmail.com","type":"email"}]
        comm_channel=users_communication_channel(row['user_id'])
        if Verbose_Flag:
            print('comm channels: ', len(comm_channel))

        for commchannel in comm_channel:
            if Verbose_Flag:
                print('commchannel: ', commchannel)
                print('commchannel[position]: ', commchannel['position'])
                print('commchannel[address]: ', commchannel['address'])
                print('commchannel[type]: ', commchannel['type'])
                print('commchannel[workflow_state]: ', commchannel['workflow_state'])
            users_df.set_value(index, 'comm_channel_address'+str(commchannel['position']), commchannel['address'])
            users_df.set_value(index, 'comm_channel_type'+str(commchannel['position']), commchannel['type'])
            users_df.set_value(index, 'comm_channel_workflow_state'+str(commchannel['position']), commchannel['workflow_state'])

    students=students_in_course2(course_id)
    students_df=pd.io.json.json_normalize(students)

    students_df['comm_channel_address']=""
    students_df['comm_channel_type']=""

    for index, row in  students_df.iterrows():
        if Verbose_Flag:
            print('index: ', index, 'row[id]: ', row['id'])
                                
        profiles=user_profile_url(row['id'])
        students_df.set_value(index, 'avatar_url', profiles['avatar_url'])

        #"address":"chip.maguire@gmail.com","type":"email"}]
        comm_channel=users_communication_channel(row['id'])
        for commchannel in comm_channel:
            if Verbose_Flag:
                print('commchannel: ', commchannel)
                print('commchannel[position]: ', commchannel['position'])
                print('commchannel[address]: ', commchannel['address'])
                print('commchannel[type]: ', commchannel['type'])
                print('commchannel[workflow_state]: ', commchannel['workflow_state'])
            students_df.set_value(index, 'comm_channel_address'+str(commchannel['position']), commchannel['address'])
            students_df.set_value(index, 'comm_channel_type'+str(commchannel['position']), commchannel['type'])
            students_df.set_value(index, 'comm_channel_workflow_state'+str(commchannel['position']), commchannel['workflow_state'])

    # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
    # set up the output write
    writer = pd.ExcelWriter('users-in-'+str(course_id)+'.xlsx', engine='xlsxwriter')


    # Here is the place to drop any columns that you do not want
    columns_to_drop=['associated_user_id', 'section_integration_id', 'sis_account_id', 'sis_course_id', 'sis_section_id', 'user.integration_id']
    users_df.drop(columns_to_drop,inplace=True,axis=1)


    if Picture_Flag:
        users_df['pictures']=''
        #headers = users_df.dtypes.index
        headers = users_df.columns.tolist()
        if Verbose_Flag:
            print('users_df columns: ', headers)
        column_for_pictures_of_users=ColIdxToXlName(len(headers) + 1)

    users_df.to_excel(writer, sheet_name='Users')

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets['Users']
              
    if Picture_Flag:
        # Widen the picture column to hold the images
        worksheet.set_column(column_for_pictures_of_users+':'+column_for_pictures_of_users, 25)


        # set the row slightly larger than the pictures
        maxsize = (Picture_size, Picture_size)
        worksheet.set_default_row(Picture_size+2)
        # set the heading row to be only 25 units high
        worksheet.set_row(0, 20)


        for index, row in  users_df.iterrows():
            avatar_url=row['avatar_url']
            if Verbose_Flag:
                print('index: ', index, 'avatar_url: ', avatar_url)
            if len(avatar_url) > 0:
                http_reponse=urlopen(avatar_url)
                if Verbose_Flag:
                    print('http_reponse: ', http_reponse.info())
                im = Image.open(http_reponse)
                if Verbose_Flag:
                    print('im: ', im.size)
                resize_scale=calculate_scale(im.size, maxsize)
                if Verbose_Flag:
                    print('resize_scale: ', resize_scale)

                image_data = BytesIO(urlopen(avatar_url).read())
                if Verbose_Flag:
                    print('image_data: ', image_data)
                # im.thumbnail(maxsize, Image.ANTIALIAS)

                # need to increase the index because the first user is in the row indexed by 0, but this has to be in the second row of the Excel spreadhsheet
                if Verbose_Flag:
                    print('column_for_pictures_of_users+str(index+2): ', column_for_pictures_of_users+str(index+2))
                worksheet.insert_image(column_for_pictures_of_users+str(index+2), avatar_url, {'image_data': image_data, 'x_scale': resize_scale, 'y_scale': resize_scale})

    students_df.to_excel(writer, sheet_name='Students')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    # add time stamp to log file
    log_time = str(time.asctime(time.localtime(time.time())))
    write_to_log(log_time)   
    write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

