#!/bin/bash
#run kthextract

rm -rf ../../../../output/parse_result
mkdir ../../../../output/parse_result

python kthextract.py $1 $2

