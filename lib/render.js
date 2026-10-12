import { readFileSync } from "node:fs";

const read = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf8"));

const themes = {
  mizuki: read("../themes/mizuki.json"),
};
// "Visitors" in Klee One, as an outline path in em units (baseline at y=0)
const label = read("./label.json");

export const THEMES = Object.keys(themes);

// Sprites sit almost side by side, overlapping only a touch.
const STEP = 0.92;
const LABEL_SIZE = 34;
const LABEL_GAP = 26;
const LABEL_COLOR = { light: "#7a84a0", dark: "#8d95b0" };

/**
 * @param {number} count
 * @param {object} opts
 * @param {string} [opts.theme]      theme name
 * @param {boolean} [opts.dark]      dim slightly for dark pages
 * @param {number} [opts.minDigits]  pad with leading zeros up to this many digits
 * @param {boolean} [opts.label]     write "Visitors" to the left
 * @param {number} [opts.padRight]   transparent margin on the right, in sprite pixels
 */
export function renderCounter(count, { theme = "mizuki", dark = false, minDigits = 5, label: withLabel = false, padRight = 0 } = {}) {
  const t = themes[theme] ?? themes.mizuki;
  const digits = String(count).padStart(minDigits, "0");
  const step = Math.round(t.width * STEP);
  const left = withLabel ? Math.ceil(label.advance * LABEL_SIZE + LABEL_GAP) : 0;
  const width = left + step * (digits.length - 1) + t.width + padRight;

  const used = [...new Set(digits)];
  const defs = used
    .map((d) => `<image id="d${d}" width="${t.width}" height="${t.height}" href="${t.digits[d]}"/>`)
    .join("");
  const uses = [...digits].map((d, i) => `<use href="#d${d}" x="${left + i * step}"/>`).join("");
  const text = withLabel
    ? `<path transform="translate(0 ${t.cardY + (label.capHeight * LABEL_SIZE) / 2}) scale(${LABEL_SIZE})" fill="${LABEL_COLOR[dark ? "dark" : "light"]}" d="${label.d}"/>`
    : "";
  const style = dark ? "<style>.s{filter:brightness(.88)}</style>" : "";

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${t.height}" width="${width}" height="${t.height}" role="img" aria-label="${count} visitors">
<title>${count} visitors</title>${style}
<defs>${defs}</defs>${text}<g class="s">${uses}</g>
</svg>`;
}
