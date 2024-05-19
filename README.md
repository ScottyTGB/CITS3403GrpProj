# CITS3403 Group Project

## Description of project

#### The project is a tutoring site for computer science students, allowing students to create tutoring requests as well as accept requests
#### The aim of the site is to connect tutors and students in a centralized place 
#### Pages include open requests, my requests, completed requests, make a request 
#### Users are to register, look for requests they want to tutor in or create a request for a unit they want tutoring in 
#### They can then view the status of their requests taken on or made via the my requests page

## Members

| UwaID | Name | Github |
|---|---|---|
| 23334455 | Tate Meinertz | tmeinertz |
| 23478063 | Minn Khant (Scotty) Maw  | ScottyTGB |
| 23485011 | Runtian Liang | kt006992 |
| 23634774 | Eva Coulter | aviicardo |

## Architecture

#### The site is run using an sqlite database for storage, flask server enables communication between the database and front end as well as loading and handling routes. 
#### The HTML is styled through bootstrap grids and CSS, basic javascript is implemented for smooth transitions
#### Data is loaded into html via flask placeholders which iteratively load data in

## Instructions to run

#### Ensure you are in a virtual environment such as venv or pipenv (Virtual environments are different for everyone, but venv from python >=3.10 will work)
#### Ensure dependencies are installed via pip install -r requirements.txt
#### Create config.env folder in root
#### Fill with SECRET_KEY=<SECRET> (Secure passkey)
#### Start the flask server via python3 app.py
#### To open the dev server, CTRL + Click on one of the IP addresses in your terminal OR go to http://127.0.0.1:4000/

## For testing 

#### Launch the app as normal
#### Go to /testing
#### The app is filled with users and requests both open and accepted
#### Accounts can be accessed view user(1:15)@example.com with password "1"





