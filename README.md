This is my blog.

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
