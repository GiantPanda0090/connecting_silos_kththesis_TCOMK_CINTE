#!/bin/bash
#install all plugin


sudo apt-get install conda

conda install pandas
conda install lxml

sudo apt-get install python-pip 
sudo apt-get install python3-pip

pip3 install selenium
pip install selenium
pip install lxml
pip3 install lxml

path = $(pwd)
export PATH=$PATH:$path/ffdriver


