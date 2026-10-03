import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { AstroIntegration } from "astro";

import { redirects } from "../redirects";

const withoutSlash = (p: string) => (p.length > 1 ? p.replace(/\/$/, "") : p);

async function walk(dir: string): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = await Promise.all(
    entries.map((entry) => (entry.isDirectory() ? walk(path.join(dir, entry.name)) : [path.join(dir, entry.name)])),
  );
  return files.flat();
}

async function exists(outDir: string, urlPath: string) {
  const clean = decodeURIComponent(urlPath.split(/[?#]/)[0]);
  const candidates = [clean, path.join(clean, "index.html"), `${clean}.html`];
  for (const candidate of candidates) {
    try {
      if ((await fs.stat(path.join(outDir, candidate))).isFile()) return true;
    } catch {}
  }
  return false;
}

/**
 * After the build:
 * - writes redirects for Caddy (`redirects.caddy`, outside dist) and Cloudflare (`dist/_redirects`)
 * - fails the build if a redirect target or an internal link points at a page that does not exist
 */
export default function siteChecks(): AstroIntegration {
  return {
    name: "site-checks",
    hooks: {
      "astro:build:done": async ({ dir, logger }) => {
        const outDir = fileURLToPath(dir);
        const errors: string[] = [];

        for (const [from, to] of Object.entries(redirects)) {
          if (!(await exists(outDir, to))) errors.push(`Redirect target does not exist: ${from} -> ${to}`);
          if (await exists(outDir, from)) errors.push(`Redirect source is also a real page: ${from}`);
        }

        const cloudflare = Object.entries(redirects).flatMap(([from, to]) => [
          `${from} ${to} 301`,
          `${withoutSlash(from)} ${to} 301`,
        ]);
        await fs.writeFile(path.join(outDir, "_redirects"), cloudflare.join("\n") + "\n");

        const caddy = Object.entries(redirects).map(
          ([from, to]) => `redir ${withoutSlash(from)} ${to} permanent\nredir ${from} ${to} permanent`,
        );
        await fs.writeFile(path.join(outDir, "..", "redirects.caddy"), caddy.join("\n") + "\n");

        const htmlFiles = (await walk(outDir)).filter((file) => file.endsWith(".html"));
        for (const file of htmlFiles) {
          const html = await fs.readFile(file, "utf8");
          for (const [, href] of html.matchAll(/\shref="(\/[^"]*)"/g)) {
            if (href.startsWith("//") || href === "/") continue;
            const target = href.split("#")[0];
            if (!target || (await exists(outDir, target)) || withoutSlash(target) + "/" in redirects) continue;
            errors.push(`Broken internal link in ${path.relative(outDir, file)}: ${href}`);
          }
        }

        if (errors.length) {
          errors.forEach((error) => logger.error(error));
          throw new Error(`${errors.length} site check(s) failed`);
        }
        logger.info(`Checked ${htmlFiles.length} pages and ${Object.keys(redirects).length} redirects`);
      },
    },
  };
}
