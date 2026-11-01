import test from 'node:test';
import assert from 'node:assert/strict';
import {foodCategories,foodProducts,foodState,filteredFood,normalizeBasket,basketSummary} from '../js/arirang-data.mjs';
import {categoryTrail} from '../js/taxonomy.mjs';
import {MAX_PRODUCTS_PER_VENDOR} from '../js/capacity.mjs';
test('food examples are separate, classified to a valid leaf, non-executable and within seller limit',()=>{
 assert.equal(foodProducts.length,18);assert.equal(foodCategories.filter(c=>c.id!=='processed').length,12);assert.equal(new Set(foodProducts.map(p=>p.id)).size,18);
 for(const p of foodProducts){assert.equal(categoryTrail({major:p.categoryPath[0],middle:p.categoryPath[1],minor:p.categoryPath[2]}).length,3);assert.equal(p.executable,false);assert(Number.isSafeInteger(p.price)&&p.price>0);assert(Number.isSafeInteger(p.stock)&&p.stock>=0);}
 assert(foodProducts.length<=MAX_PRODUCTS_PER_VENDOR);
});
test('category, leaf, search, availability and sorting combine without mutating examples',()=>{
 const state=foodState(new URLSearchParams('middle=fruit&minor=apples&q=사과&stock=1&sort=price-asc'));assert.deepEqual(filteredFood(state).map(p=>p.id),['ar-apple']);
 assert.equal(foodState(new URLSearchParams('middle=dairy&minor=apples')).classification.minor,'');assert.equal(filteredFood(foodState(new URLSearchParams('stock=1'))).length,17);
 const original=foodProducts.map(p=>p.id);const rows=filteredFood(foodState(new URLSearchParams('sort=price-asc')));assert(rows.every((p,i)=>!i||p.price>=rows[i-1].price));assert.deepEqual(foodProducts.map(p=>p.id),original);
});
test('basket rejects corrupt and unknown lines, clamps stock and computes exact totals',()=>{
 assert.deepEqual(normalizeBasket([]),{});assert.deepEqual(normalizeBasket({unknown:3,'ar-apple':99,'ar-yogurt':2,'ar-water':-1,'ar-bread':1.5,'ar-eggs':'2'}),{'ar-apple':8});assert.deepEqual(basketSummary({'ar-apple':2,'ar-water':3}),{count:5,total:22500,lines:2});assert.deepEqual(basketSummary(null),{count:0,total:0,lines:0});
});
