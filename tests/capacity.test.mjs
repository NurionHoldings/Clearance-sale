import test from 'node:test';
import assert from 'node:assert/strict';
import {MAX_VENDORS,MAX_PRODUCTS_PER_VENDOR,vendorSlots,applicationError,draftError} from '../js/capacity.mjs';
const known=[{id:'existing',name:'기존 업체'}];
const apps=n=>Array.from({length:n},(_,i)=>({id:'v'+i,name:'업체'+i,status:i%2?'approved':'pending'}));
test('100 vendor slots include existing, approved and pending; rejected slots are returned',()=>{
 assert.equal(MAX_VENDORS,100);assert.equal(vendorSlots(known,apps(98)),1);assert.equal(applicationError(known,apps(98),'신규'), '');assert.match(applicationError(known,apps(99),'신규'),/100/);
 const rows=apps(99);rows[0].status='rejected';assert.equal(vendorSlots(known,rows),1);assert.equal(applicationError(known,rows,rows[0].name,rows[0].id),'');rows.push({id:'new',name:'새 업체',status:'pending'});assert.match(applicationError(known,rows,rows[0].name,rows[0].id),/100/);
 assert.match(applicationError(known,[], '기존업체'),/이미/);
});
test('50 products per vendor independent of inventory, drafts count and deletion restores a slot',()=>{
 assert.equal(MAX_PRODUCTS_PER_VENDOR,50);const vendors=[{id:'a'},{id:'b'}];const draft={sellerId:'a',title:'상품',price:1000,quantity:100000};
 const rows=Array.from({length:49},()=>({sellerId:'a',status:'draft'}));assert.equal(draftError(vendors,rows,draft),'');rows.push(draft);assert.match(draftError(vendors,rows,draft),/50/);assert.equal(draftError(vendors,rows,{...draft,sellerId:'b'}),'');rows.pop();assert.equal(draftError(vendors,rows,draft),'');assert.match(draftError([],[],draft),/승인/);
 for(const changes of [{price:NaN},{price:1.5},{quantity:-1},{quantity:Infinity},{title:' '}])assert(draftError(vendors,[],{...draft,...changes}));
});
