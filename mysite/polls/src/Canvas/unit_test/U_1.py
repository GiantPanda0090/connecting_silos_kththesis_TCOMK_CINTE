

#This is the test case for Unit Test U.1
#expected  https://kth.instructure.com/courses/2139/assignments/24565/submissions?zip=1
#course_id 2139(sandbox)
#assignment_id 24565 test_1

#import
import sys
import config
import urllib2


#initialize test enviorment
Expected_kth_canvas= config.kth_canvas
#course_id 2139(sandbox)
Expected_kth_canvas_thesis_course_id = config.thesis_course_id #sandbox
#assignment_id 24565 testing 1; 24566 testing 2 ; 24567 testing 3;
Expcted_proporsal_assignment_id=config.proporsal_assignment_id #test_1
Expected_thesis_assignment_id=config.Thesis_assignment_id #test_2


def main(link,document_type):
    print "Start Test Case U_1"
    #define phase
    global Expected_assignment_id #0 is thesis, 1 is proporsal
    int_document_type = int(document_type)
    if int_document_type == 0:#Thesis
        Expected_assignment_id=Expected_thesis_assignment_id
    elif int_document_type == 1:#proporsal
        Expected_assignment_id=Expcted_proporsal_assignment_id
    else:
        print("Error_report:")
        print("Test Case U.1 Failed")
        print("invalid document_type")
        print("Document type can either be 0 or 1")
        print("Expected input: 0 is thesis, 1 is proporsal")
    Expected_url_formate=Expected_kth_canvas+"courses/"+str(Expected_kth_canvas_thesis_course_id)+"/assignments/"+str(Expected_assignment_id)+"/submissions?zip=1"


    if Expected_url_formate == link:
        print "The link "+ link+" is a Canvas link"

        # make sure canvas server is online and link is available
        print "Trying the get request to the link: "+ link
        r =  urllib2.Request(link)
        res = urllib2.urlopen(r)
        print "Requset return Status code: "+ str(res.getcode())
        if res.getcode()==200:
           print("Test Case U.1 Pass")
        else:
            print("Error_report:")
            print("Test Case U.1 Failed")
            print ("link is not reachable with http response code: " + str(res.getcode()))
    else:
        print("Error_report:")
        print("Test Case U.1 Failed")
        print("Expected: " + Expected_url_formate)
        print ("Actual: "+ link)



if __name__ == '__main__':
        main()



