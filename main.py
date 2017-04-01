from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, abort, session, get_flashed_messages
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from logic import SECRET, is_safe_url, process_login, register_user, show_error, get_all_posts
import random, string
from sqlalchemy import create_engine, asc
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Post, Ads, Family, Comment

app = Flask(__name__)
app.secret_key = 'kiasu_secret'
#Connecting engine to local MySQL database named obitsy_db
engine = create_engine('mysql://obitsy:Kiasu123@localhost/obitsy_db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
dbsession = DBSession()
#securing registration

#initializing flask app and login manager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/logout')
@login_required
def logout():
    successmsg = "You have succesfully logged out!"
    flash(render_template('success.html', successmsg=successmsg))
    logout_user()
    return redirect(url_for('main'))

#Routes to homepage
@app.route('/')
def main():
    posts = get_all_posts()
    print "Current user is authenticated: %s" % current_user.is_authenticated
    print "Current user is Anonymous: %s" % current_user.is_anonymous
    return render_template('home.html', posts=posts)

#Route to About us page
@app.route('/about-us')
def aboutUs():
    return render_template('about-us.html')

#Route to Contact Us page
@app.route('/contact')
def contactUs():
    return render_template('contact-us.html')

#Routes to login user
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')
        return process_login(email, password, remember)

    else:
        if get_flashed_messages():
            successmsg = get_flashed_messages()[0]
            return render_template('login.html', alert=render_template('success.html', successmsg=successmsg))
        else:
             return render_template('login.html')

#Routes to register a new user
@app.route('/register', methods=['GET', 'POST'])
def createUser():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirmpswd = request.form['confirmpswd']
        error = ""

        if name and email and password and confirmpswd:
            if confirmpswd != password:
                error = "Verify Password is not the same as Password!"
                return render_template('register.html', name=name, email=email, alert=render_template('alert.html', errormsg=error))
            else:
                return register_user(name, email, password)
        else:
            return show_error('Please fill in all fields!', 'register.html')
    else:
        return render_template('register.html')

#user profile page, accessible for logged in user only
@app.route('/user/<int:user_id>')
@login_required
def userProfile(user_id):
        user = dbsession.query(User).filter_by(id=user_id).first()
        if current_user.id == user.id:
            posts = dbsession.query(Post).filter_by(user=user).all()
            return render_template('user-profile.html', user=user, posts=posts)
        else:
            successmsg = "Sorry, you are not authorized to open other's profile"
            flash(render_template('success.html', successmsg=successmsg))
            return redirect(url_for('main'))

@app.route('/user/<int:user_id>/edit')
def editUserProfile(user_id):
    return "Edit page for user %s" % user_id

#Route to show how to use the platform
@app.route('/cara-penggunaan')
def howToUse():
    return "How to use the platform"

#Routes to create new post, check, edit & delete a single post
@app.route('/pusat-berita-kematian')
def showAllPosts():
    posts = get_all_posts()
    return render_template('post-listing.html', posts=posts)

@app.route('/newpost')
def createNewPost():
    return "Page to create new post"

@app.route('/post/<int:post_id>')
def getSinglePost(post_id):
    return "Single Post Page"

@app.route('/post/<int:post_id>/edit')
def editPost(post_id):
    return "Page to edit Single Post"

@app.route('/post/<int:post_id>/delete')
def deletePost(post_id):
    return "Page to delete post %s" % post_id

#Routes to create ads for any post
@app.route('/post/<int:post_id>/createAds')
def createAds(post_id, user_id):
    return "Create Ads for posts"

@login_manager.user_loader
def load_user(user_id):
    dbsession.rollback()
    user = dbsession.query(User).get(int(user_id))
    return user

if __name__ == '__main__':
    #app.debug = True
    app.run(host = '0.0.0.0')
