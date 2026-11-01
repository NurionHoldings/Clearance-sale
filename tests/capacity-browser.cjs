const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('node:assert/strict'),os=require('os');
const projectRoot=path.resolve(__dirname,'..');
(async()=>{
 const server=http.createServer((req,res)=>{const name=decodeURIComponent(new URL(req.url,'http://local').pathname);const file=path.join(projectRoot,name==='/'?'index.html':name);res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.woff2':'font/woff2','.svg':'image/svg+xml','.png':'image/png'})[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).on('error',()=>{res.statusCode=404;res.end()}).pipe(res)});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const url='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({headless:true,...(process.env.DAPANDA_CHROMIUM_EXECUTABLE?{executablePath:process.env.DAPANDA_CHROMIUM_EXECUTABLE}:{})});

 const page=await browser.newPage({viewport:{width:390,height:940},reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url+'/#/seller');await page.evaluate(()=>{localStorage.setItem('clearance-demo-apps',JSON.stringify(Array.from({length:96},(_,i)=>({id:'v'+i,name:'체험업체'+i,type:'제조사',status:'approved',createdAt:new Date().toISOString()}))))});await page.reload();
 await page.locator('#sellerForm [name=name]').fill('마지막업체');await page.locator('#sellerForm [type=submit]').click();assert((await page.locator('#seller [data-vendor-capacity]').innerText()).includes('남은 정원 0개'));
 await page.locator('#sellerForm [name=name]').fill('초과업체');await page.locator('#sellerForm [type=submit]').click();assert((await page.locator('#sellerStatus').innerText()).includes('100개'));
 await page.goto(url+'/#/manage');await page.locator('#draftForm').waitFor({state:'visible'});await page.locator('#draftForm [name=sellerId]').selectOption('v0');
 await page.evaluate(()=>localStorage.setItem('dapanda-product-drafts-v1',JSON.stringify(Array.from({length:49},(_,i)=>({id:'d'+i,sellerId:'v0',title:'초안'+i,price:100,quantity:5,status:'draft'})))));await page.reload();
 await page.locator('#draftForm [name=title]').fill('50번째 상품');await page.locator('#draftForm [name=price]').fill('1000');await page.locator('#draftForm [name=quantity]').fill('999');await page.locator('#draftForm [type=submit]').click();assert.equal(await page.locator('#draftList li').count(),50);assert(await page.locator('#draftForm [type=submit]').isDisabled());assert((await page.locator('#draftUsage').innerText()).includes('남은 등록 0개'));
 await page.locator('#draftList button').last().click();assert.equal(await page.locator('#draftList li').count(),49);assert.equal(await page.locator('#draftForm [type=submit]').isDisabled(),false);await page.locator('#draftForm [name=sellerId]').selectOption('v1');assert.equal(await page.locator('#draftList li').count(),0);assert((await page.locator('#draftUsage').innerText()).includes('남은 등록 50개'));
 for(const width of [320,390,768,1440]){await page.setViewportSize({width,height:940});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));}
 assert.deepEqual(errors,[]);console.log('PASS vendor 100/101 boundary; product 49/50 boundary; deletion; per-vendor separation; responsive widths');await browser.close();server.close();
})().catch(e=>{console.error(e);process.exit(1)});
