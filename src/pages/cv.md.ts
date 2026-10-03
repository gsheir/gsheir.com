import type { APIRoute } from "astro";
import { getEntry } from "astro:content";

import { markdownResponse } from "../lib/markdown-response";
import { absoluteLinks } from "../lib/posts";

export const GET: APIRoute = async ({ site }) => {
  const cv = await getEntry("pages", "cv");
  if (!cv) throw new Error("Missing src/content/pages/cv.md");
  const { name, summary } = cv.data;
  return markdownResponse(`# ${name}\n\n${summary ?? ""}\n\n${absoluteLinks(cv.body ?? "", site!.href).trim()}\n`);
};
