import csv, requests, time
from pprint import pprint
import optparse
import sys
import fnmatch
from io import StringIO, BytesIO
from lxml import html
import json
import os

# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       access_token=configuration["canvas"]["access_token"]
       baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/courses/"

header = {'Authorization' : 'Bearer ' + access_token}
payload = {}

def getStudentInfo(course_id):
    students = []

    url = baseUrl + '%s/users' % (course_id)
    extra_parameters={'enrollment_type[]': 'student', 'include[]': 'email, enrollments'}
    r = requests.get(url, params=extra_parameters, headers = header)
    results = r.json()

    for student in results:
        students.append(student)
    return students

def fill_Epost_column(course_id , student):
    user_id = student['id']
    email = student ['login_id']

    information = open('Epost.txt' , 'r')
    info = json.loads(information.read())
    column_id= info['id']  

    payload = {'column_data[content]' :  email , "user_id": user_id} 
    url = baseUrl + '%s/custom_gradebook_columns/%s/data/%s' % (course_id, column_id, user_id)
    print("url: " + url)
    requests.put(url, headers = header ,  data=payload)
 
def fill_Title_column(course_id , student):
    user_id = student['id']
    username = student['name']
    title = None

    information = open('Title.txt' , 'r')
    info = json.loads(information.read())
    column_id= info['id']

    current_Directory = os.getcwd()
    os.chdir( current_Directory + '/../../../output/parse_result')
    parse_result =os.getcwd()
    for parseFolder in os.listdir(parse_result):
        if username in parseFolder:
            proposalFolder = os.path.join(parse_result , parseFolder)
            for file in os.listdir(proposalFolder):
                if 'title' in file:
                    titleFile = os.path.join(proposalFolder, file)
                    result = open(titleFile , 'r')
                    title = result.read()
          
    payload = {'column_data[content]' :  title , "user_id": user_id} 
    url = baseUrl + '%s/custom_gradebook_columns/%s/data/%s' % (course_id, column_id, user_id)
    print("url: " + url)
    requests.put(url, headers = header ,  data=payload)

def fill_Organization_column(course_id , student):
    user_id = student['id']
    username = student['name']
    organization = None

    information = open('associations.txt' , 'r')
    info = json.loads(information.read())
    column_id= info['id']

    current_Directory = os.getcwd()
    os.chdir( current_Directory + '/../../../output/parse_result')
    parse_result =os.getcwd()
    for parseFolder in os.listdir(parse_result):
        if username in parseFolder:
            proposalFolder = os.path.join(parse_result , parseFolder)
            for file in os.listdir(proposalFolder):
                if file == 'Orgnization.txt':
                    organizationFile = os.path.join(proposalFolder, file)
                    result = open(organizationFile , 'r')
                    organization = result.read() 

    payload = {'column_data[content]' :  organization , "user_id": user_id} 
    url = baseUrl + '%s/custom_gradebook_columns/%s/data/%s' % (course_id, column_id, user_id)
    print("url: " + url)
    requests.put(url, headers = header ,  data=payload)

def fill_Keywords_column(course_id , student):
    user_id = student['id']
    username = student['name']
    keywords = None

    information = open('keyterms.txt' , 'r')
    info = json.loads(information.read())
    column_id= info['id']

    current_Directory = os.getcwd()
    os.chdir( current_Directory + '/../../../output/parse_result')
    parse_result =os.getcwd()
    for parseFolder in os.listdir(parse_result):
        if username in parseFolder:
            proposalFolder = os.path.join(parse_result , parseFolder)
            for file in os.listdir(proposalFolder):
                if 'Keyword' in file:
                    keywordFile = os.path.join(proposalFolder, file)
                    result = open(keywordFile , 'r')
                    keywords = result.read()   

    payload = {'column_data[content]' :  keywords , "user_id": user_id} 
    url = baseUrl + '%s/custom_gradebook_columns/%s/data/%s' % (course_id, column_id, user_id)
    print("url: " + url)
    requests.put(url, headers = header ,  data=payload)

def fill_Supervisor_column(course_id , student):
    user_id = student['id']
    username = student['name']
    supervisor = None

    information = open('handledare.txt' , 'r')
    info = json.loads(information.read())
    column_id= info['id']

    current_Directory = os.getcwd()
    os.chdir( current_Directory + '/../../../output/parse_result')
    parse_result =os.getcwd()
    for parseFolder in os.listdir(parse_result):
        if username in parseFolder:
            proposalFolder = os.path.join(parse_result , parseFolder)
            for file in os.listdir(proposalFolder):
                if file == 'Supervisor.txt':
                    supervisorFile = os.path.join(proposalFolder, file)
                    result = open(supervisorFile , 'r')
                    supervisor = result.read()

    payload = {'column_data[content]' :  supervisor , "user_id": user_id} 
    url = baseUrl + '%s/custom_gradebook_columns/%s/data/%s' % (course_id, column_id, user_id)
    print("url: " + url)
    requests.put(url, headers = header ,  data=payload)

def fill_Examinor_column(course_id , student):
    user_id = student['id']
    username = student['name']
    examinor = None

    information = open('examinator.txt' , 'r')
    info = json.loads(information.read())
    column_id= info['id']

    current_Directory = os.getcwd()
    os.chdir( current_Directory + '/../../../output/parse_result')
    parse_result =os.getcwd()
    for parseFolder in os.listdir(parse_result):
        if username in parseFolder:
            proposalFolder = os.path.join(parse_result , parseFolder)
            for file in os.listdir(proposalFolder):
                if 'Examiner' in file:
                    examinorFile = os.path.join(proposalFolder, file)
                    result = open(examinorFile , 'r')
                    examinor = result.read()
     
    payload = {'column_data[content]' :  examinor , "user_id": user_id} 
    url = baseUrl + '%s/custom_gradebook_columns/%s/data/%s' % (course_id, column_id, user_id)
    print("url: " + url)
    requests.put(url, headers = header ,  data=payload)

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


       if (len(remainder) < 1):
              print("Inusffient arguments\n must provide course_id \n")
       else:
           users = getStudentInfo(remainder[0])
           for user in users:
               epostContent = fill_Epost_column(remainder[0] , user)

               organizationContent = fill_Organization_column(remainder[0] , user)

               titleContent = fill_Title_column(remainder[0] , user)

               keywordsContent = fill_Keywords_column(remainder[0] , user)
               supervisorContent = fill_Supervisor_column(remainder[0] , user)
               examinorContent = fill_Examinor_column(remainder[0] , user)

 
       print("\n--DONE--\n\n")

if __name__ == "__main__": main()

