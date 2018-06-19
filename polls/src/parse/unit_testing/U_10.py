#!/usr/bin/python
#Unit Test Nr 10
#purpose: The combination of the front name and after name should be the same as the author_1/2
#purpose: consistency of the name

import os
import io
import itertools




ROOT_DIR = os.path.dirname(os.path.abspath(__file__))+"/../../../"  # This is your Project Root


def main(session_id):
    os.chdir(ROOT_DIR)
    os.chdir("output/parse_result")
    os.chdir(ROOT_DIR + "/output/parse_result")
    for folder_name in os.listdir('.'):
        if folder_name != "cache" and folder_name != "log.txt":
            folder_name_list = folder_name.split('_')
            if session_id == folder_name_list[3]:
                os.chdir(os.getcwd() + "/" + folder_name)
                file_list=[]
                if os.path.isfile("author_1.txt"):
                    file_list.append("author_1.txt")
                else:
                    return "No author found"
                if os.path.isfile("author_2.txt"):
                    file_list.append("author_2.txt")
                for file in file_list:

                    if os.path.isfile(file):
                        with open(file,'r') as f:
                            author_name=f.read()
                        f.close()

                        with open(str(file).split('.tx')[0]+"_frontname.txt",'r') as f:
                            frontname=f.read()
                        f.close()
                        with open(str(file).split('.tx')[0]+"_aftername.txt",'r') as f:
                            aftername=f.read()
                        f.close()

                        list = frontname.split(">")
                        if len(list) > 1:
                            frontname = list[1]
                            list = frontname.split("<")
                            frontname = list[0]
                        else:
                            frontname = list[0]

                        list = aftername.split(">")
                        if len(list) > 1:
                            aftername = list[1]
                            list = aftername.split("<")
                            aftername = list[0]
                        else:
                            aftername = list[0]

                        compare_list=[]
                        compare_list.append(frontname.strip())

                        list=aftername.split(" ")
                        for aftername in list:
                            if len(aftername):
                                compare_list.append(aftername.strip())

                        list = author_name.split(">")
                        if len(list) > 1:
                            author_name = list[1]
                            list = author_name.split("<")
                            author_name = list[0]
                        else:
                            author_name = list[0]



                        name_split=author_name.split(" ")

                        expected_list=[]
                        for element in name_split:
                            expected_list.append(element.strip())
                        print  expected_list
                        print compare_list

                        for expected, actuall in itertools.izip(expected_list,
                                                                compare_list):
                            if expected!=actuall:
                                return "U_10 Failed."+author_name+"  is not same as front and after name in session "+ session_id+"\n fullname:"+author_name+"\n frontname:"+frontname+"\n afterneme:"+aftername + "\n at element:"+expected+";"+actuall

                        return "U_10 Passed"






