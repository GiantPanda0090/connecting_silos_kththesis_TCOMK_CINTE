#!/usr/bin/python

import os,sys,glob
import subprocess





import config
#initialize test enviorment
Expected_kth_canvas= config.kth_canvas
#course_id 2139(sandbox)
Expected_kth_canvas_thesis_course_id = config.thesis_course_id #sandbox
#assignment_id 24565 testing 1; 24566 testing 2 ; 24567 testing 3;
Expcted_proporsal_assignment_id=config.proporsal_assignment_id #test_1
Expected_thesis_assignment_id=config.Thesis_assignment_id #test_2


def main():
    os.chdir("test_library")
    python_param= 'import list_studentList_assignment; list_studentList_assignment.main(%s,%s)' % (Expected_kth_canvas_thesis_course_id,Expcted_proporsal_assignment_id)

    message = "python3 -c "+"'" +  python_param+"'"
    #print (message)
    sub= subprocess.Popen(message, stdout=subprocess.PIPE, shell=True)
    (student_list_canvas, error) = sub.communicate()
    #print student_list_canvas
    os.chdir(os.getcwd()+ "/../../../../output/parse_result/")
    file_list= os.listdir(os.getcwd())
    student_list_canvas=student_list_canvas.replace("[","")
    student_list_canvas=student_list_canvas.replace("]","")
    student_list_canvas=student_list_canvas.replace("'","")
    student_list_canvas=student_list_canvas.replace("\n","")
    canvas_list=student_list_canvas.split(",")
    print "Canvas student list: " + str(canvas_list)
    length_expectedlist= len(canvas_list)
    canvas_nameList=[]
    profile=[]

    acutal_nameList=[]
    for dir in file_list:
        #print os.getcwd()

        os.chdir(os.getcwd()+"/"+dir)
        for root, dirs, files in os.walk("."):#per folder
            current_author_group=[]
            for filename in files:
            #print filename
                if filename=="author_1.txt":
                    author_1 = open(filename,'r')
                    current_author_group.append (author_1.read().split('>',1)[1].split('<',1)[0])
                    author_1.close()
                if filename == "author_2.txt":
                    author_2 = open(filename, 'r')
                    current_author_group.append (author_2.read().split('>',1)[1].split('<',1)[0])
                    author_2.close()
            if len(current_author_group):
                acutal_nameList.append(current_author_group)
            os.chdir('../')

    print "Processed student list: " +  str(acutal_nameList)
    length_actualList=len(acutal_nameList)
    if length_actualList!=length_expectedlist:
        print ("Error report: ")
        print ("Length of the student name list between canvas and actually processed is different")
        print ("Unit test U_2 failed")
    for Expected_student in canvas_list:
        for Processed_students in acutal_nameList:
            for Processed_student in Processed_students:
                if Expected_student==Processed_student:
                    canvas_list.remove(Expected_student)
                    acutal_nameList.remove(Processed_students)
                    break
    if len(canvas_list)==0 and len(acutal_nameList)==0:
        print ("Unit test U_2 U_4 passed")
    elif len(canvas_list)!=0:
        print ("Error report: ")
        print ("Students: "+ str(canvas_list)+"are remain in the canvas list.")
        print ("Please check if student in the list submit the correct document and the accuracy of the program")
        print ("Unit test U_2 U_4 failed")
    elif len(acutal_nameList)!=0:
        print ("Error report: ")
        print ("Students: " + str(acutal_nameList) + "are Processed but the name are not exist in the canvas.")
        print ("Please check if student in the list submit the correct document and the accuracy of the program")
        print ("Unit test U_2 U_4 failed")


    #print(length_actualList)

    return student_list_canvas


if __name__ == '__main__':
        main()
