import subprocess
import os
import sys
import shutil
import optparse


def start():
	mods_list=[]
	location=""
	parser = optparse.OptionParser()
	options, remainder = parser.parse_args()
	if (len(remainder) < 1):
		print("Insuffient arguments\n must provide path to the mods file\n")
	else:
		location=remainder[0]
	print('input location: '+ location)
	#preperation
	shutil.rmtree("bin/bib_out")
	os.mkdir("bin/bib_out")
	shutil.rmtree("output")
	os.mkdir("output")
	#Connecting silo mods to bibtex
	for folder in os.listdir(location):
		folder_loc = os.path.join(location, folder)
		for file in os.listdir(folder_loc):
			if file.endswith(".mods"):# if it is a pdf file
				source = os.path.join(folder_loc, file)
				message = "./bin/xml2bib " +"'"+ source+"'"+" >"+  "bin/bib_out/"+folder+"_bib.bib"
				print("processing command: "+message)

				sub = subprocess.Popen(message, stdout=subprocess.PIPE, shell=True)
				(mods_path, error) = sub.communicate()
				mods_list.append(source)
	#merge bibtex file
	message="cat bin/bib_out/* > output/result.bib"
	sub = subprocess.Popen(message, stdout=subprocess.PIPE, shell=True)
	(mods_path, error) = sub.communicate()
	print('ALL PROCESS DONE!')


if __name__ == '__main__':
    sys.exit(start())
