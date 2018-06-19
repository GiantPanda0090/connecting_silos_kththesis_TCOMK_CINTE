

#This is the test case for Unit Test U.1
#expected  https://kth.instructure.com/courses/2139/assignments/24565/submissions?zip=1
#course_id 2139(sandbox)
#assignment_id 24565 test_1
#purpose:test the accurate of the link obtained from canvas api
#implemented

#import
import sys
import config
import urllib2
import os


#initialize test enviorment
Expected_kth_canvas= config.kth_canvas
#course_id 2139(sandbox)
Expected_kth_canvas_thesis_course_id = config.thesis_course_id #sandbox
#assignment_id 24565 testing 1; 24566 testing 2 ; 24567 testing 3;
Expcted_proporsal_assignment_id=config.proporsal_assignment_id #test_1
Expected_thesis_assignment_id=config.Thesis_assignment_id #test_2

def print_to_log(content):
    global output
    with open('test_log.txt','w') as f:
        path=os.getcwd()
        f.write(content)
        f.write("\n")
        f.close()
    output=output + content

def main(course_id,install_course_id,assigemtn_id,installed_assignment_id,assignment_id_beta,installed_assignment_id_beta):
    global output
    global status
    output=""
    print_to_log ("Start Test Case U_1")
    #define phase

    if course_id != install_course_id:
        print_to_log("Error_report:")
        print_to_log("Test Case U.1 Failed")
        print_to_log("course id is not equal to install_course_id")
        print_to_log("Course id is: "+ str(course_id))
        print_to_log("Installed Course_id is: "+ str(install_course_id))
        status=False
    elif assigemtn_id != installed_assignment_id:
        print_to_log("Error_report:")
        print_to_log("Test Case U.1 Failed")
        print_to_log("assigemtn_id is not equal to install_assigemtn_id")
        print_to_log("assigemtn_id is: "+ str(assigemtn_id))
        print_to_log("Installed assigemtn_id is: "+ str(installed_assignment_id))
        status=False
    elif assignment_id_beta != installed_assignment_id_beta:
        print_to_log("Error_report:")
        print_to_log("Test Case U.1 Failed")
        print_to_log("assignment_id_beta is not equal to install_assignment_id_beta")
        print_to_log("assignment_id_beta is: "+ str(assignment_id_beta))
        print_to_log("Installed assignment_id_beta is: "+ str(installed_assignment_id_beta))
        status=False
    else:
        print_to_log("Test Case U.1 Pass")
        status=True


    return [output,status]


def main_th(course_id,install_course_id,assigemtn_id_thesis,installed_assignment_id_thesis):
    global output
    global status
    output=""
    print_to_log ("Start Test Case U_1")
    #define phase
    assigemtn_id_thesis=str(assigemtn_id_thesis).strip()
    assigemtn_id_thesis=assigemtn_id_thesis.replace(" ","")
    installed_assignment_id_thesis=str(installed_assignment_id_thesis).strip()
    installed_assignment_id_thesis=installed_assignment_id_thesis.replace(" ","")

    if course_id != install_course_id:
        print_to_log("Error_report:")
        print_to_log("Test Case U.1 Failed")
        print_to_log("course id is not equal to install_course_id")
        print_to_log("Course id is: "+ str(course_id))
        print_to_log("Installed Course_id is: "+ str(install_course_id))
        status=False
    elif assigemtn_id_thesis != installed_assignment_id_thesis:
        print_to_log("Error_report:")
        print_to_log("Test Case U.1 Failed")
        print_to_log("assigemtn_id_thesis is not equal to installed_assignment_id_thesis")
        print_to_log("assigemtn_id_thesis is: "+ str(assigemtn_id_thesis))
        print_to_log("Installed assigemtn_id_thesis is: "+ str(installed_assignment_id_thesis))
        status=False
    else:
        print_to_log("Test Case U.1 Pass")
        status=True


    return [output,status]







