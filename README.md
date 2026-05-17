This is my blog.

## Writing Preview

Start the local browser editor:

```bash
python scripts/editor.py
```

Then open:

```text
http://localhost:8000/editor/
```

Use the editor to create posts, write Markdown with a live preview, and save.
Saving writes to `blog/posts/` and rebuilds the generated HTML.

Create a new Markdown draft:

```bash
python scripts/new_post.py "My Post Title"
```

Start a local preview server:

```bash
python scripts/preview_blog.py
```

Then open:

```text
http://localhost:8000/blog/
```

Keep the preview command running while you write. When you save files in
`blog/posts/`, the preview script rebuilds the generated HTML automatically.

## Updating the Blog

1. Add a Markdown file in `blog/posts/`.
2. Include front matter at the top:

```markdown
---
title: My Post Title
date: 2026-05-08
slug: my-post-title
summary: One short sentence for the blog list.
---

# My Post Title

Write the post here.
```

3. Rebuild the static blog pages:

```bash
python3 scripts/build_blog.py
```

4. Commit and push the generated files.
