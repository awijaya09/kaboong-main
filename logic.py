# Serves as the controller to the model and database

import hmac
import os
import hashlib
import time
import datetime
from urlparse import urlparse, urljoin
from flask import request, url_for, render_template, redirect, jsonify
from flask_login import login_user

from sqlalchemy import create_engine, asc
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Post, Ads, Family, Comment, City
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


def getAllPosts():
    posts = dbsession.query(Post).all()
    return jsonify(Posts=[i.serialize for i in posts])


def getPostJson(post_id):
    post = get_post_byID(post_id)
    return jsonify(Post= post.serialize)


def get_post_byID(post_id):
    return dbsession.query(Post).filter_by(id=post_id).one()


def get_post_by_user(user):
    posts = dbsession.query(Post).filter_by(user=user).all()
    return posts


def get_user(user_id):
    dbsession.rollback()
    user = dbsession.query(User).get(int(user_id))
    return user


def get_user_from_email(email):
    user = dbsession.query(User).get(email)
    return user


def create_city(city):
    newCity = City(name=city)
    dbsession.add(newCity)
    dbsession.commit()
    return newCity


def check_city(city):
    find_city = dbsession.query(City).filter_by(name=city).one()

    if find_city:
        print "City found: %s" % find_city
        return find_city

    else:
        newCity = create_city(city)
        return newCity


def create_new_post(name, age, tod, resting_at, burried_at, burried_date, picture, obituary, user, city):
    todayDate = datetime.date.today()
    formattedDate = todayDate.strftime('%d-%b-%Y')
    cur_user = get_user(user.id)
    newPost = Post(date_created=formattedDate, d_name=name, d_age=age, d_tod=tod,
                    d_resting_at=resting_at,
                    d_burried_at=burried_at,
                    d_burried_date=burried_date,
                    picture=picture,
                    obituary=obituary,
                    user=cur_user,
                    city=city)
    dbsession.add(newPost)
    dbsession.commit()
    return newPost


def update_post(post_id, name, age, tod, resting_at, burried_at, burried_date, picture, obituary, user, city):
    post = get_post_byID(post_id)
    post.d_name = name
    post.d_age = age
    post.d_tod = tod
    post.d_resting_at = resting_at
    post.d_burried_date = burried_date
    post.d_burried_at = burried_at
    post.picture = picture
    post.obituary = obituary
    post.city = city
    dbsession.commit()
    return post


def delete_post(post_id):
    post = get_post_byID(post_id)
    dbsession.commit()
    dbsession.delete(post)
    dbsession.commit()


def process_login(email, password, remember):
        if email and password:
            user = validate_email(email)
            print "User received ? %s" % user.id
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
            return render_template('register.html', email=email, name=name, alert=render_template('alert.html', errormsg=error))
        else:
            try:
                create_user(name, email, password)
                # Once user created, log them in directly
                created_user = validate_email(email)
                proceed_to_login(created_user, True)
                return redirect(url_for('main'))
            except:
                dbsession.rollback()
                return redirect(url_for('createUser'))


# Helper method to show error using alert.html
def show_error(error_string, template_name):
    return render_template(template_name, alert=render_template('alert.html', errormsg=error_string))


# Checking if user exists, returns user object or None
def validate_email(email):
    dbsession.commit()
    user = dbsession.query(User).filter_by(email=email).first()
    return user


# Create new user and commit to database
def create_user(name, email, password):
    hPass = hash_str(password)
    todayDate = get_date()
    user = User(name=name, email=email, password=hPass, member_since=todayDate)
    dbsession.add(user)
    dbsession.commit()


# Checking if hashed password is the same like the password
def check_password_valid(user, password):
    hPass = hash_str(password)
    return user.password == hPass


# Login user with remember param
def proceed_to_login(user, remember):
    if remember is not None:
        login_user(user, remember=True)
    else:
        login_user(user, remember=False)
