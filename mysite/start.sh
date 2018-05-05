#!/bin/bash
#start the server

path=$(pwd)
export PATH=$PATH:$path/polls/ffdriver
python manage.py runserver

