#!/usr/bin/env python3
import datetime
import sqlite3

from flask import (render_template, g, request, current_app, session, url_for,
                   redirect)

from werkzeug.security import check_password_hash

from blog.blog import app, require_login


@app.errorhandler(404)
def not_found():
    return render_template('404_not_found.html'), 404


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        cursor = g.db.cursor()
        cursor.execute('SELECT * FROM posts ORDER BY edit_date ASC LIMIT ?',
                       (current_app.config['MAX_POSTS'],))
        posts = [{
            'id': post[0],
            'title': post[1],
            'body': post[2],
            'date': post[3]
        } for post in cursor.fetchall()]
        return render_template('index.html', posts=posts)
    else:
        query = request.form['value']
        cursor = g.db.cursor()
        cursor.execute("SELECT id FROM tags WHERE tag LIKE ?", 
                       ('%{}%'.format(query),))
        tags = [t[0] for t in cursor.fetchall()]
        rows = []
        for tag in tags:
            cursor.execute('SELECT id, title, body, post_date FROM post_tag '
                           'JOIN posts ON posts.id=post_tag.post_id '
                           'WHERE tag_id=?',
                           (str(tag),))
            rows += cursor.fetchall()
        like_query = '%{}%'.format(query)
        cursor.execute('SELECT * FROM posts WHERE title LIKE ? OR body LIKE ?',
                       (like_query, like_query))
        rows += cursor.fetchall()
        posts = [{
            'id': post[0],
            'title': post[1],
            'body': post[2],
            'date': post[3]
        } for post in rows]
        return render_template('post_list.html', posts=posts)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        curs = g.db.cursor()
        curs.execute("SELECT * FROM users WHERE username=?", (username,))
        row = curs.fetchone()
        if row:
            if check_password_hash(row[1], password):
                session['username'] = username
                return url_for('new_post')
            else:
                return "Incorrect Password", 400
        else:
            return "We couldn't find your user!", 400


@app.route('/write', methods=['GET', 'POST'])
@require_login
def new_post():
    print(session)
    if request.method == 'GET':
        return render_template('write.html')
    else:
        title = request.form['title']
        body = request.form['body']
        now = datetime.datetime.now()
        cursor = g.db.cursor()
        cursor.execute(
                    'INSERT INTO posts(title, body, post_date, edit_date)'
                    'VALUES(?,?,?,?)', (title, body, now, now))
        g.db.commit()
        return redirect(url_for('read_post', date=now.date(), title=title,
                        id=cursor.lastrowid))


@app.route("/write/<int:post_id>")
@require_login
def edit(post_id):
    try:
        post = g.db.cursor().execute('SELECT * FROM posts WHERE id=:id',
                                     (post_id,)).fetchone()
    except sqlite3.OperationalError:
        return 'The post could not be found', 404

    return render_template('write.html', post_id=post[0], post_title=post[1],
                           post_body=post[2])


@app.route('/read?<int:id>', defaults={'date': None, 'title': None})
@app.route('/read/<int:id>/<title:title>', defaults={'date': None})
@app.route('/read/<int:id>/<title:title>/<date:date>')
def read_post(id, title, date):
    cursor = g.db.cursor()
    posts = cursor.execute('SELECT * FROM posts WHERE id = ?', (id,))
    post = posts.fetchone()
    if post:
        real_title = post[1]
        real_date = datetime.datetime.strptime(post[3],
                                               "%Y-%m-%d %H:%M:%S.%f").date()
        if title == real_title and date == real_date:
            return render_template('read.html', title=post[1], body=post[2],
                                   date=post[3])
        else:
            # make sure there's no incorrect information in the URL
            return redirect(url_for('read_post', id=id, title=real_title,
                                    date=real_date))
    else:
        return render_template('404_not_found.html'), 404
