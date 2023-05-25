import markdown

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    session,
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)


# Index/Home route
@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()

    return render_template("blog/index.html", posts=posts)

def  add_tag(post_id, tag_name) -> None:
    db = get_db()

    # Check if tag already in table `tag` or not
    tag = db.execute(
        "SELECT tag_name FROM tag WHERE tag_name = ?",(tag_name,)
    ).fetchone()

    if tag:
        tag_id = tag['id']
    else:
        # add tag into table
        tag_id = db.execute(
            "INSERT INTO tag (tag_name) VALUES (?)",(tag_name,)
        )
        tag_id = tag_id.lastrowid

    db.execute(
        "INSERT INTO post_tag (post_id, tag_id) VALUES (?,?)",(post_id, tag_id)
    )
    db.commit()

def get_tag(post_id):
    db = get_db()
    tag = db.execute(
        "SELECT tag.tag_name"
        " FROM tag"
        " JOIN post_tag ON post_tag.tag_id = tag.id"
        " WHERE post_tag.post_id = ?",(post_id,)
    )
    tags = [row['tag_name'] for row in tag.fetchall()]
    return tags

def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


def get_post_like(id):
    post_like = (
        get_db()
        .execute("SELECT * FROM post_like WHERE post_id = ? AND is_liked = 1", (id,))
        .fetchall()
    )

    return post_like


def has_post_like(id):
    has_like = (
        get_db()
        .execute(
            "SELECt * FROM post_like WHERE post_id = ? AND user_id = ? AND is_liked = 1 ",
            (id, g.user["id"]),
        )
        .fetchone()
    )

    return has_like

# Create route for create post
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        tags = request.form.getlist("tags")
        error = None
        
        if not title:
            error = "Title is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            post_id =db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            post_id = post_id.lastrowid

            for tag in tags:
                add_tag(post_id, tag)

            db.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")

# Get all comment from post
def get_post_comment(id):
    post_comment = (
        get_db()
        .execute(
            "SELECT comment.*, user.username FROM comment JOIN user ON comment.user_id = user.id WHERE comment.post_id = ? ORDER BY comment.created_at ASC",
            (id,),
        )
        .fetchall()
    )

    return post_comment


# update route for update post
@bp.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?" " WHERE id= ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))
    return render_template("blog/update.html", post=post)


# Delete route for delete post
@bp.route("/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()

    return redirect(url_for("blog.index"))


# detail view for showing single post.
@bp.route("/<int:id>/view", methods=["GET", "POST"])
def post_single_view(id):
    post = get_post(id, check_author=False)
    user = get_db().execute("SELECT * FROM user WHERE id = ?",(post['author_id'],)).fetchone()
    comment = get_post_comment(id)
    like_post = get_post_like(id)
    like_post = len(like_post)
    
    tags = get_tag(id)

    user_id = session.get("user_id")

    post_content = post['body']

    html = markdown.markdown(post_content, extensions=["extra","fenced_code", "codehilite"])

    render_html =  html

    if user_id is not None:
        user_liked = has_post_like(id)
    else:
        user_liked = False

    if request.method == "POST":
        # Get the comment data from form submissiong
        comment_body = request.form["comment_body"]

        db = get_db()
        db.execute(
            "INSERT INTO comment (post_id, user_id, body) VALUES" " (?, ?, ?)",
            (id, g.user["id"], comment_body),
        )

        db.commit()

        return redirect(url_for("blog.post_single_view", id=id))

    return render_template(
        "blog/view.html",
        user=user,
        tags=tags,
        post=post,
        post_markdown=render_html,
        total_like=like_post,
        user_liked=user_liked,
        comment=comment,
    )


@bp.route("/like/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    # chck if the user has already liked the post
    like = (
        get_db()
        .execute(
            "SELECT * FROM post_like WHERE post_id = ? AND user_id=?",
            (post_id, g.user["id"]),
        )
        .fetchone()
    )

    if like is None:
        # create a new like entry
        db = get_db()
        db.execute(
            "INSERT INTO post_like (post_id, user_id, is_liked) VALUES (?, ?, ?)",
            (post_id, g.user["id"], 1),
        )
        db.commit()
    else:
        db = get_db()
        db.execute(
            "UPDATE post_like SET is_liked = 1 WHERE post_id = ? AND user_id = ?",
            (post_id, g.user["id"]),
        )
        db.commit()

    return redirect(url_for("blog.post_single_view", id=post_id))


@bp.route("/unlike/<int:post_id>", methods=["POST"])
@login_required
def unlike_post(post_id):
    # chck if the user has already liked the post
    like = (
        get_db()
        .execute(
            "SELECT * FROM post_like WHERE post_id = ? AND user_id=? AND is_liked = 1",
            (post_id, g.user["id"]),
        )
        .fetchone()
    )

    if like is not None:
        # create a new like entry
        db = get_db()
        db.execute("UPDATE post_like SET is_liked = ? WHERE id = ?", (0, like[0]))
        db.commit()

    return redirect(url_for("blog.post_single_view", id=post_id))
