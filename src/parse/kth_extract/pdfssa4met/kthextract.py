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


import sys, getopt
from lxml import etree
from utils import UsageError, ConfigError, mean, median
from pdf2xml import pdf2etree

# text to filter out from the output
text_to_filter = {
    'K T H R O Y A L I N S T IT U T E O F T E C H N O L O G Y',
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
def output_blocks_on_page(a_page_node, starting_block, page_number,filename):
    page_txts=[]
    print "output_blocks_on_page = " + str(page_number)
    print "starting_block=" + str(starting_block)

    local_block_number=0
    for block_node in a_page_node.xpath('.//BLOCK'):
        local_block_number=local_block_number+1
        if local_block_number <= starting_block:
            continue
        st = "<p>"
        et = "</p>"
        headers = block_node.xpath(".//TOKEN[@font-size > {0}]".format(9))
        page_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in headers])
        if len(page_txt):
            page_txts.append("{0}{1}{2}".format(st, page_txt, et))#text append
    with open(filename, 'w') as f:
        for txt in page_txts:
            sys.stdout.writelines([txt, '\n'])#print append text #txt is per line
            print >> f,txt, "\n"   # Python 2.x


#scan the PDF file for headers
def pdf2heads(opts, args):
    global Verbose_flag
    xmltag = True
    highlight = False
    titleonly = False
    authonly = False
    Verbose_flag = False
    look_for_all_caps_headings = False
    global automatic_rerunning
    global Found_Heading
    global Found_abstract
    global Found_Sammanfattning
    global Found_Method
    global Found_Introduction
    global abstractOut_path
    global methodOut_path
    global introductionOut_path
    global heading_path



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
    while True:
        try:
            trial_title_node = tree.xpath("//PAGE[{0}]//BLOCK[{1}]".format(page, block))[0]
            if Verbose_flag:
                print "trial_title_node:"
                print trial_title_node

#            title_headers = trial_title_node.xpath(".//TOKEN[@font-size > {0}]".format(23))
# note that the Title is assumed to be 20 points or larger in size
            title_headers = trial_title_node.xpath(".//TOKEN[@font-size > {0}]".format(20))
            if Verbose_flag:
                print "title_headers:"
                print title_headers 
            title_head_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in title_headers])
            if len(title_head_txt):
                print "<Title>" + title_head_txt + "</Title>"
                title_node=trial_title_node
                next_block=block+1
                break
        except IndexError: page+=1
        else: break
        if page > 2:
            # probably not going to find it now
            break
        
    # find subtitle - note that a subtitle is option - start on the 2nd page and second block on the page
    page = 2
    block = 2
    next_block=2
    subtitle_node = None
    while True:
        try:
            trial_subtitle_node  = tree.xpath("//PAGE[{0}]//BLOCK[{1}]".format(page, block))[0]
            if Verbose_flag:
                print "trial_subtitle_node:"
                print trial_subtitle_node

# the Subtitle is assumed to be larger than 19 points
            subtitle_headers = trial_subtitle_node.xpath(".//TOKEN[@font-size > {0}]".format(19))
            if Verbose_flag:
                print "subtitle_headers:"
                print subtitle_headers 

            if len(subtitle_headers) == 0:
                next_block=2
                break
            subtitle_head_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in subtitle_headers])
            if len(subtitle_head_txt):
                subtitle_node=trial_subtitle_node
                print "<Subtitle>" + title_head_txt + "</Subtitle>"
                next_block=3
                break

        except IndexError: block+=1
        else: break
        if block > 4:
            # probably not going to find it now
            break
    
    # find author - on inside cover
    page = 2
    block = next_block
    auth_node = None
    while True:
        try:
            trial_auth_node  = tree.xpath("//PAGE[{0}]//BLOCK[{1}]".format(page, block))[0]
            if Verbose_flag:
                print "trial_auth_node:"
                print trial_auth_node

# the author's name(s) is(are) assumed to be 15 points or larger in size
            auth_headers = trial_auth_node.xpath(".//TOKEN[@font-size > {0}]".format(15))
            if Verbose_flag:
                print "auth_headers:"
                print auth_headers
            auth_head_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in auth_headers])
            if len(title_head_txt):
                auth_node=trial_auth_node
                break

        except IndexError: block+=1
        else: break
        if block > 4:
            # probably not going to find it now
            break
    

    font_sizes = tree.xpath('//TOKEN/@font-size')
    mean_font_size =  mean(font_sizes)
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
    Found_Sammanfattning = False
    Found_Method = False
    Found_Introduction = False
    abstractOut_path = '../../../../output/abstract(en).txt'
    methodOut_path = '../../../../output/method(en).txt'
    introductionOut_path = '../../../../output/introduction(en).txt'
    heading_path = '../../../../output/heading.txt'

    #page node
    for page_node in tree.xpath('//PAGE'):
        page = page+1
        block_number=0
        for block_node in page_node.xpath('.//BLOCK'):
            block_number = block_number+1
            if xmltag:
#specify data mining model

                if block_node == title_node:#found title
                    st = "<title>"
                    et = "</title>"
                if block_node == subtitle_node:#found subtitle
                    st = "<subtitle>"
                    et = "</subtitle>"
                elif block_node == auth_node:#found author
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
                headers = block_node.xpath(".//TOKEN[@font-size > {0} or @bold = 'yes' or @font-color != '{1}']".format(mean_font_size, main_font_color))
            else:
                headers = block_node.xpath(".//TOKEN[@font-size > {0} or @bold = 'yes' or @font-color != '{1}']".format(mean_font_size*1.05, main_font_color))

            head_txt = ' '.join([etree.tostring(el, method='text', encoding="UTF-8") for el in headers])


            if head_txt in text_start_to_exclude:
                start_to_exclude = True
            head_txt=filter_headings(head_txt)

            if len(head_txt) and (not start_to_exclude):
                head_txts.append("{0}{1}{2}".format(st, head_txt, et)) #append st tag_content andet


                #abstract model
            if head_txt.find("Abstract") >= 0 or head_txt.find("ABSTRACT") >= 0:
                if not Found_abstract: #if the abstract has not been found yet
                    print "Abstract (en):"
                    output_blocks_on_page(page_node, block_number, page,abstractOut_path)
                    Found_abstract = True
                break

            if head_txt.find("Sammanfattning") >= 0 or head_txt.find("SAMMANFATTNING") >= 0:
                if not Found_Sammanfattning:
                    print "Sammanfattning (sv):"
                    output_blocks_on_page(page_node, block_number, page,abstractOut_path)
                    Found_Sammanfattning = True
                break

            if head_txt.find("Abstrakt") >= 0 or head_txt.find("ABSTRAKT") >= 0:
                if not Found_Sammanfattning:
                    print "Abstrakt (sv):"
                    output_blocks_on_page(page_node, block_number, page,abstractOut_path)
                    Found_Sammanfattning = True
                break

            if head_txt.find("Referat") >= 0 or head_txt.find("REFERAT") >= 0:
                if not Found_Sammanfattning:
                    print "Referat (sv):"
                    output_blocks_on_page(page_node, block_number, page,abstractOut_path)
                    Found_Sammanfattning = True
                break
            if head_txt.find("Introduction") >= 0 or head_txt.find("INTRODUCTION") >= 0:
                    if not Found_Introduction:  # if the abstract has not been found yet
                        print "Introduction (en):"
                        output_blocks_on_page(page_node, block_number, page, introductionOut_path)
                        Found_Introduction = True
                    break
            if head_txt.find("Methods") >= 0 or head_txt.find("METHODS") >= 0 or head_txt.find("Methodology") >= 0 or head_txt.find("METHODOLOGY") >= 0:
                if not Found_Method: #if the abstract has not been found yet
                    print "Methods (en):"
                    output_blocks_on_page(page_node, block_number, page,methodOut_path)
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
            sys.stdout.writelines([txt, '\n'])
            #reference https://stackoverflow.com/questions/7152762/how-to-redirect-print-output-to-a-file-using-python
            print >> f, txt, "\n"  # print tag information to certain file

def main(argv=None):
    global Found_abstract
    global Found_Sammanfattning
    global automatic_rerunning
    global Found_Introduction

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
        pdf2heads(opts, args)

        if not Found_abstract:
            print "Automatically running the program again with the option --caps"
            automatic_rerunning=True
            pdf2heads(opts, args)


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
