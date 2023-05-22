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


# Create route for create post
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
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
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


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
@bp.route("/<int:id>/view")
def post_single_view(id):
    post = get_post(id, check_author=False)
    like_post = get_post_like(id)
    like_post = len(like_post)

    user_id = session.get("user_id")

    if user_id is not None:
        user_liked = has_post_like(id)
    else:
        user_liked = False

    return render_template(
        "blog/view.html", post=post, total_like=like_post, user_liked=user_liked
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
