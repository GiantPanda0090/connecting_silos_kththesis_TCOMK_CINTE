#!/bin/bash
#install all plugin


sudo apt-get install conda



sudo apt-get install python-pip 
sudo apt-get install python3-pip

pip install -r requirements.txt --no-index --find-links file:///tmp/packages
pip3 install -r requirements.txt --no-index --find-links file:///tmp/packages
apt install -y xvfb
pip3 install pyvirtualdisplay

sudo apt-add-repository ppa:mozillateam/firefox-next
sudo apt-get update
sudo apt-get install firefox xvfb
Xvfb :10 -ac &
export DISPLAY=:10


source src/add_path.sh


