import type { APIRoute, GetStaticPaths } from "astro";

import { markdownResponse } from "../../lib/markdown-response";
import { getPosts, postToMarkdown, type Post } from "../../lib/posts";

export const getStaticPaths = (async () => {
  const posts = await getPosts();
  return posts.map((post) => ({ params: { slug: post.id }, props: { post } }));
}) satisfies GetStaticPaths;

export const GET: APIRoute<{ post: Post }> = ({ props, site }) =>
  markdownResponse(postToMarkdown(props.post, site!.href));
