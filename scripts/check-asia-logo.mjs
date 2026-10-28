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
assert.match(motion, /<img class="logo" src="assets\/asia-holdings-logo\.svg"/);
assert.doesNotMatch(motion, /<svg class="logo"/);
assert.match(motion, /assets\/asia-holdings-logo-cinematic\.png/);
assert.match(motion, /assets\/asia-holdings-logo-hero\.png/);
assert.match(motion, /entryBg/);
assert.match(motion, /세상을 연결하는 가치/);
assert.match(motion, /class="motion-halo"/);
assert.match(motion, /class="logo-wrap"/);
assert.match(motion, /id="intro"/);
assert.match(motion, /id="play"/);
assert.match(motion, /id="replay"/);
assert.match(motion, /id="level"/);
assert.match(motion, /clearTimeout\(introTimer\)/);
assert.match(motion, /@media\(max-width:600px\)/);
assert.match(motion, /id="entryScreen"/);
assert.match(motion, /id="skipEntry"/);
assert.match(motion, /class="entry-screen"/);
assert.match(motion, /entry-active/);
assert.match(motion, /e\.key==='Escape'/);
assert.match(motion, /setTimeout\(closeEntry,120000\)/);
assert.match(motion, /시제품으로 들어가기/);
assert.match(home, /운영사: \(주\)대현산업 플랫폼사업부/);
assert.doesNotMatch(home, /assets\/asia-holdings-logo\.svg/);
assert.doesNotMatch(home, /asia-holdings-logo-demo\.html/);
console.log('Asia Holdings logo source contracts: OK');
