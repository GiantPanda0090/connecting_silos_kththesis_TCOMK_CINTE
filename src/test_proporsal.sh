#!/bin/bash
#add geckodriver path 
#test script.... delete before deployed

path=$(pwd)
rm -rf $path/../ffdriver
mkdir $path/../ffdriver
rm -rf $path/../Source
mkdir $path/../Source
source add_path.sh 
python start_proporsal.py 2139 24565 shivabp IBstar1998

