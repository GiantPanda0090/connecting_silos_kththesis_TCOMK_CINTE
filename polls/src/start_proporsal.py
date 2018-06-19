#!/usr/bin/python
""" main run file
Usage: start_proprosal.py.main(course_id,assignment_id,document_type,user_id_list)
This file is a library. not recomand to call directly

------------


Modified on 2018.05.12
@author: Qi LI.

This is the main sequence of the program
This is triggered from views.py

20180512 remove selenium and replace with Dr Gerald download sequence

------------
"""

import platform
import urllib2
import json

from parse.kth_extract.pdfssa4met import kthextract
from Canvas.canvas import fill_proposal_gradebook_columns
from Canvas.canvas.list_custom_columns import *
from Canvas.canvas import list_custom_columns
from Canvas.canvas.list_custom_column_entries import *

from KTH import parse_profile

import sys, getopt
import os
import zipfile
import shutil
import tarfile
import uuid
import itertools
import io


from  Canvas.unit_test import U_1




ROOT_DIR = os.path.dirname(os.path.abspath(__file__))+"/.."  # This is your Project Root
json_path ='output.json'


#load api configuration
with open('config.json') as json_data_file:
    configuration = json.load(json_data_file)
    canvas = configuration['canvas']
    access_token = canvas["access_token"]
    baseUrl = 'https://%s/api/v1/courses/' % canvas.get('host', 'kth.instructure.com')
    header = {'Authorization': 'Bearer ' + access_token}



#selelnium import currently not used. might used for DiVA
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

import subprocess

import time

#defind test data - these data is used for testing the software during develop phase
running_path = "kthextract.py"
pdf_path = 'https://kth.instructure.com/courses/2139/assignments/24565/submissions/11185?download=890332'

#main class
def main(course_id,assignment_id,document_type,user_id_list):
    #session id
    #currently not used
    global my_id
    session_id = uuid.uuid1()
    #refacor into library
    args=[]
    args.append(course_id)
    args.append(assignment_id)
    args.append(document_type)    # 0 is thesis 1 is proporsal


    # backup solution. leave it here. if we dont use this in the end, we delete it
    # command = "python" + " " + running_path + " " + pdf_path + " " + document_type + " " + student_name

    #pdf download path
    download_dir = ROOT_DIR + "/Source"
    shutil.rmtree(download_dir)
    os.makedirs(download_dir)  # clean up the source


    # start canvas module
    #prepoeration work for canvas module
    print 'Preperation for canvas module start'
    path = os.getcwd()
    print "Current directory: " + path
    print "jumping to canvas module path"
    path =ROOT_DIR
    os.chdir(path+"/src")
    os.chdir('Canvas/canvas')
    print "Current directory: " + os.getcwd()
    print 'Preperation for canvas module done'

    #for each user in the user list
    for user_id in user_id_list:
        #obtain submission as file
        #Dr Gerald from KTH provide this library
        message = "python3 get_submission_as_file.py " + str(args[0]) + " " + str(args[1])+" "+str(user_id)
        print ("Running command: "+message)
        sub = subprocess.Popen(message, stdout=subprocess.PIPE, shell=True)
        (pdf_path, error) = sub.communicate()
        #convert output string into useable data
        pdf_path=pdf_path.replace("\n", "")
        print "the output file id is: " + str(pdf_path)

        destination=download_dir+"/"+str(user_id)+".pdf"
        #move download pdf into source
        shutil.move(pdf_path,destination)

    #Removed selenium code -  dont delete yet

    # print 'Automating firefox module'

    # profile = webdriver.FirefoxProfile()
    # option = Options()

    # profile.set_preference("general.useragent.override",
    #                        "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0")
    # profile.set_preference("browser.download.folderList", 2)
    # profile.set_preference("browser.download.manager.showWhenStarting", False)
    # profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    # profile.set_preference("browser.helperApps.alwaysAsk.force", False);
    # profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
    # profile.set_preference("browser.download.dir", download_dir)
    # profile.set_preference("pdfjs.disabled", True)
    # profile.update_preferences()
    #
    # option.profile = profile
    #
    # #firefox_capabilities = DesiredCapabilities.FIREFOX
    # #firefox_capabilities['marionette'] = True
    # # firefox_capabilities['binary'] = 'tools/firefox/firefox-bin'
    #
    #
    # while os.path.isfile(download_dir+"/submissions.zip")==False:
    #     print 'Logging in KTH'
    #     browser = webdriver.Firefox(firefox_profile=profile)
    #     browser = webdriver.Firefox(capabilities=firefox_capabilities, firefox_options=opts, firefox_profile=profile)
    #     browser.get("https://kth.instructure.com/")
    #     time.sleep(3)
    #
    #     username = browser.find_element_by_id("username")
    #     password = browser.find_element_by_id("password")
    #
    #     username.send_keys(args[2])
    #     password.send_keys(args[3])
    #     browser.find_element_by_name("submit").click()
    #     browser.get(pdf_path)
    #
    #     print 'Dowloading pdf..... This might take a while......'
    #     print "Downloading from: " + pdf_path
    #
    #     browser.get(pdf_path)
    #     time.sleep(10)  # make it dynamic by checking if the source folder is empty
    #     browser.close()
    #     # browser.find_element_by_name("download_submission_button").click()
    #
    #     print 'File saved in ' + download_dir
    #
    #     timeout=10
    #     while os.path.isfile(download_dir+"/submissions.zip") ==False :
    #         print os.path.isfile(download_dir+"/submissions.zip")
    #         time.sleep(5)  # make it dynamic by checking if the source folder is empty
    #         timeout-=1
    #         if timeout==0:
    #             print("Time out!")
    #             browser.close()
    #             break
    # print ("direct: "+str(os.listdir(download_dir)))
    # browser.close()
    # # browser.find_element_by_name("download_submission_button").click()
    #
    # print 'File saved in ' + download_dir
    #
    # # if the file is a package, unzip and extract it
    # for file in os.listdir(download_dir):
    #     if file.endswith(".zip") or file.endswith(".tar") or file.endswith(".tar.gz"):
    #         unzip_dir = os.path.join(download_dir, file)
    #         print "Extracting file: " + unzip_dir
    #         zip_ref = zipfile.ZipFile(unzip_dir, 'r')
    #         zip_ref.extractall(download_dir)
    #         zip_ref.close()




    print 'Done with canvas module and leaving the module'
    #canvas module done



    os.chdir(path + "/../")
    print os.getcwd()

    # start process module
    # process module preperation
    print os.getcwd()
    print 'Preperation for parse module start'
    path = os.getcwd()
    print path
    path =ROOT_DIR
    os.chdir(path)
    os.chdir('src/parse/kth_extract/pdfssa4met')
    print os.getcwd()
    print 'Preperation for the parse module done'

    processed_folder=[]
    for file in os.listdir(download_dir):
        if file.endswith(".pdf"):# if it is a pdf file
            if "-" in file:
                print "The file name is: "+ file
                #python hate '-' character. replace it with '_'
                source = os.path.join(download_dir, file)
                destination = os.path.join(download_dir, file.replace("-", "_"))
                os.rename(source, destination)
                file = file.replace("-", "_")
            pdf_locl_path = os.path.join(download_dir, file)
            print "found pdf file: " + pdf_locl_path

            # main process module
            dir=kthextract.main([pdf_locl_path, args[2]])
            #append session data
            processed_folder.append(dir)

            i =0
            super_column_id=0
            examinar_column_id=0

#obtain examinar and supervisor detail info
            column_list=lunch(2139)
            while i<len(column_list):
                if column_list[i]['title']=='Examinar':
                    examinar_column_id=column_list[i]['id']
                if column_list[i]['title'] == 'Supervisor':
                    super_column_id = column_list[i]['id']
                i+=1
            for item_super,item_exam in itertools.izip(list_column_entry(course_id,super_column_id),list_column_entry(course_id,examinar_column_id)):
                print "user_id: "+ str(item_super['user_id'])
                print "file: "+ str(file).split(".")[0].strip()

                if str(item_super['user_id']).strip().replace(" ","")==str(file).split(".")[0].strip().replace(" ",""):
                    supervisor_kthusername=item_super['content'].split(';')[1]
                    examinar_kthusername=item_exam['content'].split(';')[1]
                    examinar_info = parse_profile.get_user_info(examinar_kthusername.strip())
                    supervisor_info = parse_profile.get_user_info(supervisor_kthusername.strip())
                    os.chdir(ROOT_DIR + "/output/parse_result/"+dir)
                    json_content={}
                    with open('output.json') as f:

                        json_content = json.load(f)
                        f.close()

                    for key in examinar_info.keys():
                            if isinstance(examinar_info[key], list)==True:
                                for item in examinar_info[key]:

                                    for keys_works in item:
                                        json_append(keys_works + '_examinar', item[keys_works], json_content)
                            else:
                                json_append(key+'_examinar',examinar_info[key],json_content)

                    for key in supervisor_info.keys():
                            if isinstance(supervisor_info[key], list)==True:
                                for item in supervisor_info[key]:

                                    for keys_works in item:
                                        json_append(keys_works + '_examinar', item[keys_works], json_content)
                            else:
                                json_append(key + '_supervisor',supervisor_info[key],json_content)
                    print_json(json_path,json_content)




    print 'Done with parse module'




    return processed_folder


def print_json(source_dir,json_content):
        json_data = json.dumps(json_content)
        print("printing data to path: " + source_dir)
        with open(source_dir , 'w') as f:
            print json_data  # print tag information to certain file
            print >> f, json_data, "\n"  # print tag information to certain file

def json_append(key, value,json_content):
        json_content[key] = value
        return json_content

    # os.system(command)


if __name__ == '__main__':
    main()
