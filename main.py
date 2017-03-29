from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, abort, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import random, string
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Post, Ads, Family, Comment

#securing registration
from logic import hash_str, get_date, is_safe_url
from itsdangerous import URLSafeSerializer
from logic import SECRET

s = URLSafeSerializer(SECRET)

#initializing flask app and login manager
app = Flask(__name__)
app.secret_key = 'kiasu_secret'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Connecting engine to local MySQL database named obitsy_db
engine = create_engine('mysql://obitsy:kiasu123@localhost/obitsy_db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
dbsession = DBSession()

@login_manager.user_loader
def load_user(userid):
    user_id = int(userid)
    user = dbsession.query(User).filter_by(id=user_id).first()
    return user

@login_manager.request_loader
def load_user_from_request(request):
    if request.args.get('token'):
        userid = s.loads(token)
        return dbsession.query(User).filter_by(id=userid).first()
    else:
        return None

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
    print "Current user session id %s" % session['user_id']
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
            error = "Invalid email/password!"
            user = dbsession.query(User).filter_by(email=email).first()
            if user:
                hPass = hash_str(password)
                if user.password == hPass:
                    print "User found, password matched: %s" % user.name
                    login_user(user, remember=True)
                    print "User is logged in, current user: %s" % current_user.is_authenticated
                    next = request.args.get('next')
                    if not is_safe_url(next):
                        return abort(400)

                    if next == '/logout':
                        return redirect(url_for('main', token=s.dumps([user.id])))

                    return redirect(url_for('main', token=s.dumps([user.id])))
                else:
                    return render_template('login.html', alert=render_template('alert.html', errormsg=error))
            else:
                return render_template('login.html', alert=render_template('alert.html', errormsg=error))

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

            checkUser = dbsession.query(User).filter_by(email=email).first()

            if checkUser:
                error = "Email has been used, please use other email"
                return render_template('register.html', alert=render_template('alert.html', errormsg=error))

            #Succesfully registering user
            else:
                hPass = hash_str(password)
                todayDate = get_date()
                user = User(name=name, email=email, password=hPass, member_since=todayDate)
                dbsession.add(user)
                dbsession.commit()

                print "Registering user: %s" % user.name
                user_created = dbsession.query(User).filter_by(email=email).one()
                successmsg = "Registration Successful! Welcome to Kaboong..."

                login_user(user_created, remember=True)
                print "User login is invoked!"
                flash(render_template('success.html', successmsg=successmsg))
                return redirect(url_for('main', token=s.dumps([user_created.id])))
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

if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0')
