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

export const postMarkdownUrl = (post: Post) => `/blog/${post.id}.md`;

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

export const isoDate = (date: Date) => date.toISOString().slice(0, 10);

/** Raw Markdown for a post, with a header so the file stands on its own. */
export function postToMarkdown(post: Post, siteUrl: string) {
  const { title, description, pubDate, updatedDate, series } = post.data;
  const lines = [
    `# ${title}`,
    "",
    `> ${description}`,
    "",
    `- Author: Geoffrey Sheir`,
    `- Published: ${isoDate(pubDate)}`,
    ...(updatedDate ? [`- Updated: ${isoDate(updatedDate)}`] : []),
    ...(series ? [`- Series: ${series.name} (part ${series.part})`] : []),
    `- Source: ${new URL(postUrl(post), siteUrl)}`,
    "",
    absoluteLinks(post.body ?? "", siteUrl).trim(),
    "",
  ];
  return lines.join("\n");
}

/** Makes root-relative Markdown links absolute, so copied Markdown still works elsewhere. */
export const absoluteLinks = (markdown: string, siteUrl: string) =>
  markdown.replace(/\]\((\/[^)\s]*)\)/g, (_, path: string) => `](${new URL(path, siteUrl)})`);
