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
    db = sqlite3.connect(app.config['SQLITE_DB_FILE'])
    return db


@app.before_request
def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()


@app.teardown_appcontext
def close_db(error):
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
        db = connect_db()
        cursor = db.cursor()
        schema = open('schema.sql', 'r').read()
        cursor.executescript(schema)
        cursor.execute('INSERT INTO tags(tag) VALUES(?)', ('politics',))
        cursor.execute('INSERT INTO tags(tag) VALUES(?)', ('coding',))
        tag_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO posts(title, body, post_date, edit_date)"
            " VALUES(?, ?, ?, ?)",
            (
                'FIRST P0ST!',
                "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                datetime.datetime.now(),
                datetime.datetime.now().isoformat()
            )
        )
        values = cursor.execute('SELECT * FROM posts WHERE 1=1').fetchall()[0]
        cursor.execute('INSERT INTO post_tag(tag_id, post_id) VALUES(?,?)', (tag_id, values[0]))
        for x in range(5):
            cursor.execute(
                "INSERT INTO posts(title, body, post_date, edit_date)"
                " VALUES(?, ?, ?, ?)", values[1:])
        cursor.execute("INSERT INTO users VALUES(?,?)", ('pwarner',
                                                         pass_hash('werkzeug')))
        cursor.close()
        db.commit()


def date_format(date):
    '''
    Given a date string in datetime.datetime format, convert it into something
    more human readable
    '''
    time = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
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
            return datetime.date(*map(lambda x: int(x), values))
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
