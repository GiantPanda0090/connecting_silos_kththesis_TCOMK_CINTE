#!/usr/bin/python

import os
import io
from django.template import loader



def retrive_session_baseon_id(session_id):
    template_2 = loader.get_template('polls/done_thesis.html')
    abstract_autofill = ""
    title_autofill = ""
    author_autofill = ""
    contact_autofill = ""
    manager_autofill = ""
    toc_autofill = ""
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

    # append output result to front end
    os.chdir(ROOT_DIR + "/../output/parse_result")
    output_str_toweb=""
    session_folder_list = os.walk('.')
    # go into each output result session
    for path,folders,file in session_folder_list:
            for dir in folders:
              if dir != "cache" and dir !="log.txt":
                folder_strutre = str(dir).split("_")
                if session_id==folder_strutre[3]:

                    os.chdir(os.getcwd() + "/" + dir)
                    output_str_toweb = output_str_toweb + "\n\n" + "Session: " + dir + ":\n"
                    # go into each output result
                    for root, dirs, files in os.walk("."):  # per file
                        current_author_group = []
                        for filename in files:
                            if filename != "heading.txt" and filename != "log.txt":  # filename filter
                                output = io.open(os.getcwd() + "/" + filename, 'r', encoding="utf-8")
                                content = output.read()
                                list = content.split(">")
                                content = list[1]
                                list = content.split("<")
                                content = list[0]
                                if filename == "abstract(en).txt" or filename == "abstract(sv).txt":
                                    if (len(abstract_autofill)):
                                        abstract_autofill = abstract_autofill + "\n" + content
                                    else:
                                        abstract_autofill = content
                                if filename == "title.txt":
                                    title_autofill = content
                                if filename == "author_1.txt" or filename == "author_2.txt":
                                    if len(author_autofill):
                                        author_autofill = author_autofill + ";\n " + content
                                    else:
                                        author_autofill = content

                                if filename == "author_email_1.txt" or filename == "author_email_2.txt":
                                    if len(contact_autofill):
                                        contact_autofill = contact_autofill + "; \n" + content
                                    else:
                                        contact_autofill = content

                                if filename == "Examiner.txt" or filename == "Supervisor.txt":
                                    if len(manager_autofill):
                                        manager_autofill = manager_autofill + "; " + content
                                    else:
                                        manager_autofill = content
                                if filename == "toc(en).txt":
                                    toc_autofill = content
                                # append result for front end
                                output_str_toweb = output_str_toweb + "\n" + filename + "\n" + content
                                output.close()
                        os.chdir("../")
                        output_str_toweb = output_str_toweb + "END OF SESSION" + \
                                           "\n\n"
    # back to root
    os.chdir(ROOT_DIR)
    # send data to front end

    context = {
       'Output': output_str_toweb,
       'Body': abstract_autofill,
       'Lecturer': author_autofill,
       'Heading': title_autofill,
       "Contact": contact_autofill,
       "Manager": manager_autofill,
       "TOC": toc_autofill,
       "Session_list": session_folder_list

        }
    return HttpResponse(template_2.render(context, request))
