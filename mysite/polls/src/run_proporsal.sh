#!/bin/bash
#add geckodriver path 
#run the proporsal phase

path=$(pwd)
rm -rf $path/../ffdriver
mkdir $path/../ffdriver
rm -rf $path/../Source
mkdir $path/../Source
source add_path.sh 
python start_proporsal.py $1 $2 $3 $4

