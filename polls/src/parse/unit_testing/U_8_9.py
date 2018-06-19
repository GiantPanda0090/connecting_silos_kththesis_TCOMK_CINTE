#!/usr/bin/python
#Unit Test Nr 8 and 9
#purpose: confirm consistency via HASH SHA-1 Code
#purpose: Compare answer of the example file with expected answer. Make sure the accuracy

import os,shutil
import subprocess
from external import external_hashModule
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))+"/.."  # This is your Project Root

def main():
    shutil.rmtree(ROOT_DIR+"/unit_testing"+"/actual_result")
    os.makedirs("actual_result")
    os.chdir(ROOT_DIR+"/kth_extract/pdfssa4met")
    document_type=0
    pdfpath="test_document.pdf"
    message = "python kthextract.py "+" "+"--unittest"+" "+ pdfpath + " " + str(document_type)
    os.system(message)
    pdfpath = "test_document2.pdf"
    message = "python kthextract.py " +" "+"--unittest"+" "+ pdfpath + " " + str(document_type)+" "+"--unittest"
    os.system(message)
    pdfpath = "test_document3.pdf"
    message = "python kthextract.py " +" "+"--unittest"+" "+ pdfpath + " " + str(document_type)+" "+"--unittest"
    os.system(message)
    document_type=1
    pdfpath = "test_document4.pdf"
    message = "python kthextract.py "+" "+"--unittest"+" " + pdfpath + " " + str(document_type)+" "+"--unittest"
    os.system(message)
#useing external moduel http://code.activestate.com/recipes/576973-getting-the-sha-1-or-md5-hash-of-a-directory/
    os.chdir(ROOT_DIR+"/unit_testing")

    os.chdir("expected_result")
    EX_test_document=external_hashModule.GetHashofDirs("test_document")
    print EX_test_document
    EX_test_document2=external_hashModule.GetHashofDirs("test_document2")
    print(EX_test_document2)

    EX_test_document3=external_hashModule.GetHashofDirs("test_document3")
    print(EX_test_document3)
    EX_test_document4=external_hashModule.GetHashofDirs("test_document4")
    print(EX_test_document4)


    os.chdir(ROOT_DIR+"/unit_testing")
    os.chdir("actual_result")
    AC_test_document = external_hashModule.GetHashofDirs("test_document")
    print AC_test_document
    AC_test_document2 = external_hashModule.GetHashofDirs("test_document2")
    print(AC_test_document2)

    AC_test_document3 = external_hashModule.GetHashofDirs("test_document3")
    print(AC_test_document3)
    AC_test_document4 = external_hashModule.GetHashofDirs("test_document4")
    print(AC_test_document4)
    if EX_test_document!=AC_test_document:
        print ("Error Report:")
        print ("kthextract parsing is not accuarte. Issue at file:")
        print ("test_document")
        print ("Unit test U_8_9 failed")
    if EX_test_document2 != AC_test_document2:
        print ("Error Report:")
        print ("kthextract parsing is not accuarte. Issue at file:")
        print ("test_document2")
        print ("Unit test U_8_9 failed")

    if EX_test_document3 != AC_test_document3:
        print ("Error Report:")
        print ("kthextract parsing is not accuarte. Issue at file:")
        print ("test_document3")
        print ("Unit test U_8_9 failed")

    if EX_test_document4 != AC_test_document4:
        print ("Error Report:")
        print ("kthextract parsing is not accuarte. Issue at file:")
        print ("test_document_2018")
        print ("Unit test U_8_9 failed")

    print ("\nUnit test U_8_9 passed")

if __name__ == '__main__':
        main()