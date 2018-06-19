#!/usr/bin/python


#This is the test case for Unit Test U.2 and 4
#course_id 2139(sandbox)
#assignment_id 24565 test_1
#purpose:test the consistency of the student list between parsed artical and canvas submission
#implemented

import os,sys,glob
import subprocess





import config
import json

#initialize test enviorment
Expected_kth_canvas= config.kth_canvas
#course_id 2139(sandbox)
Expected_kth_canvas_thesis_course_id = config.thesis_course_id #sandbox
#assignment_id 24565 testing 1; 24566 testing 2 ; 24567 testing 3;

def print_to_log(content):
    global output
    with open("test_log.txt", 'w') as f:
        f.write(content)
        f.write("<br \>")

        f.close
    output=output + content

def main(Expected_kth_canvas_thesis_course_id,Expcted_proporsal_assignment_id,file_list):
    global output
    output=""
    os.chdir("test_library")
    python_param= 'import list_studentList_assignment; list_studentList_assignment.main(%s,%s)' % (Expected_kth_canvas_thesis_course_id,Expcted_proporsal_assignment_id)

    message = "python3 -c "+"'" +  python_param+"'"
    #print_to_log (message)
    sub= subprocess.Popen(message, stdout=subprocess.PIPE, shell=True)
    (student_list_canvas, error) = sub.communicate()
    #print_to_log student_list_canvas
    os.chdir(os.getcwd()+ "/../../../../output/parse_result/")
    student_list_canvas=student_list_canvas.replace("[","")
    student_list_canvas=student_list_canvas.replace("]","")
    student_list_canvas=student_list_canvas.replace("'","")
    student_list_canvas=student_list_canvas.replace("<br \>","")
    canvas_list=student_list_canvas.split(",")
    for student in canvas_list:
     if str(student).isdigit() or ('@' in student):
         canvas_list.remove(student)
    print_to_log ("Canvas student list: " + str(canvas_list))
    length_expectedlist= len(canvas_list)
    canvas_nameList=[]
    profile=[]
    status = False

    acutal_nameList=[]
    for dir in file_list:
        #print_to_log os.getcwd()
        os.chdir(os.getcwd()+"/"+dir)
        for root, dirs, files in os.walk("."):#per folder
            current_author_group=[]
            json_content_output={}
            with open("output.json") as f:
                json_content_output = json.load(f)
                f.close()            #print_to_log filename
                author_1_txt=json_content_output['author_1']
                print_to_log("Author_1 is: " + author_1_txt+"<br \>")

                current_author_group.append(author_1_txt)

                if 'author_2' in json_content_output:
                    author_2_txt=json_content_output['author_2']
                    current_author_group.append(author_2_txt)
                    print_to_log("Author_2 is: " + author_2_txt + "<br \>")

            if len(current_author_group):
                acutal_nameList.append(current_author_group)
            os.chdir('../')


    print_to_log ("Processed student list: " +  str(acutal_nameList))
    length_actualList=len(acutal_nameList)
    if length_actualList!=length_expectedlist:
        print_to_log ("Error report: ")
        print_to_log ("Length of the student name list between canvas and actually processed is different")
        print_to_log ("Unit test U_2 failed")
        status=False


    for Expected_student in canvas_list:
            for Processed_students in acutal_nameList:
                for student in Processed_students:
                    compare_ex=str(Expected_student).strip().lower()
                    compare_it=str(student).strip().lower()
                    print_to_log(str(compare_ex))
                    print_to_log("vs")
                    print_to_log(str(compare_it))
                    if compare_ex == compare_it:
                        canvas_list.remove(Expected_student)
                        acutal_nameList.remove(Processed_students)
                        break


    if len(canvas_list)==0 and len(acutal_nameList)==0:
        print_to_log ("Unit test U_2 U_4 passed")
        status=True

    elif len(canvas_list)!=0:
        print_to_log ("Error report: <br \>")
        print_to_log ("Students: "+ str(canvas_list)+"are remain in the canvas list.<br \>")
        print_to_log ("Please check if student in the list submit the correct document and the accuracy of the program<br \>")
        print_to_log ("Unit test U_2 U_4 failed<br \>")
        status=False

    elif len(acutal_nameList)!=0:
        print_to_log ("Error report: <br \>")
        print_to_log ("Students: " + str(acutal_nameList) + "are Processed but the name are not exist in the canvas.<br \>")
        print_to_log ("Please check if student in the list submit the correct document and the accuracy of the program<br \>")
        print_to_log ("Unit test U_2 U_4 failed<br \>")
        status=False



    #print_to_log(length_actualList)

    return [output,status]


if __name__ == '__main__':
        main()
