/** Offline source contract checks for the operator's static and animated logo.
 * Run: node scripts/check-asia-logo.mjs
 * This does not assert browser rendering or production readiness.
 */
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
const read = (path) => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
const svg = read('assets/asia-holdings-logo.svg');
const motion = read('asia-holdings-logo-demo.html');
const home = read('index.html');
assert.match(svg, /<svg\b[^>]*viewBox="0 0 700 580"/);
assert.match(svg, /ASIA HOLDINGS/);
assert.match(svg, /<circle[^>]*cx="390"[^>]*cy="340"/);
assert.match(svg, /linearGradient id="gold"/);
assert.match(motion, /meta name="robots" content="noindex,nofollow"/);
assert.match(motion, /prefers-reduced-motion:reduce/);
assert.match(motion, /id="intro"/);
assert.match(motion, /id="play"/);
assert.match(motion, /id="replay"/);
assert.match(motion, /id="level"/);
assert.match(motion, /clearTimeout\(introTimer\)/);
assert.match(motion, /@media\(max-width:600px\)/);
assert.match(home, /운영사: \(주\)아시아홀딩스/);
assert.match(home, /assets\/asia-holdings-logo\.svg/);
assert.match(home, /asia-holdings-logo-demo\.html/);
console.log('Asia Holdings logo source contracts: OK');
