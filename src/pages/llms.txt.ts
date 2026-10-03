import type { APIRoute } from "astro";

import { textResponse } from "../lib/markdown-response";
import { getPosts, isoDate, postMarkdownUrl } from "../lib/posts";
import { site } from "../lib/site";

export const GET: APIRoute = async ({ site: siteUrl }) => {
  const posts = await getPosts();
  const url = (path: string) => new URL(path, siteUrl).href;
  const lines = [
    `# ${site.name}`,
    "",
    `> ${site.description}`,
    "",
    "Every page below is available as Markdown. The full text of all posts is at " + url("/llms-full.txt") + ".",
    "",
    "## Blog posts",
    "",
    ...posts.map(
      (post) =>
        `- [${post.data.title}](${url(postMarkdownUrl(post))}): ${post.data.description} (${isoDate(post.data.pubDate)})`,
    ),
    "",
    "## About",
    "",
    `- [CV](${url("/cv.md")}): Experience, education, projects, and technologies`,
    `- [GitHub](${site.links.github})`,
    `- [LinkedIn](${site.links.linkedin})`,
    "",
  ];
  return textResponse(lines.join("\n"));
};
