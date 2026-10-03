# gsheir.com

Personal website and blog for Geoffrey Sheir, built with [Astro](https://astro.build), TypeScript, and [Tailwind CSS](https://tailwindcss.com).

## Local development

Prerequisites: Node.js 22 (see `.nvmrc`).

```bash
npm install
npm run dev
```

The site will be available at `http://localhost:4321/`.

| Command                | Action                                                        |
| ---------------------- | ------------------------------------------------------------- |
| `npm run dev`          | Start the development server                                  |
| `npm run build`        | Type check and build to `dist/`, checking links and redirects |
| `npm run preview`      | Preview the build                                             |
| `npm run format`       | Format with Prettier                                          |
| `npm run format:check` | Check formatting (run in CI)                                  |

To run the production container locally (Caddy serving the build, as on Railway):

```bash
docker compose up --build
```

The site will be available at `http://localhost:8080/`.

## Writing a blog post

Add a Markdown file to `src/content/blog/`. The file name becomes the URL, e.g. `src/content/blog/my-post.md` is served at `/blog/my-post/`, with the raw Markdown at `/blog/my-post.md`.

```markdown
---
title: My post
description: A one-sentence summary shown on cards, in search results, and in feeds.
pubDate: 2026-01-31
category: Data analysis
tags: [Arsenal, Football]
featured: true # optional: show on the homepage
series: # optional: link parts of a series together
  name: My series
  part: 1
---

Some text.

![Alt text for the image](https://images.gsheir.com/folder/image.png)
_Caption, with an optional [link](https://example.com)_

![Left image](https://images.gsheir.com/a.png) ![Right image](https://images.gsheir.com/b.png)

> [!NOTE]
> A callout.
```

Set `draft: true` to hide a post from the built site while you work on it (drafts still show in `npm run dev`). Rename a file to `.mdx` to use components inside a post.

The CV lives in `src/content/pages/cv.md`.

## Agent-friendly extras

- Every post (and the CV) has a raw Markdown version at the same URL with `.md`, plus "Copy as Markdown" and "Open in Claude/ChatGPT" buttons.
- [`/llms.txt`](https://gsheir.com/llms.txt) indexes the site; [`/llms-full.txt`](https://gsheir.com/llms-full.txt) has the full text of every post.
- [`/rss.xml`](https://gsheir.com/rss.xml) and [`/sitemap-index.xml`](https://gsheir.com/sitemap-index.xml).

## Deployment

The site is deployed on [Railway](https://railway.com) from `Dockerfile.web`: Node builds the site, then [Caddy](https://caddyserver.com) serves `dist/` on `$PORT`, with permanent redirects from the old URLs (see `src/redirects.ts`). Configuration is in `railway.json`.

Moving to Cloudflare is tracked in [#4](https://github.com/gsheir/gsheir.com/issues/4). The build already writes a Cloudflare-compatible `dist/_redirects`.
