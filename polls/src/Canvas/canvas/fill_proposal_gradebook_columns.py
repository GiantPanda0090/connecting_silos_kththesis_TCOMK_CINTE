import csv, requests, time
from pprint import pprint
import optparse
import sys
import fnmatch
from io import StringIO, BytesIO
from lxml import html
import json
import os
import io
import custom_column_data

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root


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


def fill_per_file(course_id , student,file_list):
    print ("student content: "+str(student))
    #current pushing student
    user_id = student['id']
    name_can=student['name']
    name=str(name_can).lower()
    email = student ['login_id']

    os.chdir(ROOT_DIR + "/../../../output/parse_result")
    print (str(os.getcwd()))

    print (str(file_list))
    for dir in file_list:
        # print os.getcwd()
      if dir !="cache" and dir!="log.txt":

        dir_constrct=str(dir).split('_')
        #['', 'Shiva Besharat Pour', 'Qi Li', 'f287b0f8-5173-11e8-9285-f0d5bf881ed6', '2018-05-06 21:25:06.686867']
        author_1=dir_constrct[1]
        author_2=dir_constrct[2]
        session_id=dir_constrct[3]
        custom_column_data.main(course_id, "session_id", user_id, str(session_id), 0)
        datetime=dir_constrct[4]
        print ("name: " + str(name))
        print ("author_1: " + str(author_1))
        print ("author_2: " + str(author_2))

        if name == author_1 or name==author_2:

            position=1
            os.chdir(os.getcwd()+"/"+dir)
            print ("dealing with folder:" + str(os.getcwd()+"/"+dir))
            json_content = {}
            with open('output.json') as f:

                json_content = json.load(f)
                f.close()
            if name != author_1:
                frontname = json_content ['author_1_frontname']
                aftername = json_content ['author_1_aftername']
                KTHusername = str(email).split("@")[0]
                pushing_name = frontname + ";" + aftername + ";" + KTHusername
                custom_column_data.main(course_id, "partner", user_id, pushing_name, 0)
            elif name != author_2:
                frontname = json_content ['author_2_frontname']
                aftername = json_content ['author_2_aftername']
                KTHusername = str(email).split("@")[0]
                pushing_name = frontname + ";" + aftername + ";" + KTHusername
                custom_column_data.main(course_id, "partner", user_id, pushing_name, 0)
            for root, dirs, files in os.walk("."):  # per folder
                    print (str(files))
                    current_author_group = []
                    for keys in json_content:
                        if keys != "heading" and keys !="Orignization_supervisor(en)" and keys !="log" and keys!="abstract(en)" and keys !="abstract(sv)" and keys != "introduction(en)" and keys != "Examiner" and keys !="Supervisor" and "author" not in keys and "givenName_" not in keys and "familyName_" not in keys:  # filename filter
                            print("obtaining info from file:"+str(os.getcwd())+"/"+keys)

                            info = json_content[keys]
                            column_name=keys
                            custom_column_data.main(course_id, str(column_name), user_id, info,position)
                            position+=1
            os.chdir("../")
            custom_column_data.main(course_id, "proceesed_date_time", user_id, str(datetime), position)
            break


    os.chdir(ROOT_DIR)

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

def main(course_id,file_list):
       global Verbose_Flag
       global remainder
       remainder=[]
       remainder.append(course_id)
       remainder.append(file_list)

       parser = optparse.OptionParser()
       parser.add_option('-v', '--verbose',
                         dest="verbose",
                         default=False,
                         action="store_true",
                         help="Print lots of output to stdout"
       )
       Verbose_Flag=False
       if Verbose_Flag:
              print('ARGV      :', sys.argv[1:])
              print('VERBOSE   :', options.verbose)
              print('REMAINING :', remainder)

       if (len(remainder) < 1):
              print("Inusffient arguments\n must provide course_id \n")
       else:
           users = getStudentInfo(remainder[0])
           for user in users:
               # epostContent = fill_Epost_column(remainder[0] , user)
               #
               # organizationContent = fill_Organization_column(remainder[0] , user)
               #
               # titleContent = fill_Title_column(remainder[0] , user)
               #
               # keywordsContent = fill_Keywords_column(remainder[0] , user)
               # supervisorContent = fill_Supervisor_column(remainder[0] , user)
               # examinorContent = fill_Examinor_column(remainder[0] , user)

               fill_per_file(remainder[0], user,remainder[1])

 
       print("\n--DONE--\n\n")

if __name__ == "__main__": main()

