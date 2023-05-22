import sqlite3
import click
import random
from flask import current_app, g

from werkzeug.security import generate_password_hash

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """ Clear the existing data and create new tables """
    init_db()
    click.echo('Initialized the database.')

# generate some random data
@click.command('init-random-db')
def random_db_command():

    init_db()
    # Add three users
    db = get_db()
    users = [
        ('John', generate_password_hash('password1')),
        ('Alice', generate_password_hash('password2')),
        ('Bob', generate_password_hash('password3'))
    ]

    for user in users:
        db.execute("INSERT INTO user (username, password) VALUES (?, ?)", user)

    posts = [
        ('First Post', 'This is the body of the first post.', 1),
        ('Second Post', 'This is the body of the second post.', 2),
        ('Third Post', 'This is the body of the third post.', 3),
        ('Fourth Post', 'This is the body of the fourth post.', 1),
        ('Fifth Post', 'This is the body of the fifth post.', 3)
    ]

    for post in posts:
        db.execute("INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)", post)

    # Add random comments to the posts
    comments = [
        "Great post!", "Nice work!", "I enjoyed reading this.", "Very insightful.", "Well done!"
    ]

    for post_id in range(1, 6):
        for _ in range(random.randint(1, 4)):
            user_id = random.randint(1, 3)
            comment_body = random.choice(comments)
            db.execute("INSERT INTO comment (post_id, user_id, body) VALUES (?, ?, ?)",
                        (post_id, user_id, comment_body))

    # Commit the changes and close the connection
    db.commit()
    click.echo('Random data has been generated in the database.')
    click.echo('seed the database with random data finished.')
    

# Register the command with the application
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(random_db_command)