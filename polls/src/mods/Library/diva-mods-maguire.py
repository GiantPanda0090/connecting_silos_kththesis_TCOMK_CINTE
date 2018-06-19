#!/usr/bin/python
# -*- coding: utf-8 -*-
# the above encoding information is as per http://www.python.org/dev/peps/pep-0263/
#
# Purpose: To parse and extract information from MODS files from DiVA
#
# Input: ./diva-mods-maguire.py -i mods-ICT-20140629.mods > mods-ICT-20140629.mods.csv
# Output: outputs a spreadhseet of the information
# note that the "-v" (verbose) argument will generate a lot of output
#
# Author: Gerald Q. Maguire Jr.
# 2014.06.24
#
#
from eulxml import xmlmap
from eulxml.xmlmap import load_xmlobject_from_file, mods
import lxml.etree as etree

import optparse
import sys
# import the following to be able to redirect stdout output to a file
#   while avoiding problems with unicode
import codecs, locale

parser = optparse.OptionParser()
parser.add_option('-i', '--input', 
                  dest="input_filename", 
                  default="default.mods",
                  )
#parser.add_option('-o', '--output', 
#                  dest="output_filename", 
#                  default="default.out",
#                  )
parser.add_option('-v', '--verbose',
                  dest="verbose",
                  default=False,
                  action="store_true",
                  help="Print lots of output to stdout"
                  )

options, remainder = parser.parse_args()

Verbose_Flag=options.verbose
if Verbose_Flag:
    print 'ARGV      :', sys.argv[1:]
    print 'VERBOSE   :', options.verbose
    print 'INPUT    :', options.input_filename
    print 'REMAINING :', remainder



#set sdout so that it can output UTF-8
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

#fileHandle=open('mods-maguire.mods', 'r')
fileHandle=open( options.input_filename, 'r')
tree=load_xmlobject_from_file(fileHandle, mods.MODS)

#<name type="personal"><namePart type="family">Abad Caballero</namePart><namePart type="given">Israel Manuel</namePart><namePart type="date">1978-</namePart><role><roleTerm type="code" authority="marcrelator">aut</roleTerm></role><affiliation>KTH, Mikroelektronik och Informationsteknik, IMIT</affiliation><affiliation>CCSlab</affiliation></name><name type="corporate"><namePart>CCSlab</namePart><role><roleTerm type="code" authority="marcrelator">oth</roleTerm></role><description>Research Group</description></name>

name_family=''
name_given=''
author_name_family=''
author_name_given=''
supervisor_name_family=''
supervisor_name_given=''
examiner_name_family=''
examiner_name_given=''
thesis_dateIssued=''
thesis_title=''
thesis_abstract_language=[]

def new_output_record():
    global name_family, name_given, author_name_family, author_name_given, supervisor_name_family, supervisor_name_given
    global examiner_name_family, examiner_name_given
    global thesis_title, thesis_abstract_language
    global thesis_dateIssued
    global thesis_url
    global thesis_url_fulltext
    global thesis_recordOrigin
#
    name_family=''
    name_given=''
    author_name_family=''
    author_name_given=''
    supervisor_name_family=''
    supervisor_name_given=''
    examiner_name_family=''
    examiner_name_given=''
    thesis_dateIssued=''
    thesis_url=''
    thesis_recordOrigin=''
    thesis_title=''
    thesis_abstract_language=[]
    thesis_url_fulltext=''

def output_column_heading():
# set the serparator to tab
    print "sep=\\t"
# output the column headings
    print "author_name_family" + "\t" + "author_name_given" + "\t" + "supervisor_name_family" + "\t" + "supervisor_name_given" + "\t" + "examiner_name_family" + "\t" +  "examiner_name_given" + "\t" + "thesis_dateIssued" + "\t" + "thesis_url"  +"\t" + "thesis_url_fulltext" + "\t" + "thesis_recordOrigin" + "\t" + "thesis_title" + "\t" + "thesis_abstract_language"


def output_current_record():
    global name_family, name_given, author_name_family, author_name_given, supervisor_name_family, supervisor_name_given
    global examiner_name_family, examiner_name_given
    global thesis_title, thesis_abstract_language
    global thesis_dateIssued
    global thesis_url
    global thesis_recordOrigin
    global thesis_url_fulltext
#
#    print name_family
#    print name_given
    print author_name_family + "\t" + author_name_given + "\t" + supervisor_name_family + "\t" + supervisor_name_given + "\t" + examiner_name_family + "\t" +  examiner_name_given + "\t" + thesis_dateIssued + "\t" + thesis_url + "\t" + thesis_url_fulltext + "\t" + thesis_recordOrigin + "\t" + thesis_title + "\t" + str(sorted(thesis_abstract_language))

def print_namePart(np):
    global name_family, name_given
#
    if Verbose_Flag:
        print "namePart: "
    if len(np.attrib) > 0:
        if Verbose_Flag:
            print np.attrib
        if np.attrib['type']:
            if np.attrib['type'].count('family') == 1 :
                name_family=np.text
            elif np.attrib['type'].count('given') == 1 :
                name_given=np.text
            else:
                if Verbose_Flag:
                    print np.attrib['type'] + " " + np.text

def print_role_term(rt):
    global name_family, name_given, author_name_family, author_name_given, supervisor_name_family, supervisor_name_given
    global examiner_name_family, examiner_name_given
#
    if Verbose_Flag:
        print "roleTerm: "
    if len(rt.attrib) > 0:
        if Verbose_Flag:
            print rt.attrib
    if rt.text is not None:
        if Verbose_Flag:
            print rt.text
    if rt.text.count('aut') == 1:
        author_name_family = name_family
        author_name_given = name_given
        if Verbose_Flag:
            print "author_name_family: " + author_name_family
            print "author_name_given: " + author_name_given
    elif rt.text.count('ths') == 1:
        supervisor_name_family = name_family
        supervisor_name_given = name_given
        if Verbose_Flag:
            print "supervisor_name_family: " + supervisor_name_family
            print "supervisor_name_given: " + supervisor_name_given
    elif rt.text.count('mon') == 1:
        examiner_name_family = name_family
        examiner_name_given = name_given
        if Verbose_Flag:
            print "examiner_name_family: " + examiner_name_family
            print "examiner_name_given: " + examiner_name_given
#
    if Verbose_Flag:
        print "name_family: " + name_family
        print "name_given: " + name_given

#<role><roleTerm
def print_role(r):
    if Verbose_Flag:
        print "role :"
    if len(r.attrib) > 0:
        if Verbose_Flag:
            print r.attrib
    if r.text is not None:
        if Verbose_Flag:
            print r.text
    for i in range(0, len(r)):
        rt=r[i]
        if rt.tag.count("}roleTerm") == 1:
            print_role_term(rt)
        else:
            if Verbose_Flag:
                print "rt[" + str(i) +"]"
                print rt

            
def print_affiliation(a):
    if Verbose_Flag:
        print "affiliation :"
    if len(a.attrib) > 0:
        if Verbose_Flag:
            print a.attrib
    if a.text is not None:
        if Verbose_Flag:
            print a.text

def print_description(d):
    if Verbose_Flag:
        print "description: "
    if len(d.attrib) > 0:
        if Verbose_Flag:
            print d.attrib
    if d.text is not None:
        if Verbose_Flag:
            print d.text

def print_name(mod_elem):
    if Verbose_Flag:
        print "Name: "
        print "Name attribute: " + str(mod_elem.attrib)
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}namePart") == 1:
            print_namePart(elem)
        elif elem.tag.count("}role") == 1:
            print_role(elem)
        elif elem.tag.count("}affiliation") == 1:
            print_affiliation(elem)
        elif elem.tag.count("}description") == 1:
            print_description(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(n) +"]"
                print elem

def print_title(elem):
    global thesis_title
    if Verbose_Flag:
        print "title: "
    if len(elem.attrib) > 0:
        if Verbose_Flag:
            print elem.attrib
    if elem.text is not None:
        thesis_title=elem.text
        if Verbose_Flag:
            print elem.text


def print_titleInfo(mod_elem):
    if Verbose_Flag:
        print "TitleInfo: "
    if len(mod_elem.attrib) > 0:
        if Verbose_Flag:
            print mod_elem.attrib
    if mod_elem.text is not None:
        if Verbose_Flag:
            print mod_elem.text
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}title") == 1:
            print_title(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem


def print_languageTerm(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print "LanguageTerm: "
            print elem.text
    
def print_language(mod_elem):
    if Verbose_Flag:
        print "Language: "
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}languageTerm") == 1:
            print_languageTerm(elem)
        elif elem.tag.count("}dateIssued") == 1:
            print_dateIssued(elem)
        elif elem.tag.count("}dateOther") == 1:
            print_datedateOther(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem


def print_dateIssued(elem):
    global thesis_dateIssued
    if elem.text is not None:
        thesis_dateIssued=elem.text
        if Verbose_Flag:
            print "dateIssued: "
            print elem.text


def print_datedateOther(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print "dateOther: "
            print elem.attrib
            print elem.text

def print_originInfo(mod_elem):
    if Verbose_Flag:
        print "originInfo: "
#       print mod_elem
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}languageTerm") == 1:
            print_languageTerm(elem)
        elif elem.tag.count("}dateIssued") == 1:
            print_dateIssued(elem)
        elif elem.tag.count("}dateOther") == 1:
            print_datedateOther(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem

def print_identifier(elem):
    global thesis_url
    if elem.text is not None:
        thesis_url=elem.text
        if Verbose_Flag:
            print "identifier: "
            print elem.text


def print_abstract(mod_elem):
    global thesis_abstract_language
    if Verbose_Flag:
        print "Abstract: "
        print "Attrib: "
    if len(mod_elem.attrib) > 0:
        thesis_abstract_language.append(mod_elem.attrib['lang'])
        if Verbose_Flag:
            print mod_elem.attrib
    if mod_elem.text is not None:
        if Verbose_Flag:
            print mod_elem

def print_recordOrigin(elem):
    global thesis_recordOrigin
    if elem.text is not None:
        thesis_recordOrigin=elem.text
        if Verbose_Flag:
            print elem.text

def print_recordContentSource(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print elem.text

def print_recordCreationDate(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print elem.text

def print_recordChangeDate(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print elem.text


def print_recordIdentifier(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print elem.text


#<recordContentSource>kth</recordContentSource><recordCreationDate>2012-04-11</recordCreationDate><recordChangeDate>2013-09-09</recordChangeDate><recordIdentifier>diva2:515038</recordIdentifier></recordInfo>
def print_recordInfo(mod_elem):
    if Verbose_Flag:
        print "recordInfo: "
        print mod_elem
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}recordOrigin") == 1:
            print_recordOrigin(elem)
        elif elem.tag.count("}recordContentSource") == 1:
            print_recordContentSource(elem)
        elif elem.tag.count("}recordCreationDate") == 1:
            print_recordCreationDate(elem)
        elif elem.tag.count("}recordChangeDate") == 1:
            print_recordChangeDate(elem)
        elif elem.tag.count("}recordIdentifier") == 1:
            print_recordIdentifier(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem
        


def print_subject(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print "subject: "
            print elem

def print_url(elem):
    global thesis_url_fulltext
    if elem.text is not None:
        thesis_url_fulltext=elem.text
        if Verbose_Flag:
            print "url: "
            print elem.text


def print_location(mod_elem):
#    print "location: "
#    print mod_elem.tag
#    print mod_elem.text
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}url") == 1:
            print_url(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem

#tree.node
#<Element {http://www.loc.gov/mods/v3}modsCollection at 0x34249b0>
#>>> tree.node[1]
#<Element {http://www.loc.gov/mods/v3}mods at 0x3d46aa0>

output_column_heading()
for i in range(0, len(tree.node)):
    if tree.node[i].tag.count("}modsCollection") == 1:
# case of a modsCollection
        if Verbose_Flag:
            print "Tag: " + tree.node[i].tag
            print "Attribute: "
            print tree.node[i].attrib
# case of a mods
    elif tree.node[i].tag.count("}mods") == 1:
        if Verbose_Flag:
            print "new mods Tag: " + tree.node[i].tag
#  print "Attribute: " + etree.tostring(tree.node[i].attrib, pretty_print=True) 
            print "Attribute: " 
            print tree.node[i].attrib
#
# print information about the publication
#
        new_output_record()
#
        current_mod=tree.node[i]
        if Verbose_Flag:
            print "Length of mod: "+ str(len(current_mod))
        for mod_element in range(0, len(current_mod)):
            current_element=current_mod[mod_element]
            if Verbose_Flag:
                print "TAG: " 
                print current_element
            if current_element.tag.count("}name") == 1:
                print_name(current_element)
            elif current_element.tag.count("}titleInfo") == 1:
                print_titleInfo(current_element)
            elif current_element.tag.count("}language") == 1:
                print_language(current_element)
            elif current_element.tag.count("}originInfo") == 1:
                print_originInfo(current_element)
            elif current_element.tag.count("}identifier") == 1:
                print_identifier(current_element)
            elif current_element.tag.count("}abstract") == 1:
                print_abstract(current_element)
            elif current_element.tag.count("}subject") == 1:
                print_subject(current_element)
            elif current_element.tag.count("}recordInfo") == 1:
                print_recordInfo(current_element)
            elif current_element.tag.count("}location") == 1:
                print_location(current_element)
#
        output_current_record()
    else:
        if Verbose_Flag:
            print "Tag: " + tree.node[i].tag


