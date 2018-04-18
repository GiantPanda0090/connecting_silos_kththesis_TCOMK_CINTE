#!/usr/bin/python
""" Extract and tag References from a PDF.

Usage: kthextract.py OPTIONS FILEPATH

based upon John Harrison's headings.py

Note that you need to install pdfssa4met
(available from http://code.google.com/p/pdfssa4met/ ).

Modified on 2015.06.10
@author: Gerald Q. Maguire Jr.

This is designed to work on a document with the KTH cover page as from my template:

Title on the cover is in 24 point font
Subtitle on the cover is in ~20 point font (pdfxml says it is 19.98 point)

Author is on the cover in 16 point font (pdfxml says it is 16.02 point)

The Abstract page begins with the word Abstract

The Sammanfattning page begins with the word Sammanfattning


------------
Created on Mar 1, 2010
@author: John Harrison

Usage: headings.py OPTIONS FILEPATH

OPTIONS:
--help, -h     Print help and exit
--noxml        Do not tag individual headings with XML tags.
                Default is to include tagging.
--title        Only print title then exit
--author       Only print author then exit
--caps         Look for ABSTRACT, SAMMANFATTNING in all caps, rather than set in a different font size
--verbose      Output lots of information


"""
import urllib2
#import requests

import os

import sys, getopt
from lxml import etree
from utils import UsageError, ConfigError, mean, median
from pdf2xml import pdf2etree

# text to filter out from the output
text_to_filter = {
    'K T H R O Y A L I N S T I T U T E O F T E C H N O L O G Y',
    'E L E C T R I C A L E N G I N E E R I N G A N D C O M P U T E R S C I E N C E'
    'K T H E l e c t r i c a l E n g i n e e r i n g a n d',
    'C o m p u t e r S c i e n c e',
    'Acknowledgements',
    'Abbreviations and Acronyms'
}

# markers used to stop outputting parts of the documents - so that only the pages before the Table of Contents are output
text_start_to_exclude = {
    'Table of contents',
    'Contents',
    'Abbreviations and Acronyms',
    'Acknowledgments'
}

#setting the flag to True - makes the program output a lot more information
Verbose_flag = False


Found_abstract = False
Found_Sammanfattning = False
automatic_rerunning=False

def filter_headings(h1):
    global Verbose_flag
    if h1 in text_to_filter:
        if Verbose_flag:
            print "excluding h1=" + h1
        return ""
    else:
        return h1

def output_text_on_block_on_page(a_page_node, starting_block, page_number, filename):
        page_txts = []
        next_page_tag = True
        print "output_blocks_on_page = " + str(page_number)
        print "starting_block=" + str(starting_block)
        local_block_number = 0
        next_block_tag =True
        st_list =["<Author>","<Address_line1>","<Address_line2>","<Email>","<PhoneNumber>","<Other_info>"]
        et_list =["</Author>","</Address_line1>","</Address_line2>","</Email>","</PhoneNumber>","</Other_info>"]
        global address
        author_count=0

            # print a_page_node
        for block_node in a_page_node.xpath('.//BLOCK'):  # all the blocks in a page
                if next_block_tag == False:
                    break
                local_block_number = local_block_number + 1
                if local_block_number <= starting_block:
                    continue

                if look_for_all_caps_headings:
                    check_headers_1 = block_node.xpath(
                        ".//TOKEN[@font-size > {0} or @bold = 'yes']".format(mean_font_size,main_font_color))
                else:
                    check_headers_1 = block_node.xpath(".//TOKEN[@font-size > {0} or @bold = 'yes' ]".format(mean_font_size * 1.05))
                print "mean font size is detected as: " + str(mean_font_size * 1.05)

                check_headers_txt_1 = ' '.join(
                    [etree.tostring(el, method='text', encoding="UTF-8") for el in check_headers_1])
                #print check_headers_txt_1
                local_text_number = 0
                for text_node in block_node.xpath('.//TEXT'):  # all the blocks in a page
                  #if local_text_number <= 5:
                      #continue
                  st=""
                  et=""
                  st = st_list[local_text_number]
                  et = et_list[local_text_number]
                # print "check header: " + check_headers_txt
                  headers = text_node.xpath(".//TOKEN[@font-size > {0} ]".format(9))
                  page_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in headers])

                  #font text debug
                  font=text_node.xpath(".//TOKEN[@font-name = dejavusans]")
                  font_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in font])
                  print font_txt
                  if len(check_headers_txt_1): #check title to skip
                         print "check header: " + check_headers_txt_1
                         print "page text: " + page_txt
                         if (check_headers_txt_1 == page_txt):
                            print "time to leave!!!!!!!!!!!!!!!!!!!!!!!!!"
                            next_block_tag = False
                            break
                  if len(page_txt):
                    # print page_txt
                    print page_txt
                    save_path= None
                    local_text_number = local_text_number + 1
                    if (local_text_number>5):
                        local_text_number=5
                    if (st == "<Author>" and author_count <2):
                        author_count+=1
                        name_split = page_txt.split();
                        save_path= '../../../../output/parse_result/'+directiory+'/author_'+str(author_count)+'_frontname'+'.txt'
                        txt = "<FrontName>" + name_split[0] + "</FrontName>"
                        with open(save_path, 'w') as f:
                            print >> f, txt, "\n"  # print tag information to certain file
                        save_path = '../../../../output/parse_result/'+directiory+'/author_' + str(
                            author_count) + '_aftername' + '.txt'
                        txt = "<AfterName>" + name_split[1] + "</AfterName>"
                        with open(save_path, 'w') as f:
                            print >> f, txt, "\n"  # print tag information to certain file

                        save_path = '../../../../output/parse_result/'+directiory+'/author_' + str(
                            author_count) + '.txt'
                        page_txts.append("{0}{1}{2}".format(st, page_txt, et))  # text append

                    if (st == "<Address_line1>"):
                        address=page_txt+" " ;
                    if (st == "<Email>"):
                        save_path = '../../../../output/parse_result/'+directiory+'/author_email_'+str(author_count)+'.txt'
                        page_txts.append("{0}{1}{2}".format(st, page_txt, et))  # text append

                    if (st == "<PhoneNumber>"):
                        save_path = '../../../../output/parse_result/'+directiory+'/author_PhoneNumber_'+str(author_count)+'.txt'
                        page_txts.append("{0}{1}{2}".format(st, page_txt, et))  # text append

                    if (st == "<Other_info>"):
                        save_path = '../../../../output/parse_result/'+directiory+'/author_Other_info_'+str(author_count)+'.txt'
                        page_txts.append("{0}{1}{2}".format(st, page_txt, et))  # text append

                    if (st == "<Address_line2>"):
                        page_txts.append("{0}{1}{2}{3}".format(st,address,page_txt,et))  # text append
                        save_path = '../../../../output/parse_result/'+directiory+'/author_address_'+str(author_count)+'.txt'

                    if (save_path!=None):
                      with open(save_path, 'w') as f:
                            for txt in page_txts:
                                # sys.stdout.writelines([txt, '\n'])#print append text #txt is per line
                                print txt + "in" + save_path
                                print >> f, txt, "\n"  # Python 2.x
                                page_txts = []


# Note that this code filters out text that is smaller than 9 points
#Exaple print:
#Abstract (en): (keyword)
#output_blocks_on_page = 5
#starting_block=2
#<p>Piezoelectric energy harvesting has been around for almost a decade to generate</p>
#<p>power from the ambient vibrations. Although the generated power is very small, but</p>
#<p>there are several ways to increase and enhance the generated power. This project</p>
#<p>presents different methods of optimizing the output power by changing the structural</p>
#<p>configuration of the energy harvesters, selection of piezoelectric material and circuit</p>
#<p>interface of these harvesters. To understand the different steps of the enhancement,</p>
#<p>the process of energy conversion by piezoelectric material has been first looked at.</p>
#<p>Different groups of piezoelectric material were studied to see what kind of materials</p>
#<p>have the ability of increasing the generated power. As mechanical configuration of the</p>
#<p>energy harvesters has a significant effect on the output voltage, their configuration</p>
#<p>such as Cantilever beam type, Cymbal type and Circular diaphragms has been</p>
#<p>described and compared. After the power generated in the piezoelectric crystal , the</p>
#<p>current is sent to through an interface circuit to get rectified and regulated. This circuit</p>
#<p>can be modified to increase the power as well. There are several types of circuits that</p>
#<p>can increase the output voltage significantly. Synchronized Switch Harvesting (SSH)</p>
#<p>techniques, Synchronous Electric Charge Extraction technique and voltage doubler</p>
#<p>are such examples. These techniques have been also studied and compared.</p>
#<p>Because of the outgrowing industry of piezoelectric energy harvesting in Medical</p>
#<p>field, their function and their progress has also been reviewed.</p>
#print block search OBS this function do not print tag search. tag search print afterwards in the end of pdf2heads
def output_blocks_on_page(a_page_node, starting_block, page_number,filename,chapter):
   page_txts=[]
   next_page_tag=True
   while next_page_tag: #per page
    print "output_blocks_on_page = " + str(page_number)
    print "starting_block=" + str(starting_block)
    local_block_number=0
    #print a_page_node
    for block_node in a_page_node.xpath('.//BLOCK'): #all the blocks in a page
        local_block_number=local_block_number+1
        if local_block_number <= starting_block:
            continue
        st = "<p>"
        et = "</p>"

        if look_for_all_caps_headings:
            check_headers = block_node.xpath(".//TOKEN[@font-size > {0} or @bold = 'yes' ]".format(mean_font_size))
        else:
            check_headers = block_node.xpath(".//TOKEN[@font-size > {0} or @bold = 'yes' ]".format(mean_font_size * 1.05))
        #print "mean front size is detected as: " + (mean_font_size * 1.05)
        check_headers_txt =' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in check_headers])
        #print "check header: " + check_headers_txt


        headers = block_node.xpath(".//TOKEN[@font-size > {0}]".format(9))
        page_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in headers])

       
        if len(check_headers_txt):
           print "check header: " + check_headers_txt
           print "page text: " + page_txt
           print "check standard: " + str(chapter) + "."
           print chapter
           if (check_headers_txt == page_txt and check_headers_txt.find(str(chapter) + ".") < 0):
               print "time to leave!!!!!!!!!!!!!!!!!!!!!!!!!"
               next_page_tag = False
               break
        
        if len(page_txt):
             org_split=[]

             if page_txt.find( "Organization:")>=0:
                print "Orgnization (en): Found"
                org_split = page_txt.split();

                count = 0
                for txt in org_split:
                    print "txt is: " + txt
                    if txt.find(":") >= 0:
                        print "found!!!!! :"
                        while count > 0:
                            del org_split[count]
                            count -= 1
                        break
                    count += 1

                save_path = '../../../../output/parse_result/'+directiory+'/Orgnization.txt'
                org_split[0]="<Orgnization>"
                org_split.append("</Orgnization>")

             if page_txt.find("Supervisor:") >= 0:
                print "Supervisor (en): Found"
                org_split = page_txt.split();

                count = 0
                for txt in org_split:
                    print "txt is: " + txt
                    if txt.find(":") >= 0:
                        print "found!!!!! :"
                        while count > 0:
                            del org_split[count]
                            count -= 1
                        break
                    count += 1

                save_path = '../../../../output/parse_result/'+directiory+'/Supervisor.txt'
                org_split[0] = "<Supervisor>"
                org_split.append("</Supervisor>")
             if (page_txt.find("Examiner") >= 0) or ((page_txt.find("Examiner") >= 0) and (page_txt.find("name")>= 0)):
                print "Examiner (en): Found"
                org_split = page_txt.split();
                count = 0
                for txt in org_split:
                    print "txt is: "+txt
                    if txt.find(":") >=0:
                        print "found!!!!! :"
                        while count>0:
                            del org_split[count]
                            count-=1
                        break
                    count += 1


                save_path = '../../../../output/parse_result/'+directiory+'/Examiner.txt'
                org_split[0] = "<Examiner>"
                org_split.append("</Examiner>")


             if len(org_split):
              i=0
              prt_str =""
              while (i<len(org_split)):
                 prt_str=prt_str+" "+org_split[i]
                 i+=1

                # text append

              with open(save_path, 'w') as f:
                        print >> f, prt_str  # print tag information to certain file #print page_txt
             page_txts.append("{0}{1}{2}".format(st, page_txt, et))#text append
    if (next_page_tag):
        #ready for next page
      page_number+=1
      starting_block=0
      a_page_node = tree.xpath('//PAGE[{0}]'.format(page_number)) [0]
      #print a_page_node

    with open(filename, 'w') as f:
        for txt in page_txts:
            #sys.stdout.writelines([txt, '\n'])#print append text #txt is per line
            print >> f,txt, "\n"   # Python 2.x

#reference https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
def hasNumbers(inputString):
     return any(char.isdigit() for char in inputString)

#scan the PDF file for headers
def pdf2heads(opts, args,document):
    global Verbose_flag
    xmltag = True
    highlight = False
    titleonly = False
    authonly = False
    Verbose_flag = False
    global look_for_all_caps_headings
    look_for_all_caps_headings = False
    global automatic_rerunning
    global Found_Heading
    global Found_abstract
    global Found_org
    global Found_key
    global Found_Author
    global Found_Sammanfattning
    global Found_Method
    global Found_Introduction
    global Found_TOC
    global abstractOut_path
    global OrgandSup_path
    global referat_path
    global methodOut_path
    global introductionOut_path
    global toc_path
    global heading_path
    global title_path
    global author_path
    global subtitle_path
    global end_tag
    global tree
    global mean_font_size
    global main_font_color
    global document_type

    document_type=document



    start_to_exclude = False

    for o, a in opts:
        if (o == '--noxml'):
            xmltag = False
        elif (o == '--highlight'):
            highlight = True
        if (o == '--title'):
            titleonly = True
        elif (o == '--author'):
            authonly = True
        elif (o == '--verbose'):
            Verbose_flag = True
            print "Verbose_flag is on"
        elif (o == '--caps'):
            print "looking for ABSTRACT and other headers in all caps"
            look_for_all_caps_headings = True

    if automatic_rerunning:
        print "looking for ABSTRACT and other headers in all caps"
        look_for_all_caps_headings = True
            
    tree = pdf2etree(args)



    # find title - look on the first page of the document at the first block of text on the page
    page = 1
    block = 1
    title_node = None
    while (page < 2):
        try:
            trial_title_node = tree.xpath("//PAGE[{0}]//BLOCK[{1}]".format(page, block))[0]

            if Verbose_flag:#verse flag
                print "trial_title_node:"
                print trial_title_node

#            title_headers = trial_title_node.xpath(".//TOKEN[@font-size > {0}]".format(23))
# note that the Title is assumed to be 20 points or larger in size
            title_headers = trial_title_node.xpath(".//TOKEN[@font-size > {0}]".format(20))

            if Verbose_flag:#verse flag
                print "title_headers:"
                print title_headers

            title_head_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in title_headers])
            if len(title_head_txt):#sucess title found
                print "Title: found"
                title_path = '../../../../output/parse_result/'+directiory+'/title.txt'
                txt = "<Title>" + title_head_txt + "</Title>"
                with open(title_path, 'w') as f:
                    print >> f, txt, "\n"  # print tag information to certain file
                title_node=trial_title_node
                next_block=block+1
                break
            block =block+1
        except IndexError: page+=1

    # find subtitle - note that a subtitle is option - start on the 2nd page and second block on the page
    # WRONG SECOND PAGE IS TABLE OF CONTENt.
    page = 1
    block = 1
    next_block=2
    subtitle_node = None
    while (page < 2):
        try:
            trial_subtitle_node  = tree.xpath("//PAGE[{0}]//BLOCK[{1}]".format(page, block))[0]
            if Verbose_flag:
                print "trial_subtitle_node:"
                print trial_subtitle_node

# the Subtitle is assumed to be larger than 19 points
            subtitle_headers = trial_subtitle_node.xpath(".//TOKEN[@font-size < {0} and @bold = 'no']".format(20))
            if Verbose_flag:
                print "subtitle_headers:"
                print subtitle_headers 

            subtitle_head_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in subtitle_headers])
            if len(subtitle_head_txt):
                print "Subtitle: found"
                subtitle_path = '../../../../output/parse_result/'+directiory+'/subtitle.txt'
                txt = "<Subtitle>" + title_head_txt + "</Subtitle>"
                with open(subtitle_path, 'w') as f:
                    print >> f, txt, "\n"  # print tag information to certain file
                subtitle_node=trial_subtitle_node
                next_block=3
                break
            block =block + 1

        except IndexError: block+=1
    
    # find author - on cover page
    Found_Author=False
    author_path = '../../../../output/parse_result/'+directiory+'/author_detail.txt'
    frontname_path = '../../../../output/parse_result/'+directiory+'/front_name.txt'
    aftername_path = '../../../../output/parse_result/'+directiory+'/after_name.txt'
    page = 1
    block = 1
    auth_node = None
    auth_count=0
    while (page < 2):
        try:
            trial_auth_node  = tree.xpath("//PAGE[{0}]//BLOCK[{1}]".format(page, block))[0]
            if Verbose_flag:
                print "trial_auth_node:"
                print trial_auth_node

# the author's name(s) is(are) assumed to be smaller than title   bigger than   degree project...
            auth_headers = trial_auth_node.xpath(".//TOKEN[@font-size < {0} and @bold = 'yes' and @font-size > {1}]".format(20,15))

            print auth_headers
            if Verbose_flag:
                print "auth_headers:"
                print auth_headers
            print document_type
            auth_head_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in auth_headers])

            if (len(auth_head_txt)>0) and auth_count<2: #found
                print "Author: found"
                auth_count +=1

                name_split = auth_head_txt.split();
                txt = "<Author>" + auth_head_txt + "</Author>"
                author_path = '../../../../output/parse_result/'+directiory+'/author_'+str(auth_count)+'.txt'

                with open(author_path, 'w') as f:
                    print txt + "in" + author_path
                    print >> f, txt, "\n"  # print tag information to certain file
                txt = "<FrontName>" + name_split[0] + "</FrontName>"

                frontname_path = '../../../../output/parse_result/'+directiory+'/author_'+str(auth_count)+'_frontname'+'.txt'

                with open(frontname_path, 'w') as f:
                    print txt + "in" + frontname_path
                    print >> f, txt, "\n"  # print tag information to certain file
                txt = "<AfterName>" + name_split[1] + "</AfterName>"

                aftername_path = '../../../../output/parse_result/'+directiory+'/author_'+str(auth_count)+'_aftername'+'.txt'

                with open(aftername_path, 'w') as f:
                    print txt + "in" + aftername_path
                    print >> f, txt, "\n"  # print tag information to certain file
                auth_node=trial_auth_node

            block =block+1
        except IndexError: page+=1

    font_sizes = tree.xpath('//TOKEN/@font-size')
    mean_font_size = mean(font_sizes)
    median_font_size = median(font_sizes)

#    print "Median Font Size (i.e. body text):", median_font_size

    font_colors = tree.xpath('//TOKEN/@font-color')
    font_color_hash = {}
    for fc in font_colors:
        try:
            font_color_hash[fc]+=1
        except KeyError:
            font_color_hash[fc] = 1

    sortlist = [(v,k) for k,v in font_color_hash.iteritems()]
    sortlist.sort(reverse=True)
    main_font_color = sortlist[0][1]
    head_txts = []
    stop = False

    page = 0
    Found_abstract = False
    Found_org=False
    Found_key = False
    Found_Sammanfattning = False
    Found_Method = False
    Found_Introduction = False
    Found_TOC = False
    OrgandSup_path = '../../../../output/parse_result/'+directiory+'/Orignization_supervisor(en).txt'
    key_path = '../../../../output/parse_result/'+directiory+'/Keyword(en).txt'
    abstractOut_path = '../../../../output/parse_result/'+directiory+'/abstract(en).txt'
    referat_path = '../../../../output/parse_result/'+directiory+'/referat(sv).txt'
    methodOut_path = '../../../../output/parse_result/'+directiory+'/method(en).txt'
    toc_path = '../../../../output/parse_result/'+directiory+'/toc(en).txt'
    introductionOut_path = '../../../../output/parse_result/'+directiory+'/introduction(en).txt'
    heading_path = '../../../../output/parse_result/'+directiory+'/heading.txt'
    title_path = '../../../../output/parse_result/'+directiory+'/title.txt'


    #page node
    for page_node in tree.xpath('//PAGE'):
        page = page+1
        block_number=0
        for block_node in page_node.xpath('.//BLOCK'):
            block_number = block_number+1
            if xmltag:
#specify data mining model
#all gone to heading....not working!!

                if block_node == title_node:#found title
                    st = "<title>"
                    et = "</title>"
                if block_node == subtitle_node:#found subtitle
                    st = "<subtitle>"
                    et = "</subtitle>"
                elif block_node == auth_node:#found author #not working
                    st = "<author>"
                    et = "</author>"
                else:
                    st = "<heading>"
                    et = "</heading>"#found other headings
                    
                if highlight:
                    st = "\033[0;32m{0}\033[0m".format(st)
                    et = "\033[0;32m{0}\033[0m".format(et)
            else:
                st = et = ""
            if block_node == title_node and authonly:
                continue
# note that the assumption that the Abstract headings is set in a larger font then the median font sized used on a page, will not find
# abstracts of Aalto university - as they set the word ABSTRACT in a slightly larger size font as used for the rest of the text, but they do set it in all CAPs
            if look_for_all_caps_headings:
                headers = block_node.xpath(".//TOKEN[(@font-size > {0} and @bold = 'yes') or @font-color != '{1}']".format(mean_font_size, main_font_color))
            else:
                headers = block_node.xpath(".//TOKEN[(@font-size > {0} and @bold = 'yes') or @font-color != '{1}']".format(mean_font_size*1.05, main_font_color))

            head_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in headers])

           # print head_txt
            if head_txt in text_start_to_exclude:
                start_to_exclude = True
            head_txt=filter_headings(head_txt)


            if len(head_txt) and (not start_to_exclude):
                head_txts.append("{0}{1}{2}".format(st, head_txt, et)) #append st tag_content andet

                # model for proposal
            if (int(document_type) == 1):
             print "first content check: "+head_txt
             if head_txt.find("Authors") >= 0 or head_txt.find("Author") >= 0:
                        if not Found_Author:  # if the abstract has not been found yet
                            print "Authors(en): OVERIDE "
                            print "Authors and detail information (en): found "
                            output_text_on_block_on_page(page_node, block_number, page, author_path)
                            Found_Author = True


             if head_txt.find("Organization and Supervisor") >= 0 or (head_txt.find("Organization") >= 0 and head_txt.find("Supervisor") >= 0):
                       if not Found_org:  # if the abstract has not been found yet
                          print "Organization and Supervisor (en): found"
                          output_blocks_on_page(page_node, block_number, page, OrgandSup_path, 0)
                          Found_org = True

             if head_txt.find("Keywords") >= 0 or head_txt.find("Keyword") >= 0:
                 print "I should be herer!!!!!"
                 if not Found_key:  # if the abstract has not been found yet
                          print "Keywords(en): found"
                          output_blocks_on_page(page_node, block_number, page, key_path, 0)
                          Found_key = True



                # model for thesis
            if head_txt.find("Abstract") >= 0 or head_txt.find("ABSTRACT") >= 0:
                if not Found_abstract: #if the abstract has not been found yet
                    print "Abstract (en): found"
                    output_blocks_on_page(page_node, block_number, page,abstractOut_path,0)
                    Found_abstract = True
                break

            if head_txt.find("Sammanfattning") >= 0 or head_txt.find("SAMMANFATTNING") >= 0:
                if not Found_Sammanfattning:
                    print "Sammanfattning (sv): found"
                    output_blocks_on_page(page_node, block_number, page,abstractOut_path,0)
                    Found_Sammanfattning = True
                break

            if head_txt.find("Abstrakt") >= 0 or head_txt.find("ABSTRAKT") >= 0:
                if not Found_Sammanfattning:
                    print "Abstrakt (sv): found"
                    output_blocks_on_page(page_node, block_number, page,abstractOut_path,0)
                    Found_Sammanfattning = True
                break

            if head_txt.find("Referat") >= 0 or head_txt.find("REFERAT") >= 0:
                if not Found_Sammanfattning:
                    print "Referat (sv): found"
                    output_blocks_on_page(page_node, block_number, page,referat_path,0)
                    Found_Sammanfattning = True
                break
                 #table of content
            if head_txt.find("Table of Contents") >= 0 or head_txt.find("Contents") >= 0:
                    if not Found_TOC:  # if the abstract has not been found yet
                        print "TOC (en): found"
                        output_blocks_on_page(page_node, block_number, page, toc_path,0)
                        Found_TOC = True
                    break



            if head_txt.find("Introduction") >= 0 or head_txt.find("INTRODUCTION") >= 0:
                    if not Found_Introduction:  # if the abstract has not been found yet
                        print "Introduction (en): found"
                        output_blocks_on_page(page_node, block_number, page, introductionOut_path, 1)
                        Found_Introduction = True


                        #Found_Introduction = True
                    break


            if head_txt.find("Methods") >= 0 or head_txt.find("METHODS") >= 0 or head_txt.find("Methodology") >= 0 or head_txt.find("METHODOLOGY") >= 0:
                if not Found_Method: #if the abstract has not been found yet
                    print "Methods (en): found"
                    output_blocks_on_page(page_node, block_number, page,methodOut_path, 0)
                    Found_Method = True
                break

#
#            if head_txt.find("Abstracto(sp)") >= 0:
#                    print "Abstracto (sp):"
#                    output_blocks_on_page(page_node, block_number, page)
#                break
#
#            if head_txt.find("Abstrait (fr)") >= 0:
#                    print "Abstrait (fr):"
#                    output_blocks_on_page(page_node, block_number, page)
#                break

            if block_node == title_node and titleonly:
                stop = True
                break
            elif block_node == auth_node and authonly:
                stop = True
                break
        if stop:
            break
    with open(heading_path, 'w') as f:
        for txt in head_txts:#print all append text
            #sys.stdout.writelines([txt, '\n'])
            #reference https://stackoverflow.com/questions/7152762/how-to-redirect-print-output-to-a-file-using-python
            print >> f, txt, "\n"  # print tag information to certain file

def main(argv=None):
    global Found_abstract
    global Found_Sammanfattning
    global automatic_rerunning
    global Found_Introduction
    global directiory

    if argv is None:
#argv=flag
        argv = sys.argv[1:]

    try:
        try:
#opts pdf address
            opts, args = getopt.getopt(argv, "ht", ["help", "test", "noxml", "highlight", "title", "author", "verbose", "caps"])
        except getopt.error as msg:
            raise UsageError(msg)
        for o, a in opts:
            if (o in ['-h', '--help']):
                # print help and exit
                sys.stdout.write(__doc__)
                sys.stdout.flush()
                return 0
            #pdf2heads has ability to update:
            #global automatic_rerunning
            #global Found_abstract
            #global Found_Sammanfattning


       # print args[0]


        #download module(expierment - might migarte into cavnas module later)
        #reference: http://www.pythonforbeginners.com/python-on-the-web/how-to-use-urllib2-in-python/
        file = urllib2.urlopen(urllib2.Request(args[0])).geturl()
        #r = requests.get(args[0], allow_redirects=True)
        print (file)


        pdffile='analyze.pdf'

        output = open(pdffile, 'wb')

        output.write(file.read())

        output.close()

        directiory=args[2].split(".")[0]


        if not os.path.exists('../../../../output/parse_result/'+directiory):
            os.makedirs('../../../../output/parse_result/'+directiory)

        pdf2heads(opts, [pdffile],args[1])

        #if not Found_abstract:
         #   print "Automatically running the program again with the option --caps"
          #  automatic_rerunning=True
          #  pdf2heads(opts, [args[0]],args[1])


    except UsageError as err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2
    except ConfigError, err:
        sys.stderr.writelines([str(err.msg),'\n'])
        sys.stderr.flush()
        return 1

if __name__ == '__main__':        
    sys.exit(main())
