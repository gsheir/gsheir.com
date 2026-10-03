// Permanent redirects from the old Django URLs. Used to generate both the Caddy
// config (Railway) and a `_redirects` file (Cloudflare), and validated at build time.
export const redirects: Record<string, string> = {
  "/about_me/": "/about/",
  "/blog/arsenal_press_part_1/": "/blog/arsenal-press-part-1/",
  "/blog/arsenal_press_part_2/": "/blog/arsenal-press-part-2/",
  "/blog/arsenal_corners_part_1/": "/blog/arsenal-corners-part-1/",
  "/blog/arsenal_corners_part_2/": "/blog/arsenal-corners-part-2/",
  "/blog/fantasy_football/": "/blog/fantasy-football/",
};
