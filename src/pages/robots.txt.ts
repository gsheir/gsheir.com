import type { APIRoute } from "astro";

import { textResponse } from "../lib/markdown-response";

export const GET: APIRoute = ({ site }) =>
  textResponse(`User-agent: *\nAllow: /\n\nSitemap: ${new URL("/sitemap-index.xml", site)}\n`);
