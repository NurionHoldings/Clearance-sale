import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { categoryPhotos, productPhotos, photo } from '../js/photo-library.mjs';
import { taxonomy } from '../js/taxonomy.mjs';
import { listings } from '../js/catalog.mjs';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = p => readFileSync(resolve(root,p),'utf8');
const lesson = JSON.parse(read('intent_DNA/lessons/shopping-content-2026-11-01.json'));
assert.equal(lesson.schema_version, 'dapanda.repository-lesson/v1');
assert.equal(lesson.adoption, 'repository_guidance_and_ci');
assert(['not_connected','receipt_verified'].includes(lesson.runtime_ingestion));
if(lesson.runtime_ingestion === 'receipt_verified') assert(lesson.runtime_receipt, '실행 엔진 수신 근거가 필요합니다.');
assert.equal(lesson.model_training,'not_performed');
assert.equal(lesson.improvement_claim,'not_evaluated');
for(const item of lesson.lessons){
 assert(item.problem && item.rule && item.evidence.length, '교훈별 원인·규칙·근거가 필요합니다.');
 for(const p of [...item.implementation,...item.checks]) assert(existsSync(resolve(root,p)), `학습 근거 파일 누락: ${p}`);
 for(const e of item.evidence) assert(/^https:\/\/github.com\/NurionHoldings\/Clearance-sale\/pull\/\d+$/.test(e.pr) && /^[a-f0-9]{40}$/.test(e.merge_commit));
}
const sources = JSON.parse(read('assets/photos/sources.json')).photos;
const keys = new Set();
for(const item of sources){
 assert(!keys.has(item.key),`사진 키 중복: ${item.key}`);keys.add(item.key);
 assert(/^https:\/\/www.pexels.com\/photo\/\d+\/$/.test(item.source),`원본 출처 확인 필요: ${item.key}`);
 assert.equal(item.license,'https://www.pexels.com/license/');
 assert.equal(item.file,`assets/photos/${item.key}.webp`);
 assert(existsSync(resolve(root,item.file)),`사진 파일 누락: ${item.file}`);
 assert(photo(item.key).includes(item.file),`사진 렌더링 연결 누락: ${item.key}`);
}
for(const [id,key] of Object.entries(categoryPhotos)){
 assert(taxonomy.some(c=>c.id===id),`알 수 없는 대분류: ${id}`);
 assert(keys.has(key),`대분류 이미지 출처 누락: ${key}`);
}
for(const [id,key] of Object.entries(productPhotos)){
 assert(listings.some(p=>p.id===id),`알 수 없는 상품: ${id}`);
 assert(keys.has(key),`상품 이미지 출처 누락: ${key}`);
}
assert(read('AGENTS.md').includes('shopping-content-2026-11-01.json'));
assert(read('js/app.js').includes('연출 이미지 · 예시'), '홈 연출 이미지 표시 누락');
assert(read('js/menswear-page.js').includes('실제 판매 상품·입점 브랜드의 촬영 자료가 아닙니다.'), '상세 연출 고지 누락');
console.log(`ARKAON repository lessons PASS: ${lesson.lessons.length} lessons; ${keys.size} sourced photos; runtime ingestion=${lesson.runtime_ingestion}; model training=${lesson.model_training}`);
