import { getCollection, type CollectionEntry } from "astro:content";

export type Post = CollectionEntry<"blog">;

const wordsPerMinute = 220;

/** Published posts, newest first. Later parts of a series come first on the same day. */
export async function getPosts(): Promise<Post[]> {
  const posts = await getCollection("blog", ({ data }) => import.meta.env.DEV || !data.draft);
  return posts.sort(
    (a, b) =>
      b.data.pubDate.valueOf() - a.data.pubDate.valueOf() || (b.data.series?.part ?? 0) - (a.data.series?.part ?? 0),
  );
}

export const postUrl = (post: Post) => `/blog/${post.id}/`;

export function readingTime(body = "") {
  const words = body
    .replace(/[#*_>`\[\]()!-]/g, " ")
    .split(/\s+/)
    .filter(Boolean).length;
  return Math.max(1, Math.round(words / wordsPerMinute));
}

const dateFormats = {
  long: { day: "numeric", month: "long", year: "numeric" },
  short: { day: "2-digit", month: "short", year: "numeric" },
  month: { month: "long", year: "numeric" },
} satisfies Record<string, Intl.DateTimeFormatOptions>;

export const formatDate = (date: Date, style: keyof typeof dateFormats = "long") =>
  date.toLocaleDateString("en-GB", dateFormats[style]);
