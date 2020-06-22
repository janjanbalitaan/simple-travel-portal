# simple-travel-portal
#Requirements
1. MySQL
2. Python 3
3. Virtualenv
4. Flask

#APIs
You may access all available APIs for the current version
https://documenter.getpostman.com/view/11713778/Szzoavdp?version=latest

#Default Credentials
1. Employee
user: employee@company.com
pass: p@ssw0rd

2. Manager
user: manager@company.com
pass: p@ssw0rd

3. Finance Manager
user: finance_manager@company.com
pass: p@ssw0rd

#How to Run
1. clone the repository to your environment
2. Create a virtual environment for python 3+
$ virtualenv -p python3 venv
3. Install all the requirements in requirements.txt
$ source venv/bin/activate
$ pip install -r requirements.txt
4. Create a database travel-portal
5. Change the database credentials in the environment variable sample.env
6. Rename sample.env to .env
7. You are ready to run the travel portal
$ source venv/bin/activate
$ python run.py
8. Enjoy using it on your browser by accessing the url: http://127.0.0.1:5000/
