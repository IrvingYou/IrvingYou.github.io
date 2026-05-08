#!/usr/bin/env python3
import html
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "blog" / "posts"
ARTICLES_DIR = ROOT / "blog" / "articles"
BLOG_INDEX = ROOT / "blog" / "index.html"


@dataclass
class Post:
    title: str
    date: str
    slug: str
    summary: str
    body_html: str


def parse_front_matter(text):
    if not text.startswith("---\n"):
        return {}, text

    _, front_matter, body = text.split("---\n", 2)
    metadata = {}
    for line in front_matter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()
    return metadata, body.lstrip()


def inline_markdown(text):
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{html.escape(match.group(2), quote=True)}">{match.group(1)}</a>',
        escaped,
    )
    return escaped


def markdown_to_html(markdown):
    blocks = []
    paragraph = []
    list_items = []
    in_code_block = False
    code_lines = []

    def flush_paragraph():
        if paragraph:
            blocks.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list():
        if list_items:
            items = "\n".join(f"<li>{inline_markdown(item)}</li>" for item in list_items)
            blocks.append(f"<ul>\n{items}\n</ul>")
            list_items.clear()

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            if in_code_block:
                code = html.escape("\n".join(code_lines))
                blocks.append(f"<pre><code>{code}</code></pre>")
                code_lines.clear()
                in_code_block = False
            else:
                flush_paragraph()
                flush_list()
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(raw_line)
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            continue

        heading_match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            content = inline_markdown(heading_match.group(2))
            blocks.append(f"<h{level}>{content}</h{level}>")
            continue

        list_match = re.match(r"^[-*]\s+(.+)$", line)
        if list_match:
            flush_paragraph()
            list_items.append(list_match.group(1))
            continue

        paragraph.append(line.strip())

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def read_post(path):
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_front_matter(text)
    first_heading = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = metadata.get("title") or (first_heading.group(1) if first_heading else path.stem)
    date = metadata.get("date") or path.stem[:10]
    slug = metadata.get("slug") or path.stem
    summary = metadata.get("summary", "")
    return Post(
        title=title,
        date=date,
        slug=slug,
        summary=summary,
        body_html=markdown_to_html(body),
    )


def page_shell(title, content, stylesheet_path, home_path, blog_path, about_path):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - Irving You</title>
    <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{stylesheet_path}">
</head>
<body>
    <div class="header">
        <div class="logo">Irving You</div>
        <nav class="nav">
            <a href="{home_path}">Home</a>
            <a href="{blog_path}">Blog</a>
            <a href="{about_path}">About</a>
        </nav>
    </div>

    <main class="main-content">
{content}
    </main>
</body>
</html>
"""


def render_article(post):
    content = f"""        <article class="post-content">
            <a class="back-link" href="../">Back to Blog</a>
            <time datetime="{html.escape(post.date)}">{format_date(post.date)}</time>
{post.body_html}
        </article>"""
    return page_shell(post.title, content, "../../style.css", "../../index.html", "../", "../../about.html")


def render_index(posts):
    if posts:
        items = "\n".join(
            f"""                <li>
                    <a href="articles/{html.escape(post.slug)}.html">{html.escape(post.title)}</a>
                    <time datetime="{html.escape(post.date)}">{format_date(post.date)}</time>
                    <p>{html.escape(post.summary)}</p>
                </li>"""
            for post in posts
        )
    else:
        items = '                <li class="empty-posts">Blog posts coming soon...</li>'

    content = f"""        <section class="blog-content active">
            <h1>Blog</h1>
            <ul class="post-list">
{items}
            </ul>
        </section>"""
    return page_shell("Blog", content, "../style.css", "../index.html", "./", "../about.html")


def format_date(date_text):
    try:
        date = datetime.strptime(date_text, "%Y-%m-%d")
        return f"{date.strftime('%B')} {date.day}, {date.year}"
    except ValueError:
        return date_text


def main():
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    posts = [read_post(path) for path in sorted(POSTS_DIR.glob("*.md"))]
    posts.sort(key=lambda post: post.date, reverse=True)

    for post in posts:
        (ARTICLES_DIR / f"{post.slug}.html").write_text(render_article(post), encoding="utf-8")

    BLOG_INDEX.write_text(render_index(posts), encoding="utf-8")
    print(f"Built {len(posts)} blog post(s).")


if __name__ == "__main__":
    main()
