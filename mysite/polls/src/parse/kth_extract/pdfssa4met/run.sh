#!/bin/bash
#run kthextract

echo 'Preperation start'
path=$(pwd)
echo $path
cd $path
rm -rf ../output/parse_result
mkdir ../output/parse_result
cd parse/kth_extract/pdfssa4met
pwd
echo 'Preperation done'

python kthextract.py $1 $2

