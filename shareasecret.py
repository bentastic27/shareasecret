from flask import Flask, g, render_template, flash, get_flashed_messages, redirect, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.wtf import Form
from wtforms import TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_bootstrap import Bootstrap
import sqlite3
from random import choice
from string import ascii_lowercase, digits
from time import time
from os.path import realpath, dirname
from os import chdir
from base64 import b64encode, b64decode

# changing dir to script directory
chdir(dirname(realpath(__file__)))

app = Flask(__name__)
Bootstrap(app)

# secret key
app.config['SECRET_KEY'] = 'CHANGE ME CHANGE ME CHANGE ME'

# sqlite db path
app.config['DATABASE'] = dirname(realpath(__file__)) + '/secret.db'


# form/class for creating the secret
class SecretForm(Form):
    secret_text = TextAreaField("Your secret", validators=[DataRequired()])
    password = PasswordField("Optional password", validators=[Optional()])
    submit = SubmitField("Submit")


# class/form for authenticating if pass protected
class AuthForm(Form):
    password = PasswordField("Secret password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# func for random string
def random_string():
    return ''.join(choice(ascii_lowercase + digits) for i in range(80))


# connect to db
def connect_db():
    g.db = sqlite3.connect(app.config['DATABASE'])


# close the db connection at the end of the every request
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# 404 pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# main page
@app.route('/', methods=['POST', 'GET'])
def index():
    form = SecretForm()

    # if form was submitted and validated
    if form.validate_on_submit():

        # setting or flashing for secret content
        if form.secret_text.data == '':
            secret_content = None
            flash("Missing your secret")
        else:
            secret_content = b64encode(form.secret_text.data)

        # setting or None'ing password
        if form.password.data == '':  # if no password
            secret_password_hash = None
        else:  # else set password hash
            secret_password_hash = generate_password_hash(form.password.data)

        # if no errors proceed
        if not get_flashed_messages():
            secret_id = random_string()
            secret_key = random_string()
            connect_db()
            g.db.execute("INSERT INTO secrets (id, timestamp, content, password, access_key) VALUES (?, ?, ?, ?, ?)",
                         [
                             secret_id,
                             time(),
                             secret_content,
                             secret_password_hash,
                             secret_key
                         ])
            g.db.commit()
            return redirect("/confirmation/" + secret_id + "/")

    return render_template('index.html', form=form)


@app.route('/confirmation/')
@app.route('/confirmation/<secret_id>/')
def confirmation_page(secret_id=None):
    if secret_id is None:
        return redirect('/')
    return render_template('confirm.html', secret_id=secret_id, url=request.url_root)


@app.route('/secret/')
@app.route('/secret/<secret_id>', methods=['POST', 'GET'])
def secret_page(secret_id=None):
    if secret_id is None:
        return redirect('/')

    # connect to and get the row
    connect_db()
    row = g.db.execute("SELECT content, password, access_key FROM secrets WHERE id=?",
                    [secret_id]).fetchone()

    if row is not None:  # if query yielded results, assign vars
        secret_content = row[0]
        secret_password_hash = row[1]
        access_key = row[2]
    else:  # no results (turn into a 404 w/ redirect)
        return render_template('404.html'), 404

    # if there was a password set in the db
    if secret_password_hash is not None:
        form = AuthForm()

        # if the auth form was submitted and validated and password hash matches
        if form.validate_on_submit() and \
                check_password_hash(secret_password_hash, form.password.data):
            # set access key as a cookie
            session['access_key'] = access_key
            # redirect to the secret with the access key set
            return redirect("/secret/" + secret_id)

        # if the access key is not set or doesn't match
        elif 'access_key' not in session or session['access_key'] != access_key:
            # render the auth form
            return render_template('auth.html', form=form, secret_id=secret_id)

    # once the authed and secret accessed, delete the secret
    g.db.execute("DELETE FROM secrets WHERE id=?", [secret_id])
    g.db.commit()

    # render the secret page
    return render_template('secret.html', secret_content=b64decode(secret_content))

# running the app
if __name__ == '__main__':  # for cli (NOT PRODUCTION)
    app.run(debug=True, host="0.0.0.0")
else:  # for wsgi
    application = app
