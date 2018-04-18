#!/usr/bin/python2.6
#
# ./KTHID-to-last-firstname-list.py list_of_KTHIDs
#
# outputs a CSV file with columns: KTHID,Last_name,First_name
#
# G. Q. Maguire Jr.
#
# 2016.12.26
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

log_file = 'log.txt' # a log file. it will log things


def write_to_log(message):

       with open(log_file, 'a') as log:
              log.write(message + "\n")
              pprint(message)

from commands import getoutput
import base64

def gqm_extract(key, ldap_response):
       lines=ldap_response.split('\n')
       for l in lines:
              wl=l.replace("\r", "")
              # check for base64 encoded name (indicated by a key with two colons)
              keyb64=key+':'
              if wl.startswith(keyb64):
                     return base64.b64decode(wl[wl.find(key)+len(key)+2:])
              if wl.startswith(key):
                     return wl[wl.find(key)+len(key)+1:]

def lookup_names(list_of_names_file, augmented_list_of_names_file):
    with open(augmented_list_of_names_file, 'w') as outfile:
        #with open(list_of_names_file, 'r', encoding='utf-8') as infile:
        with open(list_of_names_file, 'r') as infile:
            header='KTHID,Last_name,First_name\n'
            outfile.write(header)
            for line in infile:
                line2=line.replace("\n", "")
                line3=line2.replace("\r", "")
                cmdline='ldapsearch -x  -H ldaps://ldap-master.sys.kth.se -b ou=Addressbook,dc=kth,dc=se ugKthid='+line3
                if Verbose_Flag:
                       print('cmdline: ', cmdline)
                result = getoutput(cmdline)
                #parse result for:
                #  givenName: 
                #  sn: 
                last_name=gqm_extract('sn:', result)
                first_name=gqm_extract('givenName:', result)
                output_line=line3+','+last_name+','+first_name+'\n'
                if Verbose_Flag:
                       print(result)
                outfile.write(output_line)

def main():
       global Verbose_Flag

       parser = optparse.OptionParser()

       parser.add_option('-v', '--verbose',
                         dest="verbose",
                         default=False,
                         action="store_true",
                         help="Print lots of output to stdout"
       )

       options, remainder = parser.parse_args()

       Verbose_Flag=options.verbose
       if Verbose_Flag:
              print('ARGV      :', sys.argv[1:])
              print('VERBOSE   :', options.verbose)
              print('REMAINING :', remainder)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   

       if (len(remainder) < 1):
              print("Insuffient arguments\n must provide list_of_KTHIDs filename\n")
       else:
              list_of_KTHIDs_file_name=remainder[0]
              augmented_list_of_names_file=list_of_KTHIDs_file_name[:-4]+'-augmented'+'.csv'
              print('list_of_KTHIDs_file_name: ', list_of_KTHIDs_file_name)
              print('augmented_list_of_names_file: ', augmented_list_of_names_file)
              lookup_names(list_of_KTHIDs_file_name, augmented_list_of_names_file)

       # add time stamp to log file
       log_time = str(time.asctime(time.localtime(time.time())))
       write_to_log(log_time)   
       write_to_log("\n--DONE--\n\n")

if __name__ == "__main__": main()

