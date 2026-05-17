#!/usr/bin/env python3
import html
import json
import re
import subprocess
import sys
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "blog" / "posts"
BUILD_SCRIPT = ROOT / "scripts" / "build_blog.py"
PORT = 8000
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else PORT


EDITOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Editor</title>
    <script>
        window.MathJax = {
            tex: {
                inlineMath: [["$", "$"], ["\\\\(", "\\\\)"]],
                displayMath: [["$$", "$$"], ["\\\\[", "\\\\]"]]
            }
        };
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            color: #111;
            background: #f6f7f8;
        }
        button, input, textarea {
            font: inherit;
        }
        .app {
            display: grid;
            grid-template-columns: 280px minmax(0, 1fr);
            min-height: 100vh;
        }
        .sidebar {
            border-right: 1px solid #d8dde2;
            background: #fff;
            padding: 18px;
        }
        .brand {
            margin-bottom: 16px;
            font-size: 20px;
            font-weight: 700;
        }
        .post-list {
            display: grid;
            gap: 8px;
            margin-top: 16px;
        }
        .post-item {
            width: 100%;
            border: 1px solid #d8dde2;
            border-radius: 6px;
            background: #fff;
            padding: 10px;
            text-align: left;
            cursor: pointer;
        }
        .post-item.active {
            border-color: #1B5E83;
            background: #eef7fb;
        }
        .post-title {
            display: block;
            font-weight: 700;
        }
        .post-date {
            display: block;
            margin-top: 4px;
            color: #667085;
            font-size: 13px;
        }
        .main {
            display: grid;
            grid-template-rows: auto minmax(0, 1fr);
            min-width: 0;
        }
        .toolbar {
            display: flex;
            gap: 10px;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #d8dde2;
            background: #fff;
            padding: 14px 18px;
        }
        .status {
            color: #667085;
            font-size: 14px;
        }
        .button {
            border: 1px solid #1B5E83;
            border-radius: 6px;
            background: #1B5E83;
            color: #fff;
            padding: 8px 12px;
            cursor: pointer;
        }
        .button.secondary {
            background: #fff;
            color: #1B5E83;
        }
        .editor-grid {
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
            min-height: 0;
        }
        .pane {
            min-width: 0;
            min-height: 0;
            overflow: auto;
            padding: 18px;
        }
        .write-pane {
            border-right: 1px solid #d8dde2;
            background: #fff;
        }
        .field {
            display: grid;
            gap: 6px;
            margin-bottom: 12px;
        }
        label {
            color: #344054;
            font-size: 13px;
            font-weight: 700;
        }
        input, textarea {
            width: 100%;
            border: 1px solid #cbd5df;
            border-radius: 6px;
            padding: 10px;
            outline: none;
        }
        input:focus, textarea:focus {
            border-color: #1B5E83;
        }
        textarea {
            min-height: 56vh;
            resize: vertical;
            line-height: 1.6;
            font-family: Consolas, "Courier New", monospace;
        }
        .preview-pane {
            background: #fdfdfc;
        }
        .preview {
            max-width: 760px;
            margin: 0 auto;
            color: #111;
            line-height: 1.75;
        }
        .preview h1, .preview h2, .preview h3 {
            margin: 1.5rem 0 1rem;
            font-family: Georgia, serif;
            line-height: 1.3;
        }
        .preview h1 { font-size: 2.2rem; }
        .preview p, .preview ul, .preview pre { margin-bottom: 1rem; }
        .preview ul { padding-left: 1.5rem; }
        .preview time {
            display: block;
            margin: 0.35rem 0 0.7rem;
            color: #666;
            font-size: 0.95rem;
        }
        .preview code {
            background: #f4f4f4;
            border-radius: 4px;
            padding: 0.1rem 0.3rem;
            font-size: 0.95em;
        }
        .preview pre {
            overflow-x: auto;
            background: #f4f4f4;
            border-radius: 6px;
            padding: 1rem;
        }
        .preview pre code {
            background: none;
            padding: 0;
        }
        .final-link {
            color: #1B5E83;
            text-decoration: none;
        }
        @media (max-width: 900px) {
            .app { grid-template-columns: 1fr; }
            .sidebar { border-right: 0; border-bottom: 1px solid #d8dde2; }
            .editor-grid { grid-template-columns: 1fr; }
            .write-pane { border-right: 0; border-bottom: 1px solid #d8dde2; }
        }
    </style>
</head>
<body>
    <div class="app">
        <aside class="sidebar">
            <div class="brand">Blog Editor</div>
            <button class="button" id="newPost">New Post</button>
            <div class="post-list" id="postList"></div>
        </aside>
        <main class="main">
            <div class="toolbar">
                <div class="status" id="status">Ready</div>
                <div>
                    <a class="final-link" id="finalLink" href="/blog/" target="_blank">Blog</a>
                    <button class="button secondary" id="savePost">Save</button>
                </div>
            </div>
            <div class="editor-grid">
                <section class="pane write-pane">
                    <div class="field">
                        <label for="title">Title</label>
                        <input id="title" placeholder="My Post Title">
                    </div>
                    <div class="field">
                        <label for="date">Date</label>
                        <input id="date" type="date">
                    </div>
                    <div class="field">
                        <label for="slug">Slug</label>
                        <input id="slug" placeholder="my-post-title">
                    </div>
                    <div class="field">
                        <label for="summary">Summary</label>
                        <input id="summary" placeholder="One short sentence for the blog list.">
                    </div>
                    <div class="field">
                        <label for="body">Markdown</label>
                        <textarea id="body" spellcheck="true"></textarea>
                    </div>
                </section>
                <section class="pane preview-pane">
                    <article class="preview" id="preview"></article>
                </section>
            </div>
        </main>
    </div>
    <script>
        const state = { posts: [], originalPath: null, dirty: false };
        const fields = {
            title: document.getElementById("title"),
            date: document.getElementById("date"),
            slug: document.getElementById("slug"),
            summary: document.getElementById("summary"),
            body: document.getElementById("body"),
        };
        const postList = document.getElementById("postList");
        const preview = document.getElementById("preview");
        const statusEl = document.getElementById("status");
        const finalLink = document.getElementById("finalLink");

        function today() {
            return new Date().toISOString().slice(0, 10);
        }

        function slugify(text) {
            const slug = text.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
            return slug || "untitled";
        }

        function escapeHtml(text) {
            return text.replace(/[&<>"']/g, value => ({
                "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
            }[value]));
        }

        function inlineMarkdown(text) {
            const mathPattern = /(\\$\\$[\\s\\S]*?\\$\\$|\\\\\\[[\\s\\S]*?\\\\\\]|\\\\\\([\\s\\S]*?\\\\\\)|\\$(?!\\$)[^\\n$]+\\$)/g;
            return text.split(mathPattern).map(part => {
                if (!part) return "";
                if (part.match(mathPattern)) return escapeHtml(part);
                let value = escapeHtml(part);
                value = value.replace(/`([^`]+)`/g, "<code>$1</code>");
                value = value.replace(/\\*\\*([^*]+)\\*\\*/g, "<strong>$1</strong>");
                value = value.replace(/\\*([^*]+)\\*/g, "<em>$1</em>");
                value = value.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2">$1</a>');
                return value;
            }).join("");
        }

        function markdownToHtml(markdown) {
            const blocks = [];
            let paragraph = [];
            let listItems = [];
            let inCode = false;
            let codeLines = [];

            function flushParagraph() {
                if (paragraph.length) {
                    blocks.push(`<p>${inlineMarkdown(paragraph.join(" "))}</p>`);
                    paragraph = [];
                }
            }
            function flushList() {
                if (listItems.length) {
                    blocks.push(`<ul>${listItems.map(item => `<li>${inlineMarkdown(item)}</li>`).join("")}</ul>`);
                    listItems = [];
                }
            }

            for (const rawLine of markdown.split(/\\r?\\n/)) {
                const line = rawLine.replace(/\\s+$/, "");
                if (line.startsWith("```")) {
                    if (inCode) {
                        blocks.push(`<pre><code>${escapeHtml(codeLines.join("\\n"))}</code></pre>`);
                        codeLines = [];
                        inCode = false;
                    } else {
                        flushParagraph();
                        flushList();
                        inCode = true;
                    }
                    continue;
                }
                if (inCode) {
                    codeLines.push(rawLine);
                    continue;
                }
                if (!line.trim()) {
                    flushParagraph();
                    flushList();
                    continue;
                }
                const heading = line.match(/^(#{1,3})\\s+(.+)$/);
                if (heading) {
                    flushParagraph();
                    flushList();
                    const level = heading[1].length;
                    blocks.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
                    continue;
                }
                const list = line.match(/^[-*]\\s+(.+)$/);
                if (list) {
                    flushParagraph();
                    listItems.push(list[1]);
                    continue;
                }
                paragraph.push(line.trim());
            }
            flushParagraph();
            flushList();
            return blocks.join("\\n");
        }

        function renderPreview() {
            const title = fields.title.value.trim() || "Untitled";
            const date = fields.date.value || today();
            const body = fields.body.value.trim() || `# ${title}\\n\\n`;
            preview.innerHTML = `<time datetime="${escapeHtml(date)}">${escapeHtml(date)}</time>${markdownToHtml(body)}`;
            finalLink.href = `/blog/articles/${encodeURIComponent(fields.slug.value || "untitled")}.html`;
            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetClear([preview]);
                window.MathJax.typesetPromise([preview]);
            }
        }

        function setStatus(text) {
            statusEl.textContent = text;
        }

        function setDirty(value) {
            state.dirty = value;
            setStatus(value ? "Unsaved changes" : "Saved");
        }

        function readForm() {
            return {
                originalPath: state.originalPath,
                title: fields.title.value.trim(),
                date: fields.date.value,
                slug: fields.slug.value.trim(),
                summary: fields.summary.value.trim(),
                body: fields.body.value,
            };
        }

        function loadForm(post) {
            state.originalPath = post.path || null;
            fields.title.value = post.title || "";
            fields.date.value = post.date || today();
            fields.slug.value = post.slug || slugify(post.title || "");
            fields.summary.value = post.summary || "";
            fields.body.value = post.body || `# ${fields.title.value || "Untitled"}\\n\\n`;
            renderPreview();
            setDirty(false);
            renderPostList();
        }

        async function loadPosts() {
            const response = await fetch("/api/posts");
            state.posts = await response.json();
            renderPostList();
        }

        async function loadPost(path) {
            const response = await fetch(`/api/post?path=${encodeURIComponent(path)}`);
            if (!response.ok) {
                setStatus("Could not load post");
                return;
            }
            loadForm(await response.json());
        }

        function renderPostList() {
            postList.innerHTML = "";
            for (const post of state.posts) {
                const button = document.createElement("button");
                button.className = `post-item${post.path === state.originalPath ? " active" : ""}`;
                button.innerHTML = `<span class="post-title">${escapeHtml(post.title)}</span><span class="post-date">${escapeHtml(post.date)}</span>`;
                button.addEventListener("click", () => {
                    if (state.dirty && !confirm("Discard unsaved changes?")) return;
                    loadPost(post.path);
                });
                postList.appendChild(button);
            }
        }

        function newPost() {
            if (state.dirty && !confirm("Discard unsaved changes?")) return;
            loadForm({
                title: "",
                date: today(),
                slug: "",
                summary: "",
                body: "# Untitled\\n\\n",
            });
            setStatus("New post");
        }

        async function savePost() {
            const payload = readForm();
            if (!payload.title || !payload.date || !payload.slug) {
                setStatus("Title, date, and slug are required");
                return;
            }
            setStatus("Saving...");
            const response = await fetch("/api/save", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const result = await response.json();
            if (!response.ok) {
                setStatus(result.error || "Save failed");
                return;
            }
            state.originalPath = result.path;
            await loadPosts();
            renderPreview();
            setDirty(false);
            setStatus(`Saved. Final page: ${result.article}`);
        }

        document.getElementById("newPost").addEventListener("click", newPost);
        document.getElementById("savePost").addEventListener("click", savePost);
        fields.title.addEventListener("input", () => {
            if (!state.originalPath && (!fields.slug.value || fields.slug.value === "untitled")) {
                fields.slug.value = slugify(fields.title.value);
            }
            renderPreview();
            setDirty(true);
        });
        for (const field of Object.values(fields)) {
            field.addEventListener("input", () => {
                renderPreview();
                setDirty(true);
            });
        }

        loadPosts().then(newPost);
    </script>
</body>
</html>
"""


def parse_front_matter(text):
    if not text.startswith("---\n"):
        return {}, text
    _, front_matter, body = text.split("---\n", 2)
    metadata = {}
    for line in front_matter.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()
    return metadata, body.lstrip()


def read_post(path):
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_front_matter(text)
    first_heading = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = metadata.get("title") or (first_heading.group(1) if first_heading else path.stem)
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "title": title,
        "date": metadata.get("date") or path.stem[:10],
        "slug": metadata.get("slug") or path.stem,
        "summary": metadata.get("summary", ""),
        "body": body,
    }


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "untitled"


def json_response(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def text_response(handler, status, text, content_type="text/html; charset=utf-8"):
    body = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def build_blog():
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=ROOT, check=True)


def safe_post_path(relative_path):
    path = (ROOT / relative_path).resolve()
    if not path.is_relative_to(POSTS_DIR.resolve()):
        raise ValueError("Invalid post path")
    if path.suffix != ".md":
        raise ValueError("Post path must be Markdown")
    return path


class EditorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/editor", "/editor/"):
            text_response(self, 200, EDITOR_HTML)
            return
        if parsed.path == "/api/posts":
            posts = [read_post(path) for path in sorted(POSTS_DIR.glob("*.md"))]
            posts.sort(key=lambda post: post["date"], reverse=True)
            json_response(self, 200, [
                {key: post[key] for key in ("path", "title", "date", "slug", "summary")}
                for post in posts
            ])
            return
        if parsed.path == "/api/post":
            query = parse_qs(parsed.query)
            relative_path = query.get("path", [""])[0]
            try:
                path = safe_post_path(relative_path)
            except ValueError as error:
                json_response(self, 400, {"error": str(error)})
                return
            if not path.exists():
                json_response(self, 404, {"error": "Post not found"})
                return
            json_response(self, 200, read_post(path))
            return
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/save":
            json_response(self, 404, {"error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            title = payload.get("title", "").strip()
            post_date = payload.get("date", "").strip()
            slug = slugify(payload.get("slug", ""))
            summary = payload.get("summary", "").strip()
            body = payload.get("body", "").strip() + "\n"
            original_path = payload.get("originalPath")
            if not title or not post_date or not slug:
                raise ValueError("Title, date, and slug are required")

            target = POSTS_DIR / f"{post_date}-{slug}.md"
            if original_path:
                previous_target = safe_post_path(original_path)
                if target != previous_target and target.exists():
                    raise ValueError("A post with this date and slug already exists")
            elif target.exists():
                raise ValueError("A post with this date and slug already exists")

            content = f"""---
title: {title}
date: {post_date}
slug: {slug}
summary: {summary}
---

{body}"""
            target.write_text(content, encoding="utf-8")
            if original_path and target != previous_target and previous_target.exists():
                previous_target.unlink()
            build_blog()
        except (json.JSONDecodeError, OSError, subprocess.CalledProcessError, ValueError) as error:
            json_response(self, 400, {"error": str(error)})
            return

        json_response(self, 200, {
            "path": str(target.relative_to(ROOT)).replace("\\", "/"),
            "article": f"/blog/articles/{html.escape(slug)}.html",
        })


def main():
    build_blog()
    server = ThreadingHTTPServer(("", PORT), EditorHandler)
    print(f"Editor: http://localhost:{PORT}/editor/")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
