#!/usr/bin/python
""" main run file
Usage: start.py

------------


Modified on 2018.04.14
@author: Qi LI.

Modified to fit the Connecting silo requirment

fit the data mining model with thesis proporsal and thesis report BASED ON 2018 NEW EECS templet. ICT department templet is not competible

fits the requirment of DiVA


------------
"""


import os
import config
#initialize test enviorment
Expected_kth_canvas= config.kth_canvas
#course_id 2139(sandbox)
Expected_kth_canvas_thesis_course_id = config.thesis_course_id #sandbox
#assignment_id 24565 testing 1; 24566 testing 2 ; 24567 testing 3;
Expcted_proporsal_assignment_id=config.proporsal_assignment_id #test_1
Expected_thesis_assignment_id=config.Thesis_assignment_id #test_2
Expected_user_id=config.User_id

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))+"/.."  # This is your Project Root

import subprocess


import time

running_path = "kthextract.py"
pdf_path = 'https://kth.instructure.com/courses/2139/assignments/24565/submissions/11185?download=890332'
storage=[]




def main():
    # backup solution. leave it here. if we dont use this in the end, we delete it
    # command = "python" + " " + running_path + " " + pdf_path + " " + document_type + " " + student_name
    times=0
    runningtime = 5

    # start canvas module
    while times<runningtime:
        path = os.getcwd()
        os.chdir(path)
        os.chdir('../canvas')
        message = "python3 get_submission.py " + str(Expected_kth_canvas_thesis_course_id) + " " + str(Expcted_proporsal_assignment_id)+ " " + str(Expected_user_id)
        sub = subprocess.Popen(message, stdout=subprocess.PIPE, shell=True)
        (pdf_path, error) = sub.communicate()
        print "the output submission file id is: " + str(pdf_path)
        storage.append(pdf_path)
        times+=1
    temp=storage[0]
    for link in storage:
        if link!=temp:
            print ("Error Report: ")
            print ("The link is not consistent")
            print ("The Test Case U_5 failed")
            break
        temp=link
    print ("The Test Case U_5 passed")


if __name__ == '__main__':
        main()

