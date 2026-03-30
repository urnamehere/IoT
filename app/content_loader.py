"""Content loading and rendering from Markdown/YAML files."""

import os

import frontmatter
import markdown
from flask import Blueprint, current_app, render_template, abort

content = Blueprint("content", __name__)


def load_content_file(content_type, slug):
    """Load a markdown content file with YAML frontmatter.

    Args:
        content_type: One of 'modules', 'labs', 'challenges', 'hardware', 'software'
        slug: The filename without extension (e.g. '01-iot-fundamentals')

    Returns:
        dict with 'metadata' and 'html' keys, or None if not found.
    """
    content_dir = current_app.config["CONTENT_DIR"]
    filepath = os.path.join(content_dir, content_type, f"{slug}.md")

    if not os.path.isfile(filepath):
        return None

    post = frontmatter.load(filepath)
    html = markdown.markdown(
        post.content,
        extensions=["fenced_code", "codehilite", "tables", "toc", "attr_list"],
    )

    return {
        "metadata": dict(post.metadata),
        "html": html,
    }


def list_content(content_type):
    """List all content files of a given type, sorted by filename.

    Returns:
        List of dicts with metadata from each file's frontmatter.
    """
    content_dir = current_app.config["CONTENT_DIR"]
    type_dir = os.path.join(content_dir, content_type)

    if not os.path.isdir(type_dir):
        return []

    items = []
    for filename in sorted(os.listdir(type_dir)):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(type_dir, filename)
        post = frontmatter.load(filepath)
        meta = dict(post.metadata)
        meta["slug"] = filename.rsplit(".", 1)[0]
        items.append(meta)

    return items


@content.route("/modules/")
def module_list():
    modules = list_content("modules")
    return render_template("modules/index.html", modules=modules)


@content.route("/modules/<slug>")
def module_detail(slug):
    data = load_content_file("modules", slug)
    if not data:
        abort(404)
    return render_template("modules/detail.html", **data)


@content.route("/labs/")
def lab_list():
    labs = list_content("labs")
    return render_template("labs/index.html", labs=labs)


@content.route("/labs/<slug>")
def lab_detail(slug):
    data = load_content_file("labs", slug)
    if not data:
        abort(404)
    return render_template("labs/detail.html", **data)


@content.route("/challenges/")
def challenge_list():
    challenges = list_content("challenges")
    return render_template("challenges/index.html", challenges=challenges)


@content.route("/challenges/<slug>")
def challenge_detail(slug):
    data = load_content_file("challenges", slug)
    if not data:
        abort(404)
    return render_template("challenges/detail.html", **data)


@content.route("/hardware/")
def hardware_list():
    items = list_content("hardware")
    return render_template("modules/index.html", modules=items, title="Hardware Guides")


@content.route("/hardware/<slug>")
def hardware_detail(slug):
    data = load_content_file("hardware", slug)
    if not data:
        abort(404)
    return render_template("modules/detail.html", **data)


@content.route("/software/")
def software_list():
    items = list_content("software")
    return render_template("modules/index.html", modules=items, title="Software Tools")


@content.route("/software/<slug>")
def software_detail(slug):
    data = load_content_file("software", slug)
    if not data:
        abort(404)
    return render_template("modules/detail.html", **data)
