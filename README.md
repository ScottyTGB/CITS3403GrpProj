# CITS3403 Group Project

## Temporary criteria to avoid going to LMS (To be deleted)

1. a description of the purpose of the application, explaining the its design and use.
2. a  table with with each row containing the i) UWA ID ii) name and iii) Github user name of the group members.
3. a brief summary of the architecture of the application.
4. instructions for how to launch the application.
5. instructions for how to run the tests for the application.


Login - Check against, Engage session
Logout - Lose session
Sign up - Check for already existing, check for email regex, hash password, save (units and such), (begin login) LOGINID

Create request - Check for already existing, save student details + unit in table, primray key being requestID (empty tutor)
Answer request - Send RequestID, UPDATE requestID, 

Load requests - Hit databse check for lack of tutor, display all where tutor = null

tutor signs up lists their units they have done
Student signs up as a student

Student posts request
Tutor accepts

tables are 
units 
student
tutor
tutoring



tutor signs up with a list of units
students can select a unit to be taught 

Computer science units only 
computute

Searchbar units when first enter 
