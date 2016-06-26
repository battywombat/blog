#!/usr/bin/env python3
import datetime
import sqlite3
import os
from functools import wraps

from flask import Flask, g, redirect, url_for, current_app, session

from werkzeug.routing import BaseConverter, ValidationError
from werkzeug.security import generate_password_hash
import jinja2
import markdown as md

app = Flask(__name__)


app.config.from_pyfile('config.py')


def connect_db():
    return sqlite3.connect(app.config['SQLITE_DB_FILE'])


@app.before_request
def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()


@app.teardown_appcontext
def close_db(error):
    if error:
        print(error)
        return
    if hasattr(g, 'db'):
        g.db.close()
        del g.db


def pass_hash(password: str):
    return generate_password_hash(password, salt_length=100,
                                  method='pbkdf2:sha1:200000')


app.secret_key = os.urandom(24)
app.permanent_session_lifetime = datetime.timedelta(**app.config[
                                                    'SESSION_TIMEOUT'])


with app.app_context():
    if app.config['DEBUG']:
        print('darn you!')
        db = connect_db()
        cursor = db.cursor()
        schema = open('schema.sql', 'r').read()
        cursor.executescript(schema)
        cursor.executescript(open('test.sql', 'r').read())
        cursor.close()
        db.commit()


def date_format(date):
    '''
    Given a date string in datetime.datetime format, convert it into something
    more human readable
    '''
    try:
        time = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    except TypeError:
        return 'unknown time'
    return time.strftime(current_app.config['TIME_FORMAT'])


def markdown(text):
    return md.markdown(jinja2.escape(text))

app.jinja_env.filters['date'] = date_format
app.jinja_env.filters['markdown'] = markdown


def require_login(func):
    @wraps(func)
    def login_wrapper(*args, **kwargs):
        if 'username' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return login_wrapper


class DateConverter(BaseConverter):

    def to_python(self, value):
        values = value.split('-')
        try:
            return datetime.date(*[int(x) for x in values])
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        return '{}-{}-{}'.format(value.year, value.month, value.day)


class TitleConverter(BaseConverter):

    def to_python(self, value):
        return value.replace('-', ' ')

    def to_url(self, value):
        return value.replace(' ', '-')

app.url_map.converters['title'] = TitleConverter
app.url_map.converters['date'] = DateConverter
