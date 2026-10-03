import type { APIRoute } from "astro";

import { textResponse } from "../lib/markdown-response";
import { getPosts, postToMarkdown } from "../lib/posts";

export const GET: APIRoute = async ({ site }) => {
  const posts = await getPosts();
  return textResponse(posts.map((post) => postToMarkdown(post, site!.href)).join("\n---\n\n"));
};
