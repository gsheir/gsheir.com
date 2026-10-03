# General instructions

Do not make code changes unless explicitly asked. Just make proposals to start off and ask for user confirmation before making changes.

If you are unclear on the requirements, clarify those before proposing solutions.

Do not suggest code snippets unless asked.

Read the full codebase before making any proposals or changes.

Do not create additional markdown files to report progress or as a summary. Display these in the chat window instead.

Add only necessary comments. Do not use excessive formatting with dividers; newlines are sufficient.

Use British English in content, code, and documentation.

# Stack

This is a static site built with [Astro](https://docs.astro.build), TypeScript (strict), and [Tailwind CSS v4](https://tailwindcss.com/docs). There is no server-side code: `npm run build` produces plain files in `dist/`, which are served by Caddy in production.

- Use `npm` for dependency management (`npm install <package>`), and keep `package-lock.json` committed.
- Run `npm run dev` for local development (http://localhost:4321).
- After making changes, run `npm run format` and `npm run build`, and fix any errors before finishing. The build runs `astro check` (type checking) and fails on broken internal links or invalid redirects.

# Project structure

- `src/content/blog/` – blog posts as Markdown (`.md`) or MDX (`.mdx`). The file name is the URL slug.
- `src/content/pages/cv.md` – the CV.
- `src/content.config.ts` – frontmatter schemas. The build fails if a post's frontmatter does not match.
- `src/pages/` – routes. `[slug].md.ts`, `cv.md.ts`, `llms.txt.ts`, and `llms-full.txt.ts` serve raw Markdown for agents.
- `src/components/` and `src/layouts/` – shared UI.
- `src/styles/global.css` – Tailwind theme: palette, fonts, and theme-aware tokens, plus blog typography.
- `src/plugins/rehype-figures.ts` – turns image paragraphs into figures with captions.
- `src/redirects.ts` – permanent redirects. Generates `redirects.caddy` (Railway) and `dist/_redirects` (Cloudflare).
- `src/integrations/site-checks.ts` – post-build redirect generation and link checks.
- `Dockerfile.web`, `Caddyfile`, and `railway.json` – Railway deployment.

# Writing posts

Posts are plain Markdown by default. Only use MDX (`.mdx`) when a post needs a component.

- Frontmatter: `title`, `description`, `pubDate`, `category` are required; `tags`, `series` (`name`, `part`), `featured`, `draft`, `updatedDate`, and `image` are optional.
- Images are hosted on `images.gsheir.com`. An image in its own paragraph becomes a figure. An italic line directly under it becomes the caption. Images on the same line are shown side by side.
- Use GitHub-style callouts for notes: `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`.
- Link to other pages with root-relative URLs (e.g. `/blog/coaching/`).
- If a URL changes, add the old URL to `src/redirects.ts`.

# Styling

- Use Tailwind utilities with the theme tokens in `src/styles/global.css` rather than hard-coded colours: `bg-surface`, `bg-surface-alt`, `bg-card`, `text-ink`, `text-ink-muted`, `text-ink-subtle`, `text-primary`, `border-line`, and the brand scales `crimson`, `lilac`, and `sky`.
- Dark mode is driven by `data-theme="dark"` on `<html>`. The theme-aware tokens switch automatically; use the `dark:` variant only when needed.
- Add `reveal` to an element to fade it in on scroll.
