import test from 'node:test';
import assert from 'node:assert/strict';
import {taxonomy,categorySelection,categoryTrail,categoryURL,productInCategory,productCategoryPath} from '../js/taxonomy.mjs';
import {listings} from '../js/catalog.mjs';
import {menswearState,filterMenswear} from '../js/menswear-data.mjs';
import {menswearRoute} from '../js/menswear-routing.mjs';
const selection=q=>categorySelection(new URLSearchParams(q));
test('taxonomy has exactly three merchandise levels and unique sibling IDs',()=>{
 assert.equal(taxonomy.length,12);
 function unique(nodes){assert.equal(new Set(nodes.map(x=>x.id)).size,nodes.length);}
 unique(taxonomy);
 for(const root of taxonomy){assert(root.children.length);unique(root.children);for(const middle of root.children){assert(middle.children.length);unique(middle.children);for(const leaf of middle.children){assert(leaf.name);assert.equal(leaf.children,undefined);}}}
 assert.deepEqual(categoryTrail(selection('major=menswear&middle=pants&minor=slacks')).map(x=>x.name),['남성복','바지','슬랙스']);
 assert.deepEqual(categoryTrail(selection('major=footwear&middle=sneakers&minor=running')).map(x=>x.name),['신발','운동화','러닝화']);
});
test('all 23 existing sample products have valid leaf paths and single primary placement',()=>{
 assert.equal(listings.length,23);
 for(const p of listings){const path=productCategoryPath(p);assert.equal(path.length,3,p.id);const s={major:path[0],middle:path[1],minor:path[2]};assert.equal(categoryTrail(s).length,3,p.id);assert(productInCategory(p,s));assert.equal(taxonomy.filter(root=>productInCategory(p,{major:root.id})).length,1);}
});
test('changing a parent removes mismatched child selections',()=>{
 assert.deepEqual(selection('major=footwear&middle=pants&minor=slacks'),{major:'footwear',middle:'',minor:''});
 assert.deepEqual(selection('major=menswear&middle=pants&minor=oxford'),{major:'menswear',middle:'pants',minor:''});
 assert.deepEqual(selection('major=unknown&middle=pants'),{major:'',middle:'',minor:''});
});
test('middle and leaf filters persist across category, vendor, and sample URLs',()=>{
 const q=new URLSearchParams('major=menswear&middle=pants&minor=slacks');
 assert.equal(menswearRoute('#/menswear/clothing?'+q).canonical,'#/menswear/clothing?'+q);
 assert.deepEqual(filterMenswear(menswearState(q)).map(p=>p.id),['p-men-trousers']);
 q.set('middle','shirts');q.set('minor','oxford');assert.deepEqual(filterMenswear(menswearState(q)).map(p=>p.id),['p-men-shirt']);
 const url=categoryURL(selection('major=menswear&middle=suits&minor=two-piece'),'#/menswear/clothing/vendor/top-gun',new URLSearchParams('q=navy'));
 assert(url.includes('middle=suits')&&url.includes('minor=two-piece')&&url.includes('q=navy'));
});
