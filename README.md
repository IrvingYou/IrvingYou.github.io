This is my blog.

## Blog 写作流程

以下命令默认在项目根目录运行：

```powershell
cd D:\IrvingYou.github.io
```

### 1. 打开网页编辑器

```powershell
python scripts\editor.py
```

然后在浏览器打开终端提示的地址，通常是：

```text
http://localhost:8000/editor/
```

可以在网页里新建文章、写 Markdown、实时预览，并点击保存。

### 2. 本地预览网站

```powershell
python scripts\preview_blog.py
```

然后打开：

```text
http://localhost:8000/blog/
```

如果改了文章但预览没有刷新，可以手动重新生成：

```powershell
python scripts\build_blog.py
```

### 3. 发布到网站

确认本地预览没问题后：

```powershell
git status
git add blog\posts blog\index.html blog\articles
git commit -m "Update blog"
git push origin main
```

发布后等 1-2 分钟，打开：

```text
https://irvingyou.github.io/blog/
```

如果网页还是旧内容，按 `Ctrl + F5` 强制刷新。

## 文章格式

每篇文章的源文件在：

```text
blog/posts/
```

文章是 Markdown 文件，开头需要 front matter：

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

字段含义：

- `title`: 文章标题
- `date`: 发布日期
- `slug`: 文章网址名，比如 `my-post-title` 会生成 `blog/articles/my-post-title.html`
- `summary`: blog 列表里的短摘要

数学公式写法：

```markdown
行内公式：$a^2+b^2=c^2$

独立公式：
$$
E = mc^2
$$
```

## 改文章名字

如果只是改网页上显示的标题，改 Markdown 文件开头的 `title`，然后重新生成：

```powershell
python scripts\build_blog.py
```

如果也想改文章网址，改 `slug`，然后重新生成：

```powershell
python scripts\build_blog.py
```

## 删除文章

推荐在网页编辑器里删除：

1. 运行编辑器：

```powershell
python scripts\editor.py
```

2. 打开：

```text
http://localhost:8000/editor/
```

3. 在左侧选中文章，点击 `Delete`。

编辑器会自动删除对应的 Markdown 文件，并重新生成 `blog/index.html` 和 `blog/articles/`。

也可以手动删除 `blog/posts/` 里的对应 `.md` 文件，例如：

```powershell
del blog\posts\my-post.md
```

然后重新生成：

```powershell
python scripts\build_blog.py
```

最后提交并发布：

```powershell
git add blog\posts blog\index.html blog\articles
git commit -m "Remove blog post"
git push origin main
```
