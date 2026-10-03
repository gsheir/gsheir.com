import { unified } from "@astrojs/markdown-remark";
import mdx from "@astrojs/mdx";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "astro/config";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypeExternalLinks from "rehype-external-links";
import rehypeSlug from "rehype-slug";
import { remarkAlert } from "remark-github-blockquote-alert";

import siteChecks from "./src/integrations/site-checks";
import rehypeFigures from "./src/plugins/rehype-figures";

export default defineConfig({
  site: "https://gsheir.com",
  trailingSlash: "ignore",
  integrations: [mdx(), siteChecks()],
  markdown: {
    processor: unified({
      remarkPlugins: [remarkAlert],
      rehypePlugins: [
        rehypeSlug,
        [rehypeAutolinkHeadings, { behavior: "wrap", properties: { className: ["heading-link"] } }],
        [rehypeExternalLinks, { target: "_blank", rel: ["noopener", "noreferrer"] }],
        rehypeFigures,
      ],
    }),
    shikiConfig: { themes: { light: "github-light", dark: "github-dark" } },
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
