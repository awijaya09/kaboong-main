from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort, session, get_flashed_messages, send_from_directory
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from logic import SECRET, is_safe_url, process_login,register_user, show_error, get_all_posts, check_city, create_new_post, get_user, get_post_by_user, get_post_byID, delete_post, update_post, getAllPosts, getPostJson, get_user_from_email
import random
import string
import os
import httplib2
import json
import requests

from database_setup import Base, User, Post, Ads, Family, Comment
from werkzeug.utils import secure_filename

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Securing type of file uploaded
UPLOAD_FOLDER = './pictures'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.secret_key = 'kiasu_secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Securing upload
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initializing flask app and login manager

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


# Routes to homepage
@app.route('/')
def main():
    posts = get_all_posts()
    return render_template('home.html', posts=posts)


# Route to About us page
@app.route('/about-us')
def aboutUs():
    return render_template('about-us.html')


# Route to Contact Us page
@app.route('/contact')
def contactUs():
    return render_template('contact-us.html')


# Routes to login user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')
        return process_login(email, password, remember)

    else:
        if get_flashed_messages():
            successmsg = get_flashed_messages()[0]
            return render_template('login.html',
                alert=render_template('success.html', successmsg=successmsg))
        else:
            return render_template('login.html')


# Routes to register a new user
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
                return render_template('register.html',
                                    name=name, email=email,
                                    alert=render_template('alert.html', errormsg=error))
            else:
                return register_user(name, email, password)
        else:
            return show_error('Please fill in all fields!', 'register.html')
    else:
        return render_template('register.html')


# User profile page, accessible for logged in user only
@app.route('/user/<int:user_id>')
@login_required
def userProfile(user_id):
        user = get_user(user_id)
        if user:
            if current_user.id == user.id:
                posts = get_post_by_user(user)
                return render_template('user-profile.html', user=user, posts=posts)
            else:
                successmsg = "Sorry, you are not authorized to open other's profile"
                flash(render_template('success.html', successmsg=successmsg))
                return redirect(url_for('main'))
        else:
            flash(render_template('alert.html',
                                    errormsg="Sorry, no user with that ID!"))
            return redirect(url_for('main'))


@app.route('/user/<int:user_id>/edit')
def editUserProfile(user_id):
    return "Edit page for user %s" % user_id


# Route to show how to use the platform
@app.route('/cara-penggunaan')
def howToUse():
    return "How to use the platform"


# Routes to create new post, check, edit & delete a single post
@app.route('/pusat-berita-kematian')
def showAllPosts():
    posts = get_all_posts()
    return render_template('post-listing.html', posts=posts)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/newpost', methods=['GET', 'POST'])
@login_required
def createNewPost():
    if request.method == 'POST':
        if not current_user.is_anonymous:
            name = request.form['name']
            age = request.form['age']
            tod = request.form['tod']
            rumahduka = request.form['rumahduka']
            tos = request.form['tos']
            semayam = request.form['semayam']
            beritaduka = request.form['obituary']

            # Validating input from user
            city = request.form['city']
            if city:
                curCity = check_city(city)
                print "Files inside request: %s" % request.files
                if 'pict' not in request.files:
                    flash(render_template('alert.html', errormsg="Picture not in request files"))
                    return redirect(request.url)
                else:
                    pict = request.files['pict']
                    if pict.filename == '':
                        flash(render_template('alert.html', errormsg="Please input Picture"))
                        return redirect(request.url)

                    if pict and allowed_file(pict.filename):
                        filename = secure_filename(pict.filename)
                        savedPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        pict.save(savedPath)
                        pict_url = url_for('uploaded_file', filename=filename)
                        print "pict url : %s" % pict_url
                        newPost = create_new_post(name, age,
                                                    tod, rumahduka,
                                                    semayam, tos,
                                                    pict_url, beritaduka,
                                                    current_user,curCity)

                        return redirect('post/%s' % newPost.id)
            # Return an error with explaination if form is wrongly submitted
            else:
                flash(render_template('alert.html', errormsg="Error in getting City"))
                return render_template('new-post.html')
        else:
            flash(render_template('alert.html', errormsg="Please sign in to start posting"))
            return render_template('/')

    else:
        return render_template('new-post.html')


@app.route('/post/<int:post_id>')
def getSinglePost(post_id):
    post = get_post_byID(post_id)
    edit = render_template('edit.html', post_id=post_id)
    delete = render_template('delete.html', post_id=post_id)
    if not current_user.is_anonymous:
        if post.user_id == current_user.id:
            return render_template('detail-post.html',
                                    post=post,
                                    user=current_user,
                                    edit=edit,
                                    delete=delete)
        else:
            return render_template('detail-post.html', post=post)
    else:
        return render_template('detail-post.html', post=post)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def editPost(post_id):
    post = get_post_byID(post_id)
    if request.method == 'POST':
        # Check if the user is currently authorized to edit
        if post.user_id == current_user.id:
            name = request.form['name']
            age = request.form['age']
            tod = request.form['tod']
            rumahduka = request.form['rumahduka']
            tos = request.form['tos']
            semayam = request.form['semayam']
            beritaduka = request.form['obituary']

            # Validating input from user
            city = request.form['city']
            if city:
                curCity = check_city(city)
                print "Files inside request: %s" % request.files
                if 'pict' not in request.files:
                    flash(render_template('alert.html', errormsg="Picture not in request files"))
                    return redirect(request.url)
                else:
                    pict = request.files['pict']
                    if pict.filename == '':
                        flash(render_template('alert.html', errormsg="Please input Picture"))
                        return redirect(request.url)

                    if pict and allowed_file(pict.filename):
                        filename = secure_filename(pict.filename)
                        savedPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        pict.save(savedPath)
                        pict_url = url_for('uploaded_file', filename=filename)
                        print "pict url : %s" % pict_url
                        newPost = update_post(post_id, name,
                                                age, tod,
                                                rumahduka, semayam,
                                                tos, pict_url,
                                                beritaduka,
                                                current_user,curCity)

                        return redirect('post/%s' % newPost.id)
            # Return an error with explaination if form is wrongly submitted
            else:
                flash(render_template('alert.html', errormsg="Error in getting City"))
                return render_template('new-post.html')
        else:
            flash(render_template('alert.html', errormsg="You can't edit the post!"))
            return redirect('/')
    else:
        if post.user_id == current_user.id:
            return render_template('edit-post.html', post=post)
        else:
            flash(render_template('alert.html', errormsg="You can't edit the post!"))
            return redirect('/')


# Routes to delete post by id. Only authenticated user can edit his own post
@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def deletePost(post_id):
    post = get_post_byID(post_id)
    if request.method == 'POST':
        if post.user_id == current_user.id:
            delete_post(post_id)
            flash(render_template('success.html', successmsg="Post successfully deleted!"))
            return redirect('/')
        else:
            flash(render_template('alert.html', errormsg="You can't edit the post!"))
            return redirect('/')
    else:
        if post.user_id == current_user.id:
            return render_template('delete-post.html', post=post)
        else:
            flash(render_template('alert.html',
                                    errormsg="You can't edit the post!"))
            return redirect('/')


@app.route('/oauth/<provider>', methods=['POST'])
def loginGoogle(provider):
    # STEP 1 - Parse the auth code
    print "JSON %s" % request
    auth_code = request.data
    print "Step 1 - Complete, received auth code %s" % auth_code
    if provider == 'google':
        # STEP 2 - Exchange for a token
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('./static/google-api.json',
                                                    scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'),
                                        401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        print "Step 2 Complete! Access Token : %s " % credentials.access_token

        # STEP 3 - Find User or make a new one

        # Get user info
        h = httplib2.Http()
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()
        print data
        name = data['name']
        picture = data['picture']
        email = data['email']
        g_id = data['id']

        # See if user exists, if it doesn't make a new one
        user = get_user_from_email(email)
        if not user:
            register_user(name, email, g_id)

        return process_login(email, g_id, True)


@app.route('/getAllPostJson', methods=['GET', 'POST'])
def getAllPostJson():
    if request.method == 'GET':
        return getAllPosts()
    else:
        redirect('/')


@app.route('/getPostJson/<int:post_id>', methods=['GET', 'POST'])
def getPostWithJson(post_id):
    if request.method == 'GET':
        return getPostJson(post_id)
    else:
        redirect('/')


@login_manager.user_loader
def load_user(user_id):
    user = get_user(user_id)
    return user


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
