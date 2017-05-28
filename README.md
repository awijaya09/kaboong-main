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
6. sudo pip install oauth2client
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

### How to Use the Platform
```
1. Start Posting by registering or Login
2. You can use Google Account to Register or Login
3. Start Posting by Going to Post Page
4. You can get data of all posts at /getAllPostJson
5. You can also get specific data of any post via /getPostJson/<post_id>
6. You can only access once you are logged in
```

##Authors
* **Andree Wijaya**
