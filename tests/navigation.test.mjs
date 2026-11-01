import test from 'node:test';
import assert from 'node:assert/strict';
import {productDetailURL,marketReturnURL,menswearStepURLs} from '../js/navigation.mjs';
test('product detail and close preserve the validated category and search',()=>{
 const url=productDetailURL('p-cap',{major:'accessories',middle:'hats',minor:'baseball'},'야구모자');assert(url.startsWith('#/product/p-cap?'));
 const query=new URLSearchParams(url.split('?')[1]);assert.equal(marketReturnURL(query),'#/market?q='+encodeURIComponent('야구모자')+'&major=accessories&middle=hats&minor=baseball');assert.equal(marketReturnURL(new URLSearchParams('major=unknown&middle=hats&minor=x&q=  ')),'#/market');
});
test('three hierarchy steps lead to their own category depth',()=>{
 const urls=menswearStepURLs({major:'menswear',middle:'pants',minor:'slacks'});assert.equal(urls[0],'#/menswear');assert.equal(urls[1],'#/menswear/clothing?major=menswear&middle=pants');assert.equal(urls[2],'#/menswear/clothing?major=menswear&middle=pants&minor=slacks');
});
