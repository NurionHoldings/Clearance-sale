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
  await page.goto(url+'/#/market');await page.locator('.collection-entry').click();await page.locator('#menswear').waitFor({state:'visible'});await page.evaluate(()=>document.fonts.ready);
  assert.equal(await page.locator('#marketHero').isVisible(),false);assert.equal(await page.locator('.mw-vendor').count(),3);const currentURL=page.url();await page.locator('.footer-bottom a').click();assert.equal(page.url(),currentURL);assert.equal(await page.locator('#menswear .mw-card').count(),6);
  const metrics=await page.evaluate(()=>({page:document.documentElement.scrollWidth,viewport:innerWidth,over:[...document.querySelectorAll('#menswear *')].filter(e=>e.getBoundingClientRect().width>0&&e.scrollWidth>e.clientWidth+2&&getComputedStyle(e).overflowX==='visible').map(e=>e.className).filter(x=>typeof x==='string')}));assert(metrics.page<=width,JSON.stringify(metrics));
  if(width===320||width===1440)await page.screenshot({path:path.join(os.tmpdir(),'dapanda-menswear-'+width+'.png'),fullPage:false});
  for(const vendor of ['beverly-hills-polo','lee-won-jae','top-gun']){await page.locator('#mwFilterForm [name=vendor]').selectOption(vendor);await page.waitForFunction(()=>document.querySelectorAll('#menswear .mw-card').length===0);assert(await page.locator('.mw-empty').innerText().then(s=>s.includes('상품 정보를 준비')));}
  await page.locator('#mwReset').click();await page.waitForFunction(()=>document.querySelectorAll('#menswear .mw-card').length===6);
  await page.locator('[data-kind="셔츠"]').click();await page.waitForFunction(()=>document.querySelectorAll('#menswear .mw-card').length===1);assert((await page.locator('#menswear .mw-card h3').innerText()).includes('셔츠'));
  await page.locator('#mwReset').click();await page.waitForFunction(()=>document.querySelectorAll('#menswear .mw-card').length===6);
  await page.locator('#mwFilterForm [name=price]').selectOption('under30');await page.waitForFunction(()=>document.querySelectorAll('#menswear .mw-card').length===2);
  await page.locator('#mwSort').selectOption('price-asc');await page.waitForFunction(()=>document.querySelector('#menswear .mw-card h3').textContent.includes('셔츠'));assert((await page.locator('#mwFilterForm [name=price]').inputValue())==='under30');
  await page.locator('#menswear .mw-card h3 a').first().click();await page.locator('#menswearDetail').waitFor({state:'visible'});assert((await page.locator('#menswearDetail h1').innerText()).includes('셔츠'));
  await page.locator('[data-size="100"]').click();assert.equal(await page.locator('[data-size="100"]').getAttribute('aria-pressed'),'true');await page.locator('.mw-detail-actions [data-save]').click();assert.equal(await page.locator('.mw-detail-actions [data-save]').getAttribute('aria-pressed'),'true');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));if(width===320||width===1440)await page.screenshot({path:path.join(os.tmpdir(),'dapanda-menswear-detail-'+width+'.png')});
  await page.getByRole('link',{name:'남성복 목록으로',exact:true}).click();await page.locator('#menswear').waitFor({state:'visible'});assert.equal(await page.locator('#menswear .mw-card').count(),2);assert.equal(await page.locator('#mwFilterForm [name=price]').inputValue(),'under30');
  await page.reload();assert.equal(await page.locator('#menswear .mw-card [data-save="p-men-shirt"]').getAttribute('aria-pressed'),'true');
  await page.locator('#mwReset').click();await page.waitForFunction(()=>document.querySelectorAll('#menswear .mw-card').length===6);await page.locator('#mwFilterForm [name=stock]').check();await page.waitForFunction(()=>document.querySelectorAll('#menswear .mw-card').length===5);
  await page.locator('#themeBtn').click();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.goto(url+'/#/menswear/product/not-found');await page.locator('#menswearDetail h1').waitFor();assert((await page.locator('#menswearDetail h1').innerText()).includes('찾을 수'));
  await page.goto(url+'/#/menswear?q='+encodeURIComponent('\"><img src=x onerror="window.__unsafe=1">'));await page.locator('#mwFilterForm').waitFor();assert.equal(await page.evaluate(()=>window.__unsafe),undefined);assert.equal(await page.locator('#mwFilterForm img').count(),0);
  await page.locator('[data-view=market]').click();await page.locator('#market').waitFor({state:'visible'});assert.equal(await page.locator('#marketHero').isVisible(),true);await page.locator('#products .card button').nth(6).click();await page.locator('#productDialog').waitFor({state:'visible'});await page.locator('#closeProduct').click();await page.locator('[data-view=seller]').click();await page.locator('#seller').waitFor({state:'visible'});
  console.log(width+': routing, 3 vendors, combined filters, sort, sizes, saved persistence, back state, invalid URL, escaping, dark mode, legacy dialog/seller PASS');await context.close();
 }
 assert.deepEqual(errors,[]);await browser.close();server.close();
})().catch(e=>{console.error(e);process.exit(1)});
