import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {createHash} from 'node:crypto';
import {foodProducts,foodCategories} from '../js/arirang-data.mjs';import {foodImage,foodCategoryImage} from '../js/arirang-images.mjs';
test('all food image routes resolve to local source-matched assets with AI attribution',()=>{
 const manifest=JSON.parse(readFileSync('assets/arirang-images/sources.json','utf8'));const paths=new Set(manifest.files.map(f=>f.file));assert.equal(manifest.sourceRepository,'NurionHoldings/thearirang');assert.equal(manifest.files.length,30);
 for(const file of manifest.files){const bytes=readFileSync(file.file);assert.equal(bytes.length,file.bytes);assert.equal(createHash('sha256').update(bytes).digest('hex'),file.sha256);assert.equal(createHash('sha1').update(Buffer.concat([Buffer.from('blob '+bytes.length+'\0'),bytes])).digest('hex'),file.gitBlob);assert.equal(bytes.subarray(8,12).toString(),'WEBP');}
 for(const p of foodProducts){assert(Object.hasOwn(manifest.products,p.art),p.id);const html=foodImage(p.art);assert(paths.has(html.match(/src="([^"]+)"/)[1]));assert(html.includes('AI 생성 대표 이미지'));assert(!html.includes('<svg'));assert.equal(p.executable,false);}
 for(const c of foodCategories.filter(c=>c.id!=='processed'))assert(paths.has(foodCategoryImage(c.id).match(/src="([^"]+)"/)[1]));
 assert(foodImage('arbitrary-path').includes('/grains--rice-retail-v2.webp'));
});
