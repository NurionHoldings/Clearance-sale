const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('node:assert/strict'),os=require('os');
const projectRoot=path.resolve(__dirname,'..');
(async()=>{
 const server=http.createServer((req,res)=>{const name=decodeURIComponent(new URL(req.url,'http://local').pathname);const file=path.join(projectRoot,name==='/'?'index.html':name);res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.woff2':'font/woff2','.svg':'image/svg+xml','.png':'image/png'})[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).on('error',()=>{res.statusCode=404;res.end()}).pipe(res)});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const url='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({headless:true,...(process.env.DAPANDA_CHROMIUM_EXECUTABLE?{executablePath:process.env.DAPANDA_CHROMIUM_EXECUTABLE}:{})});

 const errors=[];
 for(const width of [320,390,768,1440]){
 const context=await browser.newContext({viewport:{width,height:940},reducedMotion:'reduce'}),page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url+'/#/market');await page.locator(width<=760?'#mobileNav [data-tab=food]':'header [data-view=arirang]').click();await page.locator('#arirang h1').waitFor({state:'visible'});await page.evaluate(()=>document.fonts.ready);
 assert.equal(await page.locator('#marketHero').isVisible(),false);assert.equal(await page.locator('#arirang .ar-category-grid a').count(),12);assert.equal(await page.locator('#arirang .ar-card').count(),18);assert.equal(await page.locator('#arirang [data-ar-add=ar-yogurt]').isDisabled(),true);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 if(width===320||width===390||width===1440)await page.screenshot({path:path.join(os.tmpdir(),'arirang-home-'+width+'.png'),fullPage:true});
 await page.locator('#arRegion').selectOption({label:'서울 강동구'});await page.reload();assert.equal(await page.locator('#arRegion').inputValue(),'서울 강동구');
 await page.locator('.ar-category-grid a').filter({hasText:'과일'}).click();await page.locator('.ar-subcategories a').filter({hasText:'사과'}).click();await page.waitForFunction(()=>document.querySelectorAll('#arirang .ar-card').length===1);
 await page.locator('[data-ar-add=ar-apple]').click();assert.equal(await page.locator('.ar-top [data-ar-count]').innerText(),'1');await page.locator('.ar-card h3 a').click();await page.locator('.ar-detail h1').waitFor();assert((await page.locator('.ar-crumbs').innerText()).includes('과일'));await page.locator('[data-ar-add=ar-apple]').click();await page.locator('.ar-back').click();await page.waitForFunction(()=>document.querySelectorAll('.ar-card').length===1);assert(page.url().includes('minor=apples'));assert.equal(await page.locator('.ar-card').count(),1);
 await page.locator('.ar-basket-link').click();await page.locator('.ar-cart-item').waitFor();assert((await page.locator('.ar-cart-summary').innerText()).includes('13,800원'));await page.locator('[data-ar-change=ar-apple][data-delta="1"]').click();assert((await page.locator('.ar-cart-summary').innerText()).includes('20,700원'));await page.reload();assert.equal(await page.locator('.ar-quantity span').innerText(),'3');
 await page.locator('[data-ar-remove=ar-apple]').click();assert.equal(await page.locator('.ar-cart-item').count(),0);assert((await page.locator('.ar-empty').innerText()).includes('비어'));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.goto(url+'/#/arirang');await page.locator('#arSort').selectOption('price-asc');await page.waitForFunction(()=>document.querySelector('.ar-card h3').textContent.includes('스낵'));await page.locator('#arStock').check();await page.waitForFunction(()=>document.querySelectorAll('.ar-card').length===17);
 await page.locator('#arSearch input').fill('우유');await page.locator('#arSearch button').click();await page.waitForFunction(()=>document.querySelectorAll('.ar-card').length===1);await page.locator('.ar-card h3 a').click();await page.locator('.ar-back').click();await page.locator('#arSearch').waitFor();assert(page.url().includes('q='));assert.equal(await page.locator('#arSearch input').inputValue(),'우유');
 await page.goto(url+'/#/market?major=food&middle=fruit&minor=apples');await page.locator('#arirang').waitFor({state:'visible'});assert(page.url().includes('#/arirang?'));assert.equal(await page.locator('.ar-card').count(),1);
 await page.goto(url+'/#/arirang?q='+encodeURIComponent('"><img src=x onerror="window.__unsafe=1">'));await page.locator('#arSearch').waitFor();assert.equal(await page.evaluate(()=>window.__unsafe),undefined);assert.equal(await page.locator('#arSearch img').count(),0);
 await page.goto(url+'/#/arirang/product/missing');assert((await page.locator('#arirang h1').innerText()).includes('찾을 수'));await page.goto(url+'/#/arirang');await page.locator('#themeBtn').click();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));if(width===390)await page.screenshot({path:path.join(os.tmpdir(),'arirang-dark-390.png'),fullPage:true});
 await page.locator(width<=760?'#mobileNav [data-tab=home]':'header [data-view=market]').click();await page.locator('#market').waitFor({state:'visible'});assert.equal(await page.locator('#marketHero').isVisible(),true);
 console.log(width+': food categories, leaf/search/sort, detail/back, basket totals/quantity/delete/persistence, region, invalid input/route, dark mode and overflow PASS');await context.close();
 }
 assert.deepEqual(errors,[]);await browser.close();server.close();
})().catch(e=>{console.error(e);process.exit(1)});
