DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
  id INTEGER PRIMARY KEY,
  title VARCHAR(80) NOT NULL,
  body TEXT NOT NULL,
  post_date DATETIME NOT NULL,
  edit_date DATETIME NOT NULL
);

DROP TABLE IF EXISTS tags;

CREATE TABLE tags (
  id INTEGER PRIMARY KEY,
  tag VARCHAR(20) NOT NULL
);

DROP TABLE IF EXISTS post_tag;

CREATE TABLE post_tag (
  tag_id INTEGER NOT NULL,
  post_id INTEGER NOT NULL,
  FOREIGN KEY(tag_id) REFERENCES tags(id),
  FOREIGN KEY(post_id) REFERENCES posts(id)
);

DROP TABLE IF EXISTS users;

CREATE TABLE users (
  username VARCHAR(20) PRIMARY KEY,
  password CHAR(160) NOT NULL
);
