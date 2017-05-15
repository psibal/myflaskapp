from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from datetime import datetime
#from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#Config postgresql
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/myflaskapp'

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Users (db.Model):
    __tablename__ = "users"
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Unicode)
    email = db.Column('email', db.Unicode)
    username = db.Column('username', db.Unicode)
    password = db.Column('password', db.Unicode)
    register_date = db.Column('register_date', db.Date)

class Articles (db.Model):
    __tablename__ = "articles"
    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('title', db.Unicode)
    author = db.Column('author', db.Unicode)
    body = db.Column('body', db.Unicode)
    create_date = db.Column('create_date', db.Date)


#Articles = Articles()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Passwords do not match")
    ])
    confirm =PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = Users(name=form.name.data,
                    email=form.email.data,
                    username=form.username.data,
                    password=sha256_crypt.encrypt(str(form.password.data)))
        db.session.add(user)
        db.session.commit()
        flash('You are now registered and can login.','success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #db query
        user = Users.query.filter_by(username=username).first()
        if user:
            if sha256_crypt.verify(password_candidate,user.password):
                app.logger.info('PASSWORD MATCHED')
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                app.logger.info('PASSWORD NOT MATCHED')
                error = 'Invalid Login'
                return render_template('login.html', error=error)

        else:
            app.logger.info('NO USER')
            error = 'Username not found'
            return render_template('login.html', error=error)


    return render_template('login.html')

#check if user logged in - this is a decorator
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    #get Articles
    articles = Articles.query.all()
    if articles:
        return render_template('dashboard.html', articles = articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg = msg)


class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

#Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        article = Articles(title = form.title.data,
                    body = form.body.data,
                    author = session['username'],
                    create_date = datetime.now())
        db.session.add(article)
        db.session.commit()
        flash('Article Created.','success')
        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
