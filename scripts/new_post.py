#!/usr/bin/env python3
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "blog" / "posts"


def slugify(title):
    slug = title.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "untitled"


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/new_post.py "My Post Title"')
        raise SystemExit(1)

    title = " ".join(sys.argv[1:]).strip()
    today = date.today().isoformat()
    slug = slugify(title)
    path = POSTS_DIR / f"{today}-{slug}.md"

    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"Post already exists: {path.relative_to(ROOT)}")
        raise SystemExit(1)

    path.write_text(
        f"""---
title: {title}
date: {today}
slug: {slug}
summary: 
---

# {title}

Write your post here.
""",
        encoding="utf-8",
    )
    print(f"Created {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
