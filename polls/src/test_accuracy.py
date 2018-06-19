#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from parse.kth_extract.pdfssa4met import kthextract
import json
from mods import xmlGenerator

import time



ROOT_DIR = os.path.dirname(os.path.abspath(__file__))+"/.."  # This is your Project Root
json_path ='output.json'

def start():

    download_dir=ROOT_DIR+'/Source'
    counter =0
    start = time.time()

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
    dir=""
    processed_folder=[]
    error_folder=[]
    for file in os.listdir(download_dir):
        if file.endswith(".pdf"):# if it is a pdf file
            counter+=1
            if "-" in file or "(" in file or ")" in file or " " in file:

                print "The file name is: "+ file
                #python hate '-' character. replace it with '_'
                source = os.path.join(download_dir, file)
                destination = os.path.join(download_dir, file.replace("-", "_").replace("(", "_").replace(")", "").replace(" ", "_"))
                print "After rename, The file name is: "+ destination



                os.rename(source, destination)
                file = destination
            pdf_locl_path = os.path.join(download_dir, file)
            print "found pdf file: " + pdf_locl_path
            try:
                # main process module
                dir=kthextract.main([pdf_locl_path, 0])
                print("kth extract end with: " + dir)

                if len(dir) !=0:
                    folder=ROOT_DIR+"/"+"output/parse_result/"+dir

                    modsurl = xmlGenerator.main(folder + '/output.json', folder)
                    dir=""
                    processed_folder.append(folder)

                else:
                    error_folder.count(pdf_locl_path)

            except:
                error_folder.count(pdf_locl_path)

    os.chdir(ROOT_DIR)
    end = time.time()
    print("Time to process "+str(counter)+ "amount of file is: "+ str(end - start))
    print("Failed folder: "+str(error_folder))
    print("Successed folder: "+ str(processed_folder))
    print("Length of the list is: " +str(len(processed_folder)))
    print("Done with all measurement")
    folder_list=[]
    for folder in os.listdir(ROOT_DIR+"/"+"output/parse_result/"):
           if folder not in processed_folder:
               folder_list.append(folder_list)

    print("difference folder: " + str(processed_folder))

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
    start()
