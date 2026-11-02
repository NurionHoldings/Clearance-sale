import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  availableQty,
  discountPct,
  freezeOrderSnapshot,
  inventoryConsistent,
  listings
} from '../js/catalog.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (rel) => readFileSync(join(root, rel), 'utf8');
const fail = [];
const ok = (cond, msg) => { if (!cond) fail.push(msg); };

const html = read('index.html');
const readme = read('README.md');
const robots = read('robots.txt');
const netlify = read('netlify.toml');
const dna = read('intent_DNA/clearance-sale.seed.json');

ok(/<meta name="robots" content="index,follow">/.test(html), '공개 홈 검색 허용 설정이 없습니다.');
ok(!/noindex/.test(html), '공개 홈이 검색 차단되어 있습니다.');
ok(html.includes('https://xn--2j1ba128v.store/'), '대표 주소가 없습니다.');
ok(read('sitemap.xml').includes('<loc>https://xn--2j1ba128v.store/</loc>'), '공개 홈 사이트맵이 없습니다.');
ok(robots.includes('Allow: /$') && robots.includes('Disallow: /') && robots.includes('Sitemap: https://xn--2j1ba128v.store/sitemap.xml'), '공개 홈 허용·내부 경로 차단·사이트맵 설정이 필요합니다.');
ok(!/for = "\/\*"[\s\S]*?X-Robots-Tag/.test(netlify), '전체 검색 차단 헤더가 남아 있습니다.');
for (const path of ['operations.html', 'live.html']) {
  ok(netlify.includes(`for = "/${path}"`) && /noindex/.test(read(path)), `${path}: 내부 화면 검색 차단이 필요합니다.`);
}
ok(/시제품|데모/.test(html) && /주문·결제/.test(html), '데모 고지 문구가 약합니다.');
ok(/다판다/.test(html) && /다판다/.test(readme), '다판다 브랜드 표기가 없습니다.');
ok(/www\.다판다\.store/.test(readme + html) && /www\.다판다\.shop/.test(readme + html), '등록 도메인 안내가 없습니다.');
ok(/assets\/dapanda-symbol\.svg/.test(html), '다판다 심볼이 연결되지 않았습니다.');
ok(!/(지금 구매|결제하기|주문하기|결제 완료|주문 완료|구매 확정)/.test(html), '실제 거래처럼 보이는 구매·결제 문구가 있습니다.');
ok(/Never mark an order paid without verified payment-provider evidence/.test(dna), 'Intent DNA 결제 불변조건이 없습니다.');
ok(/qtyReserved/.test(dna), 'Intent DNA에 재고 예약 불변조건이 없습니다.');

for (const listing of listings) {
  ok(listing.sellerOfRecord && listing.channel && listing.sellerId, `${listing.id}: 판매자 식별이 불완전합니다.`);
  ok(['direct', 'marketplace'].includes(listing.channel), `${listing.id}: channel이 잘못되었습니다.`);
  ok(inventoryConsistent(listing), `${listing.id}: 예약 수량이 보유 재고를 넘습니다.`);
  ok(availableQty(listing) === Math.max(0, listing.qtyOnHand - listing.qtyReserved), `${listing.id}: 판매가능 수량 계산이 틀립니다.`);
  const snap = freezeOrderSnapshot(listing, 1);
  ok(snap.executable === false, `${listing.id}: 스냅샷이 실행 가능으로 표시됩니다.`);
  ok(snap.sellerOfRecord === listing.sellerOfRecord, `${listing.id}: 스냅샷에 법적 판매자가 고정되지 않았습니다.`);
  ok(snap.paymentState === 'not-started', `${listing.id}: 스냅샷이 결제 상태를 가집니다.`);
  ok(snap.inventoryEffect === 'none', `${listing.id}: 스냅샷이 재고를 변경합니다.`);
}

ok(discountPct(100, 200) === 50, '할인율 정상 계산 실패');
ok(discountPct(0, 100) === null, '할인율 가드(0원) 실패');
ok(discountPct(200, 100) === null, '할인율 가드(역전) 실패');

const oversell = freezeOrderSnapshot(listings.find((x) => x.id === 'p-display-microwave'), 1);
ok(oversell.wouldOversell === true, '판매가능 0인 상품의 초과판매 감지가 실패했습니다.');

if (process.env.CLEARANCE_PRODUCTION_RELEASE === '1') {
  fail.push('운영 배포가 요청되었으나 인증, 사업자 검증, PG 웹훅, 재고 원자적 예약·차감, 정산원장, 감사로그, 실명 고지가 미구현입니다.');
}

if (fail.length) {
  console.error('production-gate FAIL');
  for (const item of fail) console.error('- ' + item);
  process.exit(1);
}
console.log('production-gate PASS (demo only; production release stays blocked)');
