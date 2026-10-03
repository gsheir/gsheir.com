import type { Element, ElementContent, Root } from "hast";
import { visit } from "unist-util-visit";

const isWhitespace = (node: ElementContent) =>
  (node.type === "text" && !node.value.trim()) || (node.type === "element" && node.tagName === "br");

/**
 * Turns a paragraph containing only images into a <figure>.
 *
 * - An italic line directly under the image(s) becomes the <figcaption>.
 * - Images written on the same line sit side by side; images on separate lines stack.
 */
export default function rehypeFigures() {
  return (tree: Root) => {
    visit(tree, "element", (node, index, parent) => {
      if (node.tagName !== "p" || index === undefined || !parent) return;

      const children = [...node.children];
      const meaningful = children.filter((child) => !isWhitespace(child));
      const last = meaningful.at(-1);
      const caption = last?.type === "element" && last.tagName === "em" ? last : undefined;
      const images = caption ? meaningful.slice(0, -1) : meaningful;

      if (!images.length || !images.every((child) => child.type === "element" && child.tagName === "img")) return;

      for (const image of images as Element[]) {
        image.properties.loading = "lazy";
        image.properties.decoding = "async";
      }

      const captionIndex = caption ? children.indexOf(caption) : children.length;
      const sideBySide =
        images.length > 1 &&
        !children
          .slice(0, captionIndex)
          .some(
            (child) =>
              (child.type === "text" && child.value.includes("\n")) ||
              (child.type === "element" && child.tagName === "br"),
          );

      const figure: Element = {
        type: "element",
        tagName: "figure",
        properties: sideBySide ? { className: ["figure-row"] } : {},
        children: [...(images as Element[])],
      };
      if (caption) {
        figure.children.push({ type: "element", tagName: "figcaption", properties: {}, children: caption.children });
      }

      parent.children[index] = figure;
    });
  };
}
