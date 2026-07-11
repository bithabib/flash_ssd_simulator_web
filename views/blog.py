"""Beginner blog: /blog index and /blog/<slug> posts explaining SSDs and ZNS."""
from flask import render_template, abort

from app import app
from views.blog_content import POSTS, POSTS_BY_SLUG, CATEGORIES


@app.route("/blog")
def blog_index():
    return render_template("blog_index.html", posts=POSTS, categories=CATEGORIES)


@app.route("/blog/<slug>")
def blog_post(slug):
    post = POSTS_BY_SLUG.get(slug)
    if not post:
        abort(404)
    idx = POSTS.index(post)
    prev_post = POSTS[idx - 1] if idx > 0 else None
    next_post = POSTS[idx + 1] if idx < len(POSTS) - 1 else None
    related = [POSTS_BY_SLUG[s] for s in post.get("related", []) if s in POSTS_BY_SLUG]
    return render_template("blog_post.html", post=post, posts=POSTS,
                           categories=CATEGORIES, prev_post=prev_post,
                           next_post=next_post, related=related)
