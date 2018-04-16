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
import sys
from parse.kth_extract.pdfssa4met import kthextract


print os.getcwd()
print 'Preperation start'
path=os.getcwd()
print path
os.chdir(path)
os.chdir('parse/kth_extract/pdfssa4met')
print os.getcwd()
print 'Preperation done'



running_path= "kthextract.py"
pdf_path='http://kth.diva-portal.org/smash/get/diva2:953624/FULLTEXT01.pdf'
document_type="0"
student_name = "Qi_Li" #obtain from canvas
command = "python"+" "+running_path+" " + pdf_path+" " + document_type + " " +student_name





def main(argv=None):
    print("running command"+" '"+ command +"'")
    kthextract.main([pdf_path,0,student_name])
    #os.system(command)
if __name__ == '__main__':
        main()
