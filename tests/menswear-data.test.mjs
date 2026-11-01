import test from 'node:test';
import assert from 'node:assert/strict';
import { menswearListings, menswearVendors, menswearState, filterMenswear } from '../js/menswear-data.mjs';
import { availableQty, freezeOrderSnapshot, inventoryConsistent } from '../js/catalog.mjs';
const state=q=>menswearState(new URLSearchParams(q));
test('real vendor names are kept separate from fictional catalog sellers',()=>{
 assert.deepEqual(menswearVendors.map(v=>v.name),['비버리힐스 폴로','이원재','TOP GUN']);
 for(const v of menswearVendors)assert.equal(filterMenswear(state('vendor='+v.id)).length,0);
 assert.equal(filterMenswear(state('')).length,6);
});
test('combined filters, price boundaries and stock follow the displayed labels',()=>{
 assert.deepEqual(filterMenswear(state('kind=셔츠&price=under30')).map(p=>p.id),['p-men-shirt']);
 assert.equal(filterMenswear(state('kind=아우터&price=under30')).length,0);
 assert.equal(filterMenswear(state('stock=1')).length,5);
 assert.deepEqual(filterMenswear(state('q=포레스트')).map(p=>p.id),['p-men-cardigan']);
 assert(filterMenswear(state('price=30to50')).every(p=>p.price>=30000&&p.price<50000));
});
test('sort and invalid query normalization do not mutate the catalog',()=>{
 const ids=menswearListings.map(p=>p.id);
 const ascending=filterMenswear(state('sort=price-asc')).map(p=>p.price);
 assert.deepEqual(ascending,[24000,29000,32000,35000,39000,69000]);
 assert.deepEqual(filterMenswear(state('sort=price-desc')).map(p=>p.price),[...ascending].reverse());
 const discount=filterMenswear(state('sort=discount')).map(p=>1-p.price/p.listPrice);
 assert(discount.every((n,i)=>i===0||n<=discount[i-1]));
 assert.deepEqual(menswearListings.map(p=>p.id),ids);
 assert.equal(state('vendor=unknown&kind=unknown&price=bad&sort=bad').vendor,'all');
 assert.equal(state('kind=unknown').kind,'전체');
});
test('sample detail selections never reserve inventory or create executable orders',()=>{
 for(const p of menswearListings){assert(inventoryConsistent(p));const before=structuredClone(p);const snap=freezeOrderSnapshot(p);assert.equal(snap.executable,false);assert.equal(snap.inventoryEffect,'none');assert.deepEqual(p,before);}
 assert.equal(availableQty(menswearListings.find(p=>p.id==='p-men-cardigan')),0);
});

import { menswearRoute, menswearVendorPath } from '../js/menswear-routing.mjs';
test('hierarchy routes separate parent, child, vendor and individual product',()=>{
 assert.equal(menswearRoute('#/menswear').level,'collection');
 assert.equal(menswearRoute('#/menswear/clothing').level,'category');
 for(const vendor of menswearVendors){const r=menswearRoute(menswearVendorPath(vendor.id));assert.equal(r.level,'vendor');assert.equal(r.vendorId,vendor.id);assert.equal(r.isSample,undefined);}
 const detail=menswearRoute('#/menswear/clothing/vendor/top-gun/product/example?q=navy');
 assert.equal(detail.level,'product');assert.equal(detail.vendorId,'top-gun');assert.equal(detail.productId,'example');assert.equal(detail.base,'#/menswear/clothing/vendor/top-gun');
 assert.equal(menswearRoute('#/menswear/samples/product/p-menswear').isSample,true);
});
test('old shared links migrate without assigning sample products to a real vendor',()=>{
 assert.equal(menswearRoute('#/menswear?vendor=top-gun&kind=셔츠').canonical,'#/menswear/clothing/vendor/top-gun?kind=%EC%85%94%EC%B8%A0');
 assert.equal(menswearRoute('#/menswear/product/p-menswear?vendor=top-gun').base,'#/menswear/samples');
 assert.equal(menswearRoute('#/menswear/product/p-menswear').isSample,true);
 assert.doesNotThrow(()=>menswearRoute('#/menswear/clothing/vendor/%broken/product/%broken'));
});
