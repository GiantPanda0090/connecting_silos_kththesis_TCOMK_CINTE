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







from parse.kth_extract.pdfssa4met import kthextract
import sys, getopt
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
import shutil
import zipfile


import subprocess


import os
import time







running_path= "kthextract.py"
pdf_path='https://kth.instructure.com/courses/2139/assignments/24565/submissions/11185?download=890332'






def main(argv=None):
    argv = sys.argv[1:]

    opts, args = getopt.getopt(argv, "ht",
                                       ["help", "test", "noxml", "highlight", "title", "author", "verbose", "caps"])

    document_type = 0 #0 is thesis 1 is proporsal

    #backup solution. leave it here. if we dont use this in the end, we delete it
    #command = "python" + " " + running_path + " " + pdf_path + " " + document_type + " " + student_name


#start canvas module
    print os.getcwd()
    print 'Preperation for canvas module start'
    path = os.getcwd()
    print "Current directory: "+path
    print "jumping to canvas module path"
    os.chdir(path)
    os.chdir('Canvas/canvas')
    print "Current directory: "+os.getcwd()
    print 'Preperation for canvas module done'
    message = "python3 list_submissions.py "+ args[0]+" "+args[1]
    sub = subprocess.Popen(message, stdout=subprocess.PIPE, shell=True)

    (pdf_path, error)=sub.communicate()
    print "the output url is: "+str(pdf_path)

    print 'Automating firefox module'

    download_dir = os.getcwd()+"/../../../Source"
    shutil.rmtree(download_dir)
    os.makedirs(download_dir)    #clean up the source

    profile = webdriver.FirefoxProfile()
    option = Options()

    profile.set_preference("general.useragent.override",
                                   "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False);
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    profile.set_preference("browser.download.dir", download_dir)
    profile.set_preference("pdfjs.disabled", True)
    profile.update_preferences()


    option.profile=profile

    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    #firefox_capabilities['binary'] = 'tools/firefox/firefox-bin'
    print 'Logging in KTH'
    browser = webdriver.Firefox(capabilities=firefox_capabilities,firefox_options = opts,firefox_profile=profile)
    browser.get("https://login.kth.se/login")
    time.sleep(3)

    username = browser.find_element_by_id("username")
    password = browser.find_element_by_id("password")

    username.send_keys(args[2])
    password.send_keys(args[3])
    browser.find_element_by_name("submit").click()
    print 'Dowloading pdf..... This might take a while......'
    print "Downloading from: " + pdf_path
    browser.get(pdf_path)
    time.sleep(10)
    print 'File saved in '+ download_dir

#if the file is a package, unzip and extract it
    for file in os.listdir(download_dir):
     if file.endswith(".zip") or file.endswith(".tar") or file.endswith(".tar.gz"):
         unzip_dir=os.path.join(download_dir, file)
         print "Extracting file: " + unzip_dir
         zip_ref = zipfile.ZipFile(unzip_dir, 'r')
         zip_ref.extractall(download_dir)
         zip_ref.close()



    print 'Done with canvas module and leaving the module'

    os.chdir(path+"/../")
    print os.getcwd()



#start kthextract module
    #print("running command"+" '"+ command +"'")
    print os.getcwd()
    print 'Preperation for parse module start'
    path = os.getcwd()
    print path
    os.chdir(path)
    os.chdir('src/parse/kth_extract/pdfssa4met')
    print os.getcwd()
    print 'Preperation for the parse module done'

    for file in os.listdir(download_dir):
     if file.endswith(".pdf"):
         pdf_locl_path=os.path.join(download_dir, file)
         print "found pdf file: " + pdf_locl_path
         kthextract.main([pdf_locl_path,document_type])
    print 'Done with parse module'
    print 'Whole process done'


    #os.system(command)
if __name__ == '__main__':
        main()
