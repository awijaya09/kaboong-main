import hmac
import os
import hashlib
import time
from urlparse import urlparse, urljoin
from flask import request, url_for, render_template, redirect
from flask_login import login_user

from sqlalchemy import create_engine, asc
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Post, Ads, Family, Comment
engine = create_engine('mysql://obitsy:kiasu123@localhost/obitsy_db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
dbsession = DBSession()

file = open('static/secret.txt', 'r')
SECRET = file.read()

def hash_str(s):
    return hmac.new(SECRET, s, digestmod=hashlib.sha256).hexdigest()

def get_date():
    return time.strftime("%d %b %Y")

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_all_posts():
    return dbsession.query(Post).all()

def process_login(email, password, remember):
        if email and password:
            user = validate_email(email)
            print "User received ? %s" %user.id
            if user:
                if check_password_valid(user, password):
                    proceed_to_login(user, remember)
                    return redirect(url_for('main'))
                else:
                    return show_error("Invalid username/password", 'login.html')
            else:
                return show_error('Please register before logging in!', 'login.html')

        else:
            return show_error('Please fill in both email & password!', 'login.html')

def register_user(name, email, password):
        error = ""
        checkUser = validate_email(email)

        if checkUser:
            error = "Email has been used, please use other email"
            return render_template('register.html',email=email, name=name, alert=render_template('alert.html', errormsg=error))
        else:
            try:
                create_user(name, email, password)
                #once user created, log them in directly
                created_user = validate_email(email)
                proceed_to_login(created_user, True)
                return redirect(url_for('main'))
            except:
                dbsession.rollback()
                return redirect(url_for('createUser'))

#Helper method to show error using alert.html
def show_error(error_string, template_name):
    return render_template(template_name, alert=render_template('alert.html', errormsg=error_string))

#Checking if user exists, returns user object or None
def validate_email(email):
    dbsession.commit()
    user = dbsession.query(User).filter_by(email=email).first()
    return user

#Create new user and commit to database
def create_user(name, email, password):
    hPass = hash_str(password)
    todayDate = get_date()
    user = User(name=name, email=email, password=hPass, member_since=todayDate)
    dbsession.add(user)
    dbsession.commit()

#Checking if hashed password is the same like the password
def check_password_valid(user, password):
    hPass = hash_str(password)
    return user.password == hPass

#Login user with remember param
def proceed_to_login(user, remember):
    if remember is not None:
        login_user(user, remember=True)
    else:
        login_user(user, remember=False)
