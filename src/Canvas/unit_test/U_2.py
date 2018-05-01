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
    print student_list_canvas
    acutal_nameList=[]
    for dir in file_list:
        #print os.getcwd()

        os.chdir(os.getcwd()+"/"+dir)
        for root, dirs, files in os.walk("."):
            for filename in files:
            #print filename
                if filename=="author_1.txt":
                    author_1 = open(filename,'r')
                    acutal_nameList.append (author_1.read().split('>',1)[1].split('<',1)[0])
                    author_1.close()
                if filename == "author_2.txt":
                        author_2 = files.read()
                        acutal_nameList.append (author_2.read().split('>',1)[1].split('<',1)[0])
                        author_2.close()
            os.chdir('../')
    print acutal_nameList
    return student_list_canvas


if __name__ == '__main__':
        main()
