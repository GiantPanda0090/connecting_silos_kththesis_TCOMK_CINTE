#!/bin/bash
#add geckodriver path 


path=$(pwd)
export PATH=$PATH:$path/../ffdriver

mv -f geckodriver  /usr/local/bin/geckodriver

