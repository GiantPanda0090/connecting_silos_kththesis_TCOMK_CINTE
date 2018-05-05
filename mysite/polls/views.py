# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.contrib import messages


from .models import Question
import os
root =os.getcwd()
os.chdir(os.getcwd()+'/polls/src')
from src import start_proporsal
import os
import sys
import thread



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

        messages.success(request, 'Form submission successful')
        data_list = []  # We will insert all the inputs in this array
        for key in request.POST:
            data_list.append(request.POST[key])
        course_id=data_list[2]
        assignment_id=data_list[0]
        username=data_list[4]
        password=data_list[3]
        # try:
        #     thread.start_new_thread(process(request), ("Thread-2", 4,))
        # except:
        #     print "process are not started"
        print "data_list" + str(len(data_list))

        start_proporsal.main(course_id, assignment_id, username, password)
        context = {
            'Course_id': course_id,
            'Assignment_id': assignment_id,
            'Username': username,
            'Password': password,

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



