# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.contrib import messages
import io

from .models import Question
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
os.chdir(ROOT_DIR+'/src')
from src import start_proporsal
import os
import sys
import thread

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root


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

#@print_http_response
def index(request):
    global course_id
    global assignment_id
    global username
    global password

    course_id = 0
    assignment_id = 0
    username = ""
    password = ""
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    template_1 = loader.get_template('polls/process.html')
    template_2 = loader.get_template('polls/done.html')


    #/home/lqschool/git/Connecting_Silo/mysite/polls/index.html
    #/home/lqschool/git/Connecting_Silo/mysite/polls/index.html
    if request.method == 'POST':
        data_list = []  # We will insert all the inputs in this array
        for key in request.POST:
            data_list.append(request.POST[key])
            #[u'assignmentid', u'password', u'courseid', u'document_id', u'username', u'G5IUnO5gs50vs5X48A2jvXv1pJQbVNKVW3wRLbEds3I51uWboteHfkEZ2Q3mDvI9']

        course_id=data_list[2]
        assignment_id=data_list[0]
        username=data_list[4]
        password=data_list[1]
        document_type=data_list[3]
        print data_list
        # try:
        #     thread.start_new_thread(process(request), ("Thread-2", 4,))
        # except:
        #     print "process are not started"
        #print "data_list" + str(len(data_list))

        session_folder_list=start_proporsal.main(course_id, assignment_id, username, password,document_type)

        os.chdir(ROOT_DIR+"/output/parse_result")
        output_str_toweb=""
        file_list = os.listdir(os.getcwd())
        for dir in session_folder_list:
            # print os.getcwd()

            if dir != "cache":
                os.chdir(os.getcwd() + "/" + dir)
                output_str_toweb = output_str_toweb + "\n\n" + "Session: "+dir + ":\n"

                for root, dirs, files in os.walk("."):#per folder
                    current_author_group=[]
                    for filename in files:
                        if filename!="heading.txt":#filename filter
                            output = io.open(os.getcwd()+"/"+filename,'r', encoding="utf-8")
                            output_str_toweb=output_str_toweb+"\n"+filename+"\n"+output.read()
                            output.close()
                    os.chdir("../")
                    output_str_toweb=output_str_toweb+ "END OF SESSION"+\
                                 "\n\n"

        os.chdir(ROOT_DIR)
        context = {
            'Course_id': course_id,
            'Assignment_id': assignment_id,
            'Username': username,
            'Password': password,
            'Output': output_str_toweb,

        }
        return HttpResponse(template_2.render(context, request))
    context = {

    }
    #print "Starting Connecting Silo Process......"

    #print "Process Done!!"

    return HttpResponse(template.render(context,request))

def process(request):
    template = loader.get_template('polls/process.html')

    context = {
        'Course_id': course_id,
        'Assignment_id': assignment_id,
        'Username': username,
        'Password': password,

    }

    return HttpResponse(template.render(context,request))


def done(request):
    template = loader.get_template('polls/done.html')

    context = {
        'Course_id': course_id,
        'Assignment_id': assignment_id,
        'Username': username,
        'Password': password,

    }
    return HttpResponse(template.render(context,request))



