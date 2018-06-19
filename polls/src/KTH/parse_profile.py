import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

# Use Python Pandas to create XLSX files
import pandas as pd




with open('KTHconfig.json') as json_data_file:
       configuration = json.load(json_data_file)
       
       baseUrl="https://"+configuration["kth"]["host"]+"/api/profile/1.1/"
print "dealing with" + baseUrl
      
payload = {}

def get_user_info(userid): 

   
    info_found = []
    url = baseUrl +(userid)

    print("url: " + url)

    r = requests.get(url)

    if r.status_code == requests.codes.ok:
        page_response=r.json()

       
    for p_response in page_response:  
        info_found.append(p_response)

    #while r.links['current']['url'] != r.links['last']['url']:  
            #  r = requests.get(r.links['next']['url'], headers=header)  
             # page_response = r.json()  
              #for p_response in page_response:  
                  #   info_found.append(p_response)

    print(r.json())
    return r.json()



if __name__ == "__main__":
    get_user_info(sys.argv[1])
