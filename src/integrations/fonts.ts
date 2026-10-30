import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { AstroIntegration } from "astro";

/**
 * Switzer's licence forbids redistribution, and this repository is public, so the font files are not
 * committed. They are self-hosted on images.gsheir.com and downloaded into src/assets/fonts (gitignored)
 * before each dev server or build, which then bundles them like any other asset. A file is downloaded
 * only when it is missing or does not match its checksum, so later runs work offline.
 */
const source = "https://images.gsheir.com/fonts/switzer/";
const fonts = [
  { file: "Switzer-Variable.woff2", sha256: "d1bf801ffb1a6096def70a7c532255722ad87d948b13a8a586e342f7091f8ee4" },
  { file: "Switzer-VariableItalic.woff2", sha256: "bf66eb64d539c68c9ebc455e7776cbfcf16cf3cae8b57ce1930e0f0f6ab32a49" },
];
const fontsDir = fileURLToPath(new URL("../assets/fonts/", import.meta.url));

const sha256 = (data: Uint8Array) => createHash("sha256").update(data).digest("hex");

async function ensureFont({ file, sha256: expected }: (typeof fonts)[number]) {
  const target = path.join(fontsDir, file);
  try {
    if (sha256(await fs.readFile(target)) === expected) return false;
  } catch {}
  const response = await fetch(source + file);
  if (!response.ok) throw new Error(`${source + file} returned ${response.status}`);
  const data = new Uint8Array(await response.arrayBuffer());
  if (sha256(data) !== expected) throw new Error(`${source + file} does not match its checksum`);
  await fs.mkdir(fontsDir, { recursive: true });
  await fs.writeFile(target, data);
  return true;
}

export default function selfHostedFonts(): AstroIntegration {
  return {
    name: "self-hosted-fonts",
    hooks: {
      "astro:config:setup": async ({ logger }) => {
        try {
          const downloaded = (await Promise.all(fonts.map(ensureFont))).filter(Boolean).length;
          if (downloaded) logger.info(`Downloaded ${downloaded} font file(s) to src/assets/fonts`);
        } catch (error) {
          throw new Error(
            `Could not download the Switzer font files (${(error as Error).message}). ` +
              "They are needed once; after that they are kept in src/assets/fonts.",
          );
        }
      },
    },
  };
}
