# Kaboong - Online Obituary
The project is to create a simple online obituary portal using Flask, MySQL and SQLAlchemy

## Getting Started
The project requires the following system
- Python 2.7
- MySQL 5.4
- SQLAclhemy
- Flask

### Installing
The project will run on any server Apache or Nginx.
To start using this project, on your server, run:
```
1. sudo apt-get update
2. sudo apt-get install python2.7 python-pip
3. sudo pip install flask
4. sudo pip install SQLAlchemy
5. sudo pip install MySQL-python
```

To install MySQL :
```
sudo apt-get install mysql-server build-dep python-mysqldb
```
- Follow the onscreen instruction to enter the root password
- Then setup new user to create a database:
```
$>mysql --user=root mysql -p
mysql> CREATE USER 'user' IDENTIFIED BY 'password';
mysql> CREATE DATABASE database_name CHARSET UTF8;
mysql> GRANT ALL PRIVILEGES ON database_name.* TO "user"@"localhost" IDENTIFIED BY "password";
mysql> \q
```
Update your database name 
To start the project:
1. Navigate to the project directory and run
```
$>python database_setup.py
$>python testData1.py
```
2. Database and initial input will be inserted into the db
3. Start the project 
```
$>python main.py
```


### Online Version
The project is accessible on my private server : http://188.166.188.203/
##Authors
* **Andree Wijaya**
