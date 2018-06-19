#!/bin/bash
#install all plugin

sudo apt-get install python-pip 
sudo apt-get install python3-pip

pip install -r requirements.txt -

sudo apt install -y xvfb

sudo apt-add-repository ppa:mozillateam/firefox-next
sudo apt-get update
sudo apt-get install firefox xvfb
Xvfb :10 -ac &
export DISPLAY=:10


source src/add_path.sh
