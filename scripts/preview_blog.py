#!/usr/bin/env python3
import http.server
import os
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "blog" / "posts"
BUILD_SCRIPT = ROOT / "scripts" / "build_blog.py"
PORT = int(os.environ.get("PORT", "8000"))


def build():
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=ROOT, check=True)


def snapshot():
    return {
        path: path.stat().st_mtime
        for path in POSTS_DIR.glob("*.md")
        if path.is_file()
    }


def watch_posts():
    previous = snapshot()
    while True:
        time.sleep(1)
        current = snapshot()
        if current != previous:
            try:
                build()
            except subprocess.CalledProcessError:
                print("Build failed. Fix the post and save again.")
            previous = current


def main():
    build()
    threading.Thread(target=watch_posts, daemon=True).start()

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as server:
        print(f"Preview: http://localhost:{PORT}/blog/")
        print("Leave this running while you write. Press Ctrl+C to stop.")
        os.chdir(ROOT)
        server.serve_forever()


if __name__ == "__main__":
    main()
