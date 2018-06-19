# Connecting_Silos_KTHthesis_TCOMK_CINTE 
 Automation System for Thesis Processing in Canvas and Diva<br /><br />
 KTH CINTE and TCOMK Thesis Project 2018 4th Semester<br />
 
 ![Build Status](https://travis-ci.org/GiantPanda0090/connecting_silos_kththesis_TCOMK_CINTE.svg?branch=master)

 
 Author:<br /> 
 Qi Li, Shiva Besharat Pour<br /><br />
 Examinar:<br />
 Gerald Q. Maguire Jr.<br /><br />
 Academic adviser:<br />
 Anders Västberg<br /><br />
 Examin Insitutution:<br />
 KTH Royal Institute of Technology<br />
 School of Electrical Engineering and Computer Science (EECS))<br />
 Department of Communication Systems<br />
 Stockholm, Sweden<br /><br />
 
 Project Outline:<br />
 Polls is the Connecting Silo application. The Connecting Silo project is build base on Under Professor  Gerald Q. Maguire Jr toolbox. The source code for the toolbox can be found in KTH internal github. application bibutils_6.2_for_DiVA is a tool that can batch convert mods generate from Connecting Silo(folder polls) into bibtex. The application bibutils_6.2_for_DiVA is build base on Professor  Gerald Q. Maguire Jr. from Royal Institute of Technology Sweden [1] <br />
 Polls:<br />
 Name of the module will be changed later.....<br />
 Process Module: src/parse/kth_extract<br />
 Canvas RestAPI Operation: src/Canvas<br />
 DiVA Operation: src/Diva<br />
 KTH API:er : src/KTH<br />
 Output Data: output<br />

 bibutils_6.2_for_DiVA:<br />
 Main class:xml2bib_loop.py<br />
 Rest of the class and method information can be found under professor  Gerald Q. Maguire Jr repositiory: https://github.com/gqmaguirejr/bibutils_6.2_for_DiVA [1] <br />

 Install project requisition:<br />
 run './install_requisition.sh'<br />
 project is using python pip3,pip,conda,selenium, lxml and geckodriver for firefox<br />
 Project is build upon Django framwork<br />
 User need to configure config.json under 'polls/src/Canvas/canvas' and KTHconfig.json under 'polls/src/KTH' for the program to excecute  properly<br />
 Under config.json user need to input oauth token and the address of the Canvas server.<br />
 
 General start up:<br />
 bibutils_6.2_for_DiVA:<br />
 python xml2bib_loop.py 'path of the output folder'<br />
 For this project the 'path of the output folder' is '../polls/output/parse_result'
 Polls:<br />
 The data in the thesis report is partially automated with module: test_accuracy.py <br />

 DiVA location for thesis report:<br />

 



 Note:<br />
 Thesis: document_type = 0<br />
 Proporsal: document_type = 1<br /><br />

 The project intended to serve the KTH - Royal Institute of Technology Sweden Canvas LMS. If user need to implement the program in the Canvas LMS that other Institute deployed, user might need to modify specific setting. The setting that need to modified is unknown.<br />

[1]Jr, Gerald Q. Maguire. Bibutils_6.2_for_DiVA: A Version of Bibutils_6.2 for Use with DiVA. C, 2018. https://github.com/gqmaguirejr/bibutils_6.2_for_DiVA.<br />
 
 
 

