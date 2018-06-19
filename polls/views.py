# -*- coding: utf-8 -*-
#  Django page backend process
from __future__ import unicode_literals

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.contrib import messages
import io

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root



os.chdir(ROOT_DIR+'/src')
from src import *
from src.Canvas.unit_test import *
import os
import sys
from lti import ToolConfig
from lti.contrib.django import DjangoToolProvider
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from braces.views import CsrfExemptMixin
from django.contrib.sessions.backends.db import SessionStore
import requests
from pyvirtualdisplay import Display
import itertools
from src.KTH import parse_profile
from src.mods import xmlGenerator




from django.contrib.auth.models import User

import json


#api config
# styled based upon https://martin-thoma.com/configuration-files-in-python/
with open('config.json') as json_data_file:
       configuration = json.load(json_data_file)
       canvas = configuration['canvas']
       access_token= canvas["access_token"]
       # access_token=configuration["canvas"]["access_token"]
       #baseUrl = 'https://kth.instructure.com/api/v1/courses/' # changed to KTH domain
       baseUrl = 'https://%s/api/v1/courses/' % canvas.get('host', 'kth.instructure.com')
       header = {'Authorization' : 'Bearer ' + access_token}


def print_json(source_dir,json_content):
        json_data = json.dumps(json_content)
        print("printing data to path: " + source_dir)
        with open(source_dir , 'w') as f:
            print json_data  # print tag information to certain file
            print >> f, json_data, "\n"  # print tag information to certain file

def json_append(key, value,json_content):
        json_content[key] = value
        return json_content


#system self check

def update_database(request):
    session_id =request.POST['user_session_id']
    os.chdir(ROOT_DIR + "/output/parse_result")
    folder_list=[]
    for folder_name in os.listdir('.'):
     if folder_name != "cache" and folder_name != "log.txt" and folder_name != "test_log.txt":
      folder_name_list=folder_name.split('_')
      if session_id==folder_name_list[3]:
       if session_id == folder_name_list[3]:
              folder_list.append(folder_name)
       os.chdir(os.getcwd() + "/" + folder_name)
       for root, dirs, files in os.walk("."):  # per file
        current_author_group = []
        exclude_keys = []

        json_content = {}
        with open('output.json') as f:
            json_content = json.load(f)
            f.close()


        for keys in json_content:
            changed_content=request.POST[keys].strip() #from front end
            content =json_content[keys].strip()


        #if there is a change occure
            if changed_content != content and keys not in exclude_keys:
                json_append(keys,changed_content,json_content)
                # f=open(filename, 'w')
                # f.write(changed_content.encode("utf-8"))
                # f.close()

                #consistency
                filename_construct = keys.split("_")
                if  ("frontname" in str(keys)) or ("aftername" in str(keys)):
                        frontname_file=filename_construct[0]+"_"+filename_construct[1]+"_"+"frontname"
                        aftername_file=filename_construct[0]+"_"+filename_construct[1]+"_"+"aftername"
                        author_file=filename_construct[0]+"_"+filename_construct[1]

                        exclude_keys.append(author_file)

                        frontname=json_content[frontname_file]
                        frontname.strip()

                        aftername=json_content[aftername_file]
                        aftername.strip()

                        #merge=open(author_file, 'w')
                        write_str_list=str(frontname+" "+aftername)

                                # reference https://stackoverflow.com/questions/7152762/how-to-redirect-print-output-to-a-file-using-pytho
                        json_append(author_file,write_str_list,json_content)

                elif  "author_1" in str(keys) or "author_2" in str(keys):
                    frontname_file = filename_construct[0] + "_" + str(filename_construct[1]).split('.')[0] + "_" + "frontname"
                    aftername_file = filename_construct[0] + "_" + str(filename_construct[1]).split('.')[0] + "_" + "aftername"
                    author_file = filename_construct[0] + "_" + filename_construct[1]

                    exclude_keys.append(frontname_file)
                    exclude_keys.append(aftername_file)

                    #write to author
                    author=json_content[author_file]

                    # output = io.open(os.getcwd() + "/" + author_file, 'r')
                    # author = output.read()
                    # output.close()

                    name_construct=author.split(" ")
                    author_name=[]
                    for item in name_construct:
                        author_name.append(item)

                    #write front name
                    json_append(frontname_file,author_name[0],json_content)
                    # with open(frontname_file, 'w') as f:
                    #     write_line.append(author_name[0])
                    #     f.writelines(write_line)
                    #     f.close(

                    write_line=''
                    i = 1
                    while i < (len(author_name)):
                        write_line=write_line+' '+author_name[i]
                        i += 1

                    json_append(aftername_file,write_line,json_content)

                    # # with open(aftername_file, 'w') as f:
                    #     i =1
                    #     while i< (len(author_name)):
                    #         write_line.append(author_name[i])
                    #         write_line.append(" ")
                    #         i+=1
                    #     f.writelines(write_line)
                    #     f.close()
                elif "familyName_" in str(keys) or "givenName_" in str(keys):
                    list=str(keys).split('_')
                    frontname_key=''
                    aftername_key=''
                    key=''
                    if 'examinar' in list[1].strip().split():
                        key='Examiner'
                        exclude_keys.append(key)
                        frontname_key='familyName_examinar'
                        aftername_key='givenName_examinar'
                    else:
                        key = 'Supervisor'
                        exclude_keys.append(key)
                        frontname_key = 'familyName_supervisor'
                        aftername_key = 'givenName_supervisor'

                    #merge front and given Name
                    front_name=json_content[frontname_key]
                    front_name=str(front_name.encode('utf-8')).strip()
                    aftername =json_content[aftername_key]
                    aftername=str(aftername.encode('utf-8')).strip()

                    fullname=(front_name+" ".encode('utf-8')+aftername)

                    json_append(key,fullname, json_content)
                elif "Examiner" in str(keys):
                    frontname_keys ="familyName_"+ str(keys).strip().lower()
                    aftername_keys = "givenName_"+ str(keys).strip().lower()
                    author_keys = 'Examiner'

                    exclude_keys.append(frontname_keys)
                    exclude_keys.append(aftername_keys)

                    # write to author
                    author = json_content[author_keys]

                    # output = io.open(os.getcwd() + "/" + author_file, 'r')
                    # author = output.read()
                    # output.close()

                    name_construct = author.split(" ")
                    author_name = []
                    for item in name_construct:
                        author_name.append(item)

                    # write front name
                    json_append(frontname_keys, author_name[0], json_content)
                    # with open(frontname_file, 'w') as f:
                    #     write_line.append(author_name[0])
                    #     f.writelines(write_line)
                    #     f.close(

                    write_line = ''
                    i = 1
                    while i < (len(author_name)):
                        write_line = write_line + ' ' + author_name[i]
                        i += 1

                    json_append(aftername_keys, write_line, json_content)


                print_json('output.json',json_content)

    os.chdir(ROOT_DIR)
    # send data back to canvas
    # print 'Sending Result back to Canvas Grade book'
    # course_id=request.session[session_id + '_course_id']
    #
    # fill_proposal_gradebook_columns.main(course_id, folder_list)
    # print 'Whole process done'
    if  request.POST['session_id_session']==u'checked':
        return retrive_session_baseon_id(request)
    else:
        return retrive_generalsession_baseon_id(request)




def retrive_generalsession_baseon_id(request):
    if "1" in str(request.POST['stage']):
        template_2 = loader.get_template('polls/done.html')
    else:
        template_2 = loader.get_template('polls/done_thesis.html')

    folder_list=request.session[request.POST['session_id_session']]

    abstract_autofill = ""
    title_autofill = ""
    author_autofill = ""
    contact_autofill = ""
    manager_autofill = ""
    toc_autofill = ""
    level_autofill=""
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

    # append output result to front end
    os.chdir(ROOT_DIR + "/output/parse_result")
    examinar_list=[]
    supervisor_list=[]
    student_list=[]

    title_list=[]

    for folder in folder_list:
        if folder != "cache" and folder != "log.txt":
            #read session info for front end
            title=[]
            dir_list = str(folder).split("_")
            title.append("author_1: ")
            title.append(dir_list[1])
            title.append("author_2: ")
            title.append(dir_list[2])
            title.append("Session_id: ")
            title.append(dir_list[3])
            title.append("Process Date Time: ")
            title.append(dir_list[4])
            title.append(str(folder))

            title_list.append(title)

            os.chdir(os.getcwd() + "/" + folder)
            json_content = {}
            with open('output.json') as f:
                json_content = json.load(f)
                f.close()

            for root, dirs, files in os.walk("."):  # per file
                        current_author_group = []
                        for keys in json_content:
                            #autofill polopoly

                            if keys != "heading" and keys != "log":  # filename filter
                                content=json_content[keys]
                                content_list=[]
                                content_list.append(keys)
                                content_list.append(content)
                                #check term
                                if keys == "abstract(en)" or keys == "abstract(sv)":
                                    if (len(abstract_autofill)):
                                        abstract_autofill = abstract_autofill + "\n" + content
                                    else:
                                        abstract_autofill = content
                                if keys == "title":
                                    title_autofill = content
                                if keys == "level":
                                    level_autofill = content
                                if keys == "author_1" or keys == "author_2":
                                    if len(author_autofill):
                                        author_autofill = author_autofill + ";\n " + content
                                    else:
                                        author_autofill = content

                                if keys == "author_email_1" or keys == "author_email_2":
                                    if len(contact_autofill):
                                        contact_autofill = contact_autofill + "; \n" + content
                                    else:
                                        contact_autofill = content

                                if keys == "Examiner" or keys == "Supervisor":
                                    if len(manager_autofill):
                                        manager_autofill = manager_autofill + "; " + content
                                    else:
                                        manager_autofill = content
                                if keys == "toc(en)":
                                    toc_autofill = content
                                # append result for front end
                                if '_examinar' in keys:
                                    examinar_list.append(content_list)
                                elif '_supervisor' in keys:
                                    supervisor_list.append(content_list)
                                else:
                                    student_list.append(content_list)

                        os.chdir("../")

    # back to root
    os.chdir(ROOT_DIR)
    # send data to front end

    context = {
        'Title': title_list,
        'Session_id':request.POST['session_id_session'],
        'Examinar_info': examinar_list,
        'Student_info': student_list,
        'Supervisor_info': supervisor_list,
        'Body': abstract_autofill,
        'Lecturer': author_autofill,
        'Heading': title_autofill,
        "Contact": contact_autofill,
        "Manager": manager_autofill,
        "Level":level_autofill,
        "TOC": toc_autofill,
        "Session_list": folder_list,
        "Debug":request.POST['stage']

    }
    return HttpResponse(template_2.render(context, request))


def retrive_session_baseon_id(request):
    if "1" in str(request.POST['stage']):
        template_2 = loader.get_template('polls/done.html')
    else:
        template_2 = loader.get_template('polls/done_thesis.html')
    session_id=request.POST['user_session_id']


    abstract_autofill = ""
    title_autofill = ""
    author_autofill = ""
    contact_autofill = ""
    manager_autofill = ""
    toc_autofill = ""
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
    examinar_list = []
    supervisor_list = []
    student_list = []
    title_list=[]
    # append output result to front end
    os.chdir(ROOT_DIR + "/output/parse_result")
    folder_list = os.walk('.')
    # go into each output result session
    for path,folders,file in folder_list:
            for dir in folders:
              if dir != "cache" and dir !="log.txt":
                folder_strutre = str(dir).split("_")
                if session_id==folder_strutre[3]:
                    request.session[session_id] = [dir]

                    os.chdir(os.getcwd() + "/" + dir)
                    title = []

                    dir_list = str(dir).split("_")
                    title.append("author_1: ")
                    title.append(dir_list[1])
                    title.append("author_2: ")
                    title.append(dir_list[2])
                    title.append("Session_id: ")
                    title.append(dir_list[3])
                    title.append("Process Date Time: ")
                    title.append(dir_list[4])
                    title.append(str(dir))

                    title_list.append(title)
                    json_content = {}
                    with open('output.json') as f:
                        json_content = json.load(f)
                        f.close()

                    # go into each output result
                    for root, dirs, files in os.walk("."):  # per file
                        current_author_group = []
                        #auto fill polopoly
                        for keys in json_content:
                            if keys != "heading" and keys != "log":  # filename filter
                                content=json_content[keys]
                                content_list=[]
                                content_list.append(keys)
                                content_list.append(content)
                                #check term
                                if keys == "abstract(en)" or keys == "abstract(sv)":
                                    if (len(abstract_autofill)):
                                        abstract_autofill = abstract_autofill + "\n" + content
                                    else:
                                        abstract_autofill = content
                                if keys == "title":
                                    title_autofill = content
                                if keys == "author_1" or keys == "author_2":
                                    if len(author_autofill):
                                        author_autofill = author_autofill + ";\n " + content
                                    else:
                                        author_autofill = content

                                if keys == "author_email_1" or keys == "author_email_2":
                                    if len(contact_autofill):
                                        contact_autofill = contact_autofill + "; \n" + content
                                    else:
                                        contact_autofill = content

                                if keys == "Examiner" or keys == "Supervisor":
                                    if len(manager_autofill):
                                        manager_autofill = manager_autofill + "; " + content
                                    else:
                                        manager_autofill = content
                                if keys == "toc(en)":
                                    toc_autofill = content
                                # append result for front end
                                if '_examinar' in keys:
                                    examinar_list.append(content_list)
                                elif '_supervisor' in keys:
                                    supervisor_list.append(content_list)
                                else:
                                    student_list.append(content_list)
                        os.chdir("../")

    # back to root
    os.chdir(ROOT_DIR)
    # send data to front end

    context = {
       'Title':title_list,
       'Examinar_info': examinar_list,
       'Student_info': student_list,
       'Supervisor_info': supervisor_list,
       'Body': abstract_autofill,
       'Lecturer': author_autofill,
       'Heading': title_autofill,
       "Contact": contact_autofill,
       "Manager": manager_autofill,
       "TOC": toc_autofill,
       "Session_list": folder_list

        }
    return HttpResponse(template_2.render(context, request))



#installation first step
def install(request):
    template = loader.get_template('polls/install.html')

#define parameter
    global app_title
    global app_description
    global config_url
    global launch_view_name


    # define parameter for lti installation
    app_title = 'Proporsal Approval'
    app_description = 'KTH Automation proporsal'
    launch_view_name = 'lti_CS_launch'
    config_url = request.build_absolute_uri(reverse('lti_bound'))
    print "address: "
    obrained_list=[]
    proporsal_list=[]
    thesis_list=[]
    context={}
    #receive form
    return HttpResponse(template.render(context,request))

def accept_form(request):
        template_3 = loader.get_template('polls/install_assignment_list.html')
        global course_id_install

        # getting available thesis course list and proporsal course list
        course_id_install = request.POST['courseid']
        # 0 for thesis 1 for proprosal
        thesis_list = creat_assignment_list(course_id_install, 0)
        proporsal_list = creat_assignment_list(course_id_install, 1)
        beta_list = creat_assignment_list(course_id_install, 2)

        context = {
            'Course_List_Proporsal': proporsal_list,
            'Course_List_Thesis': thesis_list,
            'Beta_draft_list': beta_list,
            'Course_id':course_id_install
        }
        # send result back to front end
        return HttpResponse(template_3.render(context, request))


#installation second step
def install_2(request):
    template_1 = loader.get_template('polls/install_done.html')
    template_2 = loader.get_template('polls/install_fail.html')
    #accepting data from form
    if request.method == 'POST':
        print request.POST
        context={}
        #trigger final step
        r=install_final(request)
        #if finall step success or failed. sending different result page
        if r.status_code == requests.codes.ok:
            return HttpResponse(template_1.render(context, request))
        else:
            return HttpResponse(template_2.render(context, request))


#final stage of installation
def install_final(request):
    #Install proporsal module
    #define parameter for the lti app
    app_title = 'Schedule Oral Presentation'
    app_description = 'Connecting Silo project - schedule a time for thesis presentation and obtain suitable info'
    launch_view_name = 'lti_CS_launch'
    #when form is submitted
    if request.method == 'POST':
        print ("Request receive"+ str(request.POST))
        course_id_install=request.POST['courseid']

        print course_id_install
        print "Course id for current session:"
        print course_id_install
        #https://<canvas>/api/v1/courses/<course_id>/external_tools'
        url=baseUrl + '%s/external_tools' % (course_id_install)
        #obtain installation data
        assignment_id =request.POST['proporsal_choice']

        assignment_id_beta =request.POST['beta_choice']

        assignment_id_thesis =request.POST['thesis_choice']
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
        loc=ROOT_DIR+"/allowed_course.txt"
        with open( loc, 'w') as f:
            f.write(str(course_id_install)+"||"+str(assignment_id)+","+str(assignment_id_beta)+","+str(assignment_id_thesis)+"\n")
            f.close()






        config_url = request.build_absolute_uri(reverse('lti_bound'))
        #furthur define parameter for lti app
        payload_proposal= {
            'name': app_title,
            'privacy_level': "public",
            'description': app_description,
            'consumer_key': "N/A",
            'shared_secret': "",
            'course_navigation[text]': app_title,
            'course_navigation[default]': "enabled",
            'course_navigation[enabled]': "true",
            'course_navigation[visibility]': "public",
            'config_type': "by_url",
            'config_url': config_url,
            'custom_fields[assignment_id]': assignment_id,
            'custom_fields[assignment_id_beta]': assignment_id_beta

        }
        #send installation to Canvas
        print ("Posting request to: "+url)
        r=requests.post(url,headers=header,data=payload_proposal)
        print ("Receive: "+str(r))
        url=baseUrl + '%s/external_tools' % (course_id_install)
        #find the lti external tool id from canvas
        payload={
            'search_term':app_title
        }
        print ("Getting request to: "+url)
        r=requests.get(url,headers=header,data=payload)

        # PUT /api/v1/courses/:course_id/external_tools/:external_tool_id
        return_val=r.json()
        print ("Receive: "+str(return_val))
        id=return_val[0]['id']
        #update rest of the infor base on the id obtained
        payload_proposal = {
            'privacy_level': "public",
            'course_navigation[text]': app_title,
            'course_navigation[default]': "enabled",
            'course_navigation[enabled]': "true",
            'course_navigation[visibility]': "public",
            'custom_fields[assignment_id]':assignment_id,
            'custom_fields[assignment_id_beta]': assignment_id_beta
        }
        print ("Putting request to: "+url)

        url=baseUrl + '%s/external_tools/%s' % (course_id_install,id)
        r=requests.put(url,headers=header,data=payload_proposal)
        print ("Receive: "+str(r))
        #double check application existent. if failed this will give 404
        payload = {
            'search_term': app_title
        }
        print ("Getting request to: "+url)
        r = requests.get(url, headers=header, data=payload)
        # PUT /api/v1/courses/:course_id/external_tools/:external_tool_id
        return_val = r.json()
        print ("Receive: "+str(return_val))

        # Install thesis module
        #lti application installation parameter
        app_title = 'Thesis Approval'
        app_description = 'Connecting Silo project -Approve final thesis and obtain suitable info'
        launch_view_name = 'lti_CSThesis_launch'
        config_url = request.build_absolute_uri(reverse('lti_bound_theis'))
        #furthur define parameter
        payload_thesis = {
            'name': app_title,
            'privacy_level': "public",
            'description': app_description,
            'consumer_key': "N/A",
            'shared_secret': "",
            'course_navigation[text]': app_title,
            'course_navigation[default]': "enabled",
            'course_navigation[enabled]': "true",
            'course_navigation[visibility]': "public",
            'config_type': "by_url",
            'config_url': config_url,
            'custom_fields[assignment_id]': assignment_id_thesis

        }
        # sending installtion request to canvas
        url=baseUrl + '%s/external_tools' % (course_id_install)
        print ("Posting request to: "+url)
        r = requests.post(url, headers=header, data=payload_thesis)
        print ("Receive: ")
        print (r.json())
        #finding the installed app on canvas
        payload = {
            'search_term': app_title
        }
        print ("Getting request to: "+url)
        r = requests.get(url, headers=header, data=payload)
        # PUT /api/v1/courses/:course_id/external_tools/:external_tool_id
        return_val = r.json()
        print ("Receive: ")
        print return_val
        thesis_id=return_val[0]['id']
        #base on the id found, update application
        payload_thesis = {
            'privacy_level': "public",
            'course_navigation[text]': app_title,
            'course_navigation[default]': "enabled",
            'course_navigation[enabled]': "true",
            'course_navigation[visibility]': "public",
            'custom_fields[assignment_id]': assignment_id_thesis
        }
        url = baseUrl + '%s/external_tools/%s' % (course_id_install, thesis_id)
        print ("Putting request to: "+url)
        r = requests.put(url, headers=header, data=payload_thesis)
        print ("Receive: "+ str(r.json()))
        payload = {
            'search_term': app_title
        }
        #confirm installation, if installation failed this will give 404
        print ("Getting request to: "+url)
        r = requests.get(url, headers=header, data=payload)
        # PUT /api/v1/courses/:course_id/external_tools/:external_tool_id
        return_val = r.json()
        print ("Receive: "+ str(return_val))


        #Install gecko driver and xml base on os
        # dynamic download geckodriver and pdf2xml based on OS

        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

        print "Dowloading geckodriver for selenium automation base on Operatiing system "
        print "Operating System:  " + platform.system()
        shutil.rmtree(ROOT_DIR + "/src/parse/kth_extract/pdfssa4met/pdf2xml/current/")
        os.makedirs(ROOT_DIR + "/src/parse/kth_extract/pdfssa4met/pdf2xml/current/")  # clean up the current for pdf2xml
        if platform.system() == "Linux":
            url = "https://github.com/mozilla/geckodriver/releases/download/v0.20.1/geckodriver-v0.20.1-linux64.tar.gz"
            src = ROOT_DIR + "/src/parse/kth_extract/pdfssa4met/pdf2xml/pdftoxml.linux64.exe.1.2_7"
            print src
            dst = ROOT_DIR + "/src/parse/kth_extract/pdfssa4met/pdf2xml/current/pdf2xml_osfit"
            print dst
            shutil.copyfile(src, dst)
            os.chmod(ROOT_DIR + "/src/parse/kth_extract/pdfssa4met/pdf2xml/current/pdf2xml_osfit", 0755)

        if platform.system() == "Darwin":
            url = "https://github.com/mozilla/geckodriver/releases/download/v0.20.1/geckodriver-v0.20.1-macos.tar.gz"
            src = ROOT_DIR + "/src/parse/kth_extract/pdfssa4met/pdf2xml/pdftoxml_osx"
            dst = ROOT_DIR + "/src/parse/kth_extract/pdfssa4met/pdf2xml/current/pdf2xml_osfit"
            shutil.copyfile(src, dst)
            os.chmod(ROOT_DIR + "/src/parse/kth_extract/pdfssa4met/pdf2xml/current/pdf2xml_osfit", 0755)

        response = urllib2.urlopen(url)
        html = response.read()
        print "downloading " + url
        #install headless display. this will take over port 8000 and cause problem to development server
        display = Display(visible=0, size=(800, 600))
        display.start()

        # Open our local file for writing
        with open(ROOT_DIR + "/ffdriver/geckodriver_linux.tar.gz", "wb") as local_file:
            local_file.write(html)
            local_file.close()
            tar = tarfile.open(ROOT_DIR + "/ffdriver/geckodriver_linux.tar.gz")
            tar.extractall(path=ROOT_DIR + '/ffdriver')
            tar.close()
        context={}

        return r


#stop django use csrf cookies. canvas dont like it
#this code is referenced from other website
class Object(CsrfExemptMixin, APIView):
    authentication_classes = []

    def post(self, request, format=None):
        return Response({'received data': request.data})

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root


#tool config proporsal -creat xml config
#reference: https://github.com/pylti/lti
def tool_config(request):
    app_title = 'Proporsal Approval'
    app_description = 'KTH Automation proporsal'
    launch_view_name = 'lti_CS_launch'
    launch_url = request.build_absolute_uri(reverse('lti'))

    # maybe you've got some extensions
    extensions = {
        'my_extensions_provider': {
            # extension settings...
        }
    }
    print app_title

    lti_tool_config = ToolConfig(
        title=app_title,
        launch_url=launch_url,
        secure_launch_url=launch_url,
        extensions=extensions,
        description = app_description

    )

    return HttpResponse(lti_tool_config.to_xml(), content_type='text/xml')
#tool config thesis -creat xml config
#reference: https://github.com/pylti/lti
def tool_config_thesis(request):

    app_title = 'Thesis Approval'
    app_description = 'KTH Automation THesis'
    launch_view_name = 'lti_CSThesis_launch'
    launch_url = request.build_absolute_uri(reverse('lti_th'))

    # maybe you've got some extensions
    extensions = {
        'my_extensions_provider': {
            # extension settings...
        }
    }
    print app_title


    lti_tool_config = ToolConfig(
        title=app_title,
        launch_url=launch_url,
        secure_launch_url=launch_url,
        extensions=extensions,
        description = app_description

    )

    return HttpResponse(lti_tool_config.to_xml(), content_type='text/xml')


# Create your views here.
#Reference: https://chase-seibert.github.io/blog/2010/08/06/redirect-console-output-to-a-django-httpresponse.html
def print_http_response(f):
    """ Wraps a python function that prints to the console, and
    returns those results as a HttpResponse (HTML)"""

    class WritableObject:
        def __init__(self):
            self.content = []
        def write(self, string):
            self.content.append(string)

    def new_f(*args, **kwargs):
        printed = WritableObject()
        sys.stdout = printed
        f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        return HttpResponse(['<BR>' if c == '\n' else c for c in printed.content ])
    return new_f


#lti integration for thesis approval
@csrf_exempt #no csrf cookie used
def lti_thesis(request):
    global assignment_id
    template = loader.get_template('polls/index_thesis.html')
    template_err = loader.get_template('polls/index_error.html')

    assignment_id_thesis = request.POST['custom_assignment_id'] #proporsal - custom_assignment_id
    course_id =request.POST['custom_canvas_course_id']
    username = request.POST['custom_canvas_user_login_id']
    username_list = username.split('@')
    username = username_list[0]
    userid = request.POST['custom_canvas_user_id']
    assignment_id=assignment_id_thesis#test
    print "assignment id proporsal: " + assignment_id
    print "course id: " + course_id

    loc = ROOT_DIR + "/allowed_course.txt"
    installed_id = ""

    with open(loc, 'r') as f:
        installed_id = f.read()
        f.close()

    installed_id_new = installed_id.split("||")[0]
    # str(assignment_id)+","+str(assignment_id_beta)+","+str(assignment_id_thesis)
    assignment_id_list = installed_id.split("||")[1].split(",")

    answer = U_1.main_th(course_id, installed_id_new, assignment_id, assignment_id_list[2])
    if answer[1] == False:
        context = {
            'Error_msg': answer[0]
        }
        return HttpResponse(template_err.render(context, request))
    # optain student list from canvas
    thesis_student_list = lunch(course_id, assignment_id)

    if 'proporsal_student_list' not in request.session:
        errmsg="You have not booked any presentation before. Please book presentation for student before approve thesis"
        template_err=loader.get_template('polls/index_error.html')
        context={
            'Error_msg':errmsg
        }
        return HttpResponse(template_err.render(context, request))
    previous_student_list = request.session['proporsal_student_list']



    for student in previous_student_list:
        student_id = student[0]
        for student_thesis in thesis_student_list:
            if student_id == student_thesis[0]:
                if student_thesis[3] == 1:
                    student.append(1)
                else:
                    student.append(0)
                thesis_student_list.remove(student_thesis)

    print "student list: "
    print previous_student_list
    approved_processed_list = []
    not_approved_processed_list = []

    # for eac student in the student list
    for student in previous_student_list:
        print "current student:"
        print student
        if student[3] == 1 and student[5] == 1 and student[6] == 1:  # if the proporsal has been approved
            approved_processed_list.append(student)

        else:
            not_approved_processed_list.append(student)


    # send to front end
    context = {
        'Request': request.POST,
        'Course_id': course_id,
        'Assignment_id': assignment_id,
        'username': username,
        'userid': userid,
        'Document_Type': 1,
        'Student_list': approved_processed_list,
        'Not_Approved_list': not_approved_processed_list
    }
    return HttpResponse(template.render(context, request))



# new index
# for lti app submit thesis phase
def index_submit_thesis(request):
    template_2 = loader.get_template('polls/done_thesis.html')

    # accept form data
    if request.method == 'POST':
        csrf_token = request.POST['csrfmiddlewaretoken']
        course_id = request.POST['courseid']
        assignment_id = request.POST['assignmentid']
        data_list = []  # We will insert all the inputs in this array
        print "Received feedback: "
        print (str(request.POST))
        # change recived json to list
        for key in request.POST:
            data_list.append(request.POST[key])
            # [u'assignmentid', u'password', u'courseid', u'document_id', u'username', u'G5IUnO5gs50vs5X48A2jvXv1pJQbVNKVW3wRLbEds3I51uWboteHfkEZ2Q3mDvI9']
        print "Converted List:"
        print (str(data_list))
        data = str(request.POST)
        # take away first csrf cookies and other useless stuff
        # leave only use id in the data list
        data_list.remove(course_id)
        data_list.remove(assignment_id)
        data_list.remove(csrf_token)

        print data_list
        # start main program senquence
        # proporsal
        session_folder_list_beta = start_proporsal.main(course_id, assignment_id, 0, data_list)

        os.chdir(ROOT_DIR)

        test_flag = True
        sessionid_beta = []



        # polopoly autofill json
        abstract_autofill = ""
        title_autofill = ""
        author_autofill = ""
        contact_autofill = ""
        manager_autofill = ""
        toc_autofill = ""
        title_list = []
        examinar_list = []
        supervisor_list = []
        student_list = []
        if test_flag:
            session_folder_list = session_folder_list_beta
            # send data back to canvas
            print 'Sending Result back to Canvas Grade book'
            fill_proposal_gradebook_columns.main(course_id, session_folder_list)
            print 'Whole process done'
            os.chdir(ROOT_DIR+"/src/Canvas/unit_test")
            answer=U_2_4.main(course_id, assignment_id, session_folder_list)

            if answer[1] == False:
                template_err = loader.get_template('polls/index_error.html')
                context = {
                    'Error_msg': answer[0]
                }
                return HttpResponse(template_err.render(context, request))

            # append output result to front end
            session_id = request.session.session_key
            request.session[session_id] = session_folder_list
            request.session[session_id+'_course_id']=course_id

            os.chdir(ROOT_DIR + "/output/parse_result")
            # go into each output result session
            for dir in session_folder_list:
                if dir != "cache":
                    os.chdir(os.getcwd() + "/" + dir)
                    title = []
                    dir_list = str(dir).split("_")
                    title.append("author_1: ")
                    title.append(dir_list[1])
                    title.append("author_2: ")
                    title.append(dir_list[2])
                    title.append("Session_id: ")
                    title.append(dir_list[3])
                    title.append("Process Date Time: ")
                    title.append(dir_list[4])
                    title.append(str(dir))

                    title_list.append(title)

                    # go into each output result
                    for root, dirs, files in os.walk("."):  # per file
                        current_author_group = []

                        json_content = {}
                        with open('output.json') as f:
                            json_content = json.load(f)
                            f.close()

                        for keys in json_content:

                            if keys != "heading" and keys != "log":  # filename filter
                                content = json_content[keys]

                                content_list = []
                                content_list.append(keys)
                                content_list.append(content)

                                if '_examinar' in keys:
                                    examinar_list.append(content_list)
                                elif '_supervisor' in keys:
                                    supervisor_list.append(content_list)
                                else:
                                    student_list.append(content_list)


                                # polopoly autofill json
                                if keys == "abstract(en)" or keys == "abstract(sv)":
                                    if (len(abstract_autofill)):
                                        abstract_autofill = abstract_autofill + "\n" + content
                                    else:
                                        abstract_autofill = content
                                if keys == "title":
                                    title_autofill = content
                                if keys == "author_1" or keys == "author_2":
                                    if len(author_autofill):
                                        author_autofill = author_autofill + ";\n " + content
                                    else:
                                        author_autofill = content

                                if keys == "author_email_1" or keys == "author_email_2":
                                    if len(contact_autofill):
                                        contact_autofill = contact_autofill + "; \n" + content
                                    else:
                                        contact_autofill = content

                                if keys == "Examiner" or keys == "Supervisor":
                                    if len(manager_autofill):
                                        manager_autofill = manager_autofill + "; " + content
                                    else:
                                        manager_autofill = content
                                if keys == "toc(en)":
                                    toc_autofill = content

                                # append result for front end
                        os.chdir("../")
        # back to root
        os.chdir(ROOT_DIR)
        # send data to front end

        context = {
            'Session_id': session_id,
            'Title': title_list,
            'Course_id': course_id,
            'Assignment_id': assignment_id,
            'Examinar_info': examinar_list,
            'Student_info': student_list,
            'Supervisor_info': supervisor_list,
            'Body': abstract_autofill,
            'Lecturer': author_autofill,
            'Heading': title_autofill,
            "Contact": contact_autofill,
            "Manager": manager_autofill,
            "TOC": toc_autofill,
            "Session_list": session_folder_list

        }
        return HttpResponse(template_2.render(context, request))


# new index
# for lti app submit proporsal phase
def index_submit(request):
    template_2 = loader.get_template('polls/done.html')

    # accept form data
    if request.method == 'POST':
        csrf_token = request.POST['csrfmiddlewaretoken']
        course_id = request.POST['courseid']
        assignment_id = request.POST['assignmentid']
        assignment_id_beta = request.POST['assignmentidbeta']
        data_list = []  # We will insert all the inputs in this array
        print "Received feedback: "
        print (str(request.POST))
        # change recived json to list
        for key in request.POST:
            data_list.append(request.POST[key])
            # [u'assignmentid', u'password', u'courseid', u'document_id', u'username', u'G5IUnO5gs50vs5X48A2jvXv1pJQbVNKVW3wRLbEds3I51uWboteHfkEZ2Q3mDvI9']
        print "Converted List:"
        print (str(data_list))
        data = str(request.POST)
        # take away first csrf cookies and other useless stuff
        # leave only use id in the data list
        data_list.remove(course_id)
        data_list.remove(assignment_id)
        data_list.remove(assignment_id_beta)
        data_list.remove(csrf_token)

        print data_list
        # start main program senquence
        # proporsal

        session_folder_list_proporsal = start_proporsal.main(course_id, assignment_id, 1, data_list)
        session_folder_list_beta = start_proporsal.main(course_id, assignment_id_beta, 0, data_list)

        output_str_toweb = ""
        test_flag = True
        sessionid_beta = []
        for sessions_prop, session_beta in itertools.izip(session_folder_list_proporsal, session_folder_list_beta):
            beta_name_parse = session_beta.split("_")
            prop_name_parse = sessions_prop.split("_")
            if beta_name_parse[1] != prop_name_parse[1] or beta_name_parse[2] != prop_name_parse[2] or beta_name_parse[
                3] != prop_name_parse[3]:
                print ("Error Report!")
                print ("Same session with different session number and folder")
                output_str_toweb = "Error Report!\n" + "Same session with different session number and folder\n"
                output_str_toweb = output_str_toweb + "proporsal folder: " + str(
                    sessions_prop) + "\n" + "beta draft folder: " + str(session_beta)
                test_flag = False
                break
            else:
                test_flag = True




        abstract_autofill = ""
        title_autofill = ""
        author_autofill = ""
        contact_autofill = ""
        manager_autofill = ""
        toc_autofill = ""
        title_list=[]
        examinar_list = []
        supervisor_list = []
        student_list = []
        if test_flag:
            session_folder_list = session_folder_list_beta
            # send data back to canvas
            print 'Sending Result back to Canvas Grade book'
            fill_proposal_gradebook_columns.main(course_id, session_folder_list)
            print 'Whole process done'

        #TODO:ACTIVTE THIS LATER
            # examinar_email_pair = request.session['examinar_email']
            # os.chdir(ROOT_DIR + "/output/parse_result")
            #
            # for process in examinar_email_pair:
            #     for folder in session_folder_list:
            #         if str(process[0]).lower() in folder:
            #             os.chdir(folder)
            #             examinar_email = process[1]
            #             examinar_id = str(examinar_email).split('@')[0]
            #             examinar_info = parse_profile.get_user_info(examinar_id)
            #             for key in examinar_info.keys():
            #                 with open(key + '_examinar', 'w') as f:
            #                     f.write(str(examinar_info[key]))
            #                     f.close()
            #             break
            #os.chdir(ROOT_DIR)


            # append output result to front end
            session_id = request.session.session_key
            request.session[session_id] = session_folder_list
            request.session[session_id+'_course_id']=course_id


            os.chdir(ROOT_DIR + "/output/parse_result")
            # go into each output result session
            for dir in session_folder_list:
                if dir != "cache":
                    os.chdir(os.getcwd() + "/" + dir)
                    title=[]
                    dir_list=str(dir).split("_")
                    title.append("author_1: ")
                    title.append(dir_list[1])
                    title.append("author_2: ")
                    title.append(dir_list[2])
                    title.append("Session_id: ")
                    title.append(dir_list[3])
                    title.append("Process Date Time: ")
                    title.append(dir_list[4])
                    title.append(str(dir))
                    title_list.append(title)

                    # go into each output result
                    for root, dirs, files in os.walk("."):  # per file
                        current_author_group = []
                        json_content = {}
                        with open('output.json') as f:
                            json_content = json.load(f)
                            f.close()
                        for keys in json_content:

                            if keys != "heading" and keys != "log":  # filename filter
                                content = json_content[keys]

                                content_list=[]
                                content_list.append(keys)
                                content_list.append(content)

                                if '_examinar' in keys:
                                    examinar_list.append(content_list)
                                elif '_supervisor' in keys:
                                    supervisor_list.append(content_list)
                                else:
                                    student_list.append(content_list)


                                # polopoly autofill json
                                if keys == "abstract(en)" or keys == "abstract(sv)":
                                    if (len(abstract_autofill)):
                                        abstract_autofill = abstract_autofill + "\n" + content
                                    else:
                                        abstract_autofill = content
                                if keys == "title":
                                    title_autofill = content
                                if keys == "level":
                                     level_autofill = content
                                if keys == "author_1" or keys == "author_2":
                                    if len(author_autofill):
                                        author_autofill = author_autofill + ";\n " + content
                                    else:
                                        author_autofill = content

                                if keys == "author_email_1" or keys == "author_email_2":
                                    if len(contact_autofill):
                                        contact_autofill = contact_autofill + "; \n" + content
                                    else:
                                        contact_autofill = content

                                if keys == "Examiner" or keys == "Supervisor":
                                    if len(manager_autofill):
                                        manager_autofill = manager_autofill + "; " + content
                                    else:
                                        manager_autofill = content
                                if keys == "toc(en)":
                                    toc_autofill = content




                                # append result for front end
                        os.chdir("../")
        # back to root
        os.chdir(ROOT_DIR)
        # send data to front end

        context = {
            'Session_id': session_id,
            'Title': title_list,
            'Course_id': course_id,
            'Assignment_id': assignment_id,
            'Examinar_info': examinar_list,
            'Student_info': student_list,
            'Supervisor_info': supervisor_list,
            'Body': abstract_autofill,
            'Lecturer': author_autofill,
            'Heading': title_autofill,
            "Contact": contact_autofill,
            "Manager": manager_autofill,
            "Level":level_autofill,
            "TOC": toc_autofill,
            "Session_list": session_folder_list

        }
        return HttpResponse(template_2.render(context, request))


#lti integration for proporsal approval
@csrf_exempt #no csrf cookie used
def lti_proporsal(request):
    template = loader.get_template('polls/index.html')
    template_err = loader.get_template('polls/index_error.html')

    global course_id
    global assignment_id


    # obtain information that program need
    course_id =request.POST['custom_canvas_course_id']
    loc = ROOT_DIR + "/allowed_course.txt"
    installed_id=""

    with open(loc,'r') as f:
        installed_id=f.read()
        f.close()

    installed_id_new=installed_id.split("||")[0]
    #str(assignment_id)+","+str(assignment_id_beta)+","+str(assignment_id_thesis)
    assignment_id_list=installed_id.split("||")[1].split(",")


    username=request.POST['custom_canvas_user_login_id']
    username_list =username.split('@')
    username=username_list[0]
    userid=request.POST['custom_canvas_user_id']
    assignment_id_proporsal = request.POST['custom_assignment_id'] #proporsal - custom_assignment_id
    assignment_id_beta = request.POST['custom_assignment_id_beta'] #beta draft - custom_assignment_id_beta
    assignment_id=assignment_id_proporsal#test
    print "assignment id proporsal: "+assignment_id_proporsal
    print "assignment id beta: "+assignment_id_beta
    print "course id: "+course_id
    answer = U_1.main(course_id, installed_id_new,assignment_id,assignment_id_list[0],assignment_id_beta,assignment_id_list[1])
    if answer[1] == False:
        context = {
            'Error_msg': answer[0]
        }
        return HttpResponse(template_err.render(context, request))
#optain student list from canvas
    proporsal_student_list=lunch(course_id, assignment_id_proporsal)
    beta_student_list=lunch(course_id, assignment_id_beta)




    for student in proporsal_student_list:
        student_id=student[0]
        for student_beta in beta_student_list:
            if student_id==student_beta[0]:
                if student_beta[3]==1:
                    student.append(1)
                else:
                    student.append(0)
                beta_student_list.remove(student_beta)

    print "student list: "
    print proporsal_student_list
    approved_processed_list = []
    not_approved_processed_list = []
    examinar_email_list=[]

    #for eac student in the student list
    for student in proporsal_student_list:
        print "current student:"
        print student
        if student[3]==1 and student[5]==1:#if the proporsal has been approved
            approved_processed_list.append(student)
            examinar_email_list.append([student[1],student[4]])
        else:
            not_approved_processed_list.append(student)

    request.session['examinar_email'] =examinar_email_list
    request.session['proporsal_student_list'] = proporsal_student_list


    #send to front end
    context = {
        'Request': request.POST,
        'Course_id':course_id,
        'Assignment_id':assignment_id_proporsal,
        'Assignment_id_beta': assignment_id_beta,
        'username': username,
        'userid':userid,
        'Document_Type':1,
        'Student_list':approved_processed_list,
        'Not_Approved_list':not_approved_processed_list,
    }
    return HttpResponse(template.render(context,request))


#new lti
#generate polopoly json
def generate_polopoly_json(request):
    template_2 = loader.get_template('polls/final_timebooking.html')

    jsonStr=json.dumps(request.POST)

    context = {
        'Json_str': jsonStr,


    }
    return HttpResponse(template_2.render(context, request))


#new lti
#generate and download mods file
def modsOut(request):
    template_2 = loader.get_template('polls/index_error.html')

    #obtain output folder list
    session_id = request.session.session_key
    folder_list=request.session[session_id]
    os.chdir(ROOT_DIR + "/output/parse_result")
    session_id=request.GET['session_id']
    folder=''
    for folders in folder_list:
        if session_id in folders:
            folder = folders
    if len(folder):
        modsurl=xmlGenerator.main(folder+'/output.json',folder)
        #reference: https://www.quora.com/How-do-I-make-a-download-button-in-my-web-page-work-with-Django
        with open(modsurl, 'rb') as mods:
    	    response = HttpResponse(mods.read())
            response['content_type'] = 'application/mods+xm'
    	    response['Content-Disposition'] = 'attachment;filename=modsXML.mods'
            os.chdir(ROOT_DIR)
            return response
    else:

        os.chdir(ROOT_DIR)

        context = {
            'Error message': "MODS DOWNLOAD ERROR WITH RESPONSE "+request,

             }


    return HttpResponse(template_2.render(context, request))



