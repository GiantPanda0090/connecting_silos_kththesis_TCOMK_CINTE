# Connecting_Silos_KTHthesis_TCOMK_CINTE
 Automation System for Thesis Processing in Canvas and Diva<br /><br />
 KTH CINTE and TCOMK Thesis Project 2018 4th Semester<br />
 
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
 Process Module: src/parse/kth_extract/pdfssa4met<br />
 Canvas RestAPI Operation: src/Canvas<br />
 DiVA Operation: src/Diva<br />
 Output Data: output<br />
 Unesed Libraries:library<br />
 
 Project Managment Tool: Atlassian Jira Cloud<br />

 Install project requisition:<br />
 run './install_requisition.sh'<br />
 project is using python pip3,pip,conda,selenium, lxml and geckodriver for firefox<br />
 
 General start up:<br />
 run 'source src/add_path.sh' during first run or add 'export PATH=$PATH:<src path>/../ffdriver' into .bashrc/.cshrc file under home directory<br />
 ./src/start.py <course_id> <assignment_id> <KTH_username> <KTH_password> <document_type> <br />
 
 Process unit usage: <br />
 ./run.sh <pdf_document> <document_type> <student_name> <br />
 Thesis: document_type = 0<br />
 Proporsal: document_type = 1<br />
 
 
 
 Project is currently in progress...........
