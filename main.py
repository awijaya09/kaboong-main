from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, abort, session, get_flashed_messages
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
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
from logic import hash_str, get_date, is_safe_url
from itsdangerous import URLSafeSerializer
from logic import SECRET

s = URLSafeSerializer(SECRET)

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
    posts = dbsession.query(Post).all()
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
        if email and password:
            try:
                dbsession.rollback()
                user = dbsession.query(User).filter_by(email=email).one()
                if user:
                    hPass = hash_str(password)
                    if user.password == hPass:
                        print "User found, password matched: %s" % user.name
                        login_user(user, remember=True, force=True)
                        print "User is logged in, current user is authenticated: %s" % current_user.is_authenticated

                        return redirect(url_for('main'))
                    else:
                        error = "Invalid username/password"
                        return render_template('login.html', alert=render_template('alert.html', errormsg=error))
                else:
                    error = "Please register before logging in!"
                    return render_template('login.html', alert=render_template('alert.html', errormsg=error))
            except:
                dbsession.rollback()
                error = "Trouble finding your email"
                return render_template('login.html', alert=render_template('alert.html', errormsg=error))
        else:
            error = "Please fill in both email & password"
            return render_template('login.html', alert=render_template('alert.html', errormsg=error))

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
                checkUser = dbsession.query(User).filter(User.email == email).first()

                if checkUser:
                    error = "Email has been used, please use other email"
                    return render_template('register.html',email=email, name=name, alert=render_template('alert.html', errormsg=error))

                #Succesfully registering user
                else:
                    hPass = hash_str(password)
                    todayDate = get_date()
                    user = User(name=name, email=email, password=hPass, member_since=todayDate)
                    try:
                        dbsession.add(user)
                        dbsession.commit()
                        print "Registering user: %s" % user.name
                        flash("Please login to continue!")
                        #once user created, log them in directly
                        user_created = dbsession.query(User).filter_by(email=email).one()

                        print "User is logged in, current user is authenticated: %s" % current_user.is_authenticated
                        print "User is logged in, created user id: %s" % user_created.id
                        print "User is logged in, current user id: %s" % current_user.get_id()
                        login_user(user_created, remember=True)
                        return redirect(url_for('main'))

                    except:
                        dbsession.rollback()
                        return redirect(url_for('createUser'))

        else:
            error = "Please fill in all fields!"
            return render_template('register.html', alert=render_template('alert.html',errormsg=error))
    else:
        return render_template('register.html')

@app.route('/user/<int:user_id>')
def userProfile(user_id):
    if current_user.is_authenticated :
        user = dbsession.query(User).filter_by(id=user_id).first()
        if current_user.id == user.id:

            posts = dbsession.query(Post).filter_by(user=user).all()
            return render_template('user-profile.html', user=user, posts=posts)
        else:
            successmsg = "Sorry, you are not authorized to open other's profile"
            flash(render_template('success.html', successmsg=successmsg))
            return redirect(url_for('main'))
    else:
        return redirect(url_for('main'))

@app.route('/user/<int:user_id>/edit')
def editUserProfile(user_id):
    return "Edit page for user %s" % user_id

#Routes to create new post, check, edit & delete a single post
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
    print "load_user is invoke!"
    print "user_id value %s" % int(user_id)

    print "Trying to get user..."
    dbsession.rollback()
    user = dbsession.query(User).get(int(user_id))
    return user

    #userq = dbsession.execute(text("SELECT user.id AS user_id, user.name AS user_name, user.email AS user_email, user.password AS$, user.is_authenticated FROM user WHERE user.id = :userid LIMIT :param ") , {'userid':userid, 'param':1})
    #user = userq.fetchone()[0]
    #print "User object : %s" % user

if __name__ == '__main__':
    app.run(host = '0.0.0.0')
