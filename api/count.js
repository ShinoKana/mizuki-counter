import { Redis } from "@upstash/redis";
import { renderCounter, THEMES } from "../lib/render.js";

// Upstash Redis via the Vercel marketplace (KV_REST_API_*) or Upstash's own
// variable names. The kana-counter.vercel.app instance shares a free store
// with other projects, so it only touches keys under "kana-counter:" and
// never flushes or scans the database.
const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL ?? process.env.KV_REST_API_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN ?? process.env.KV_REST_API_TOKEN,
});

const NAME = /^[A-Za-z0-9_.-]{1,39}$/;

const list = (value) => (value ?? "").split(",").map((s) => s.trim()).filter(Boolean);

// ALLOWED_NAMES="alice,bob" limits which counters this deployment keeps;
// leave it unset to count any name.
const ALLOWED = new Set(list(process.env.ALLOWED_NAMES));

// COUNTER_START="alice:4008" carries a count over from an older counter.
// It is applied once, the first time that name is counted.
const START = Object.fromEntries(list(process.env.COUNTER_START).map((p) => p.split(":")).map(([n, v]) => [n, Number(v)]));

const lastSeen = new Map(); // shown if the database can't be reached

async function count(name, peek) {
  const key = `kana-counter:${name}`;
  if (peek) return Number((await redis.get(key)) ?? START[name] ?? 0);
  let n = await redis.incr(key);
  if (n === 1 && START[name]) {
    n = START[name] + 1;
    await redis.set(key, n);
  }
  return n;
}

const clamp = (value, lo, hi, fallback) => {
  if (value === null || value === "") return fallback;
  const n = Number(value);
  return Number.isFinite(n) ? Math.min(Math.max(Math.round(n), lo), hi) : fallback;
};

const svgResponse = (svg, status = 200) =>
  new Response(svg, {
    status,
    headers: {
      "content-type": "image/svg+xml; charset=utf-8",
      // GitHub's image proxy must ask again on every page view
      "cache-control": "max-age=0, no-cache, no-store, must-revalidate",
    },
  });

export async function GET(request) {
  const params = new URL(request.url).searchParams;
  const options = {
    theme: THEMES.includes(params.get("theme")) ? params.get("theme") : THEMES[0],
    dark: params.get("dark") === "1",
    minDigits: clamp(params.get("digits"), 1, 10, 5),
    label: params.get("label") === "1",
    padRight: clamp(params.get("pad"), 0, 400, 0),
  };

  // ?demo=1234 draws that number without touching the database
  if (params.has("demo")) {
    return svgResponse(renderCounter(clamp(params.get("demo"), 0, 9999999999, 0), options));
  }

  const name = params.get("name") ?? "";
  if (!NAME.test(name)) {
    return new Response("name must be 1-39 letters, digits, '.', '_' or '-'", { status: 400 });
  }
  if (ALLOWED.size && !ALLOWED.has(name)) {
    return new Response("this deployment only keeps counters for its owner; deploy your own copy (see the README)", {
      status: 403,
    });
  }

  let n;
  try {
    // ?peek=1 shows the number without counting a visit
    n = await count(name, params.get("peek") === "1");
    lastSeen.set(name, n);
  } catch (err) {
    console.error("counter store unavailable:", err);
    n = lastSeen.get(name) ?? START[name] ?? 0;
  }
  return svgResponse(renderCounter(n, options));
}
