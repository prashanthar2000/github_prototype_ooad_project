from flask import render_template, url_for, flash, redirect, request
from github import app, db, bcrypt
from github.forms import RegistrationForm, LoginForm
from github.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import os
import subprocess
from werkzeug.utils import secure_filename
import zipfile
import io
import pathlib

@app.route("/")
def index():
    return redirect(url_for('login'))


@app.route("/home")
@login_required
def home():
    repos = list (os.listdir(current_user.username))
    return render_template('home.html', repos=repos , add_repo=True)

@app.route("/add_repo")
@login_required
def add_repo():
    repo_name = request.args.get('repo_name')
    print(os.listdir("./"+current_user.username))
    try:
        os.mkdir("./"+current_user.username + "/" + repo_name)
        os.system("cd ./" + current_user.username + "/" + repo_name +"; git init")
    except Exception  as e:
        print(e)
        # return e
    return render_template("home.html" , add_repo=True)
    # return render_template('add_repo')
    # return True

@app.route("/repo")
@login_required
def repo_files():
    repo_name = request.args.get('repo_name')
    files = os.listdir("./"+current_user.username + "/" + repo_name)
    print(sorted(files))
    files = sorted(files)
    return render_template("repo_files.html" , files=files , repo_files_page=True, repo_name=repo_name )
    
@app.route("/files")
@login_required
def get_files():
    repo_name = request.args.get('repo_name')
    file_name = request.args.get('file_name')
    print(repo_name , file_name )
    try:
        f  = open( current_user.username + "/" + repo_name + "/" + file_name)
        content = f.read()
        f.close()
        return str(content) 

    except Exception as e:
        print(e)
    flash('server error', 'danger')
    return redirect(url_for('home'))

@app.route("/download")
@login_required
def download():
    repo_name = request.args.get('repo_name')
    filename = current_user.username + "/" + repo_name +"/"
    base_path = pathlib.Path(filename)
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            z.write(f_name)
    data.seek(0)
    return flask.send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename=repo_name+".zip"
    )


@app.route('/upload')
@login_required
def upload():
    repo_name = request.args.get("repo_name")
    return render_template('upload.html' , repo_name=repo_name)
	
@app.route('/uploader', methods = ['GET', 'POST'])
@login_required
def upload_file():
    
    if request.method == 'POST':
        repo_name = request.form.get('repo_name')    
        f = request.files['file']
        filename = current_user.username + "/" + repo_name +"/" +  f.filename
        f.save(filename)
        return 'file uploaded successfully'

import random
import string
def generate_random_string(N):
    res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = N))
    return res

@app.route("/commit")
@login_required
def commit():
    repo_name = request.args.get('repo_name')
    commit_message = generate_random_string(64)
    cmd = "cd " + current_user.username + "/" + repo_name +"; git add . ; git commit -m " + commit_message 
    print(cmd)
    os.system(cmd)
    flash('changes has been commited', 'success')
    return redirect(url_for('home'))

#shows only latest change history
@app.route("/commit_history")
@login_required
def commit_histroy():
    repo_name = request.args.get('repo_name')
    cmd = "cd " + current_user.username + "/" + repo_name +"; git show" 
    temp = subprocess.check_output(cmd , shell=True)
    temp = str(temp).split("\\n")[::-1]
    result = []
    for i in temp:
        if i == "":
            break
        result.append(i) 
    
    return '<br>'.join(result[::-1])


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # os.system("mkdir " + form.username.data)
        os.mkdir(form.username.data)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')
