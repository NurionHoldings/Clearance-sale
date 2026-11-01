import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {setup,signedFixture,admin,seller,outsider} from '../operations/helpers.mjs';
import {providerFixture} from './provider-fixture.mjs';
import {liveService} from '../../netlify/functions/_live/service.mjs';
import {externalProviders,providerConfiguration} from '../../netlify/functions/_live/providers.mjs';
async function fixture(mode='test'){
 const f=await setup();for(const file of ['20261101210000_live_studio.sql','20261102010000_live_operations.sql'])await f.db.exec(readFileSync('netlify/database/migrations/'+file,'utf8'));
 const now={value:new Date('2026-11-20T00:00:00Z')},gateway=providerFixture({mode}),s=liveService(f.pool,{clock:()=>now.value,gateway}),{k}=await signedFixture(f.s);
 const studio=await s.saveStudio(admin,{name:'검증용 공간',description:'실제 고객 자료 아님',address:'테스트',equipment:['카메라'],bufferMinutes:30,active:true});
 const b=await s.requestBooking(seller,{studioId:studio.id,contractId:k.id,startsAt:'2026-11-21T01:00:00Z',endsAt:'2026-11-21T02:00:00Z',purpose:'검증용 촬영'});await s.quote(admin,b.id,{amountWon:55000,note:'장비 포함 55,000원 (VAT 포함), 이용 전 전액 취소 합의'});await s.accept(seller,b.id,{quoteVersion:1,consent:true});
 if(mode==='live'){
  await assert.rejects(s.createInvoice(seller,b.id),/리허설/);gateway.setMode('test');
  const rb=await s.requestBooking(seller,{studioId:studio.id,contractId:k.id,startsAt:'2026-11-22T01:00:00Z',endsAt:'2026-11-22T02:00:00Z',purpose:'PG 테스트 리허설'});await s.quote(admin,rb.id,{amountWon:1000,note:'PG 테스트 전용'});await s.accept(seller,rb.id,{quoteVersion:1,consent:true});const ri=await s.createInvoice(seller,rb.id);await s.confirmPayment(seller,{orderId:ri.order_id,amount:1000,paymentKey:'prior_rehearsal'});await s.refundPayment(admin,ri.id,{reason:'테스트 전액 취소',consent:true});gateway.setMode('live');
 }
 return {...f,ops:f.s,s,now,gateway,b};
}
const confirm=i=>({orderId:i.order_id,amount:i.amount_won,paymentKey:'payment_test_unique'});

test('immutable quote sets checkout amount; identity, amount and ownership are enforced before PG; repeated approval is idempotent',async()=>{const f=await fixture();try{
 await assert.rejects(f.s.createInvoice(outsider,f.b.id),/조회/);await assert.rejects(f.s.createInvoice(admin,f.b.id),/본인/);
 const i=await f.s.createInvoice(seller,f.b.id),again=await f.s.createInvoice(seller,f.b.id);assert.equal(i.id,again.id);assert.equal(i.amount_won,55000);
 await assert.rejects(f.s.confirmPayment(seller,{...confirm(i),amount:1}),/금액/);assert.equal(f.gateway.calls.length,0);
 await assert.rejects(f.s.confirmPayment(outsider,confirm(i)),/조회/);assert.equal(f.gateway.calls.length,0);
 const paid=await f.s.confirmPayment(seller,confirm(i));assert.equal(paid.status,'paid');assert.equal(paid.mode,'test');assert(!JSON.stringify(paid).includes('payment_test_unique'));
 await f.s.confirmPayment(seller,confirm(i));assert.equal(f.gateway.calls.length,1);
 await assert.rejects(f.s.cancelBooking(seller,f.b.id,{reason:'환불 없이 취소'}),/전액 취소/);
 assert.equal((await f.s.invoiceList(outsider)).length,0);assert.equal((await f.s.operationalStatus(admin)).pendingPayments,0);await assert.rejects(f.s.operationalStatus(seller),/관리자/);
 assert.equal((await f.ops.auditChain(admin)).valid,true);assert.equal((await f.db.query('SELECT count(*) AS n FROM live_invoices')).rows[0].n,1);
 }finally{await f.close();}});

test('lost PG approval/cancel response is recovered by lookup; only admin can refund; cancellation closes reservation once',async()=>{const f=await fixture();try{
 const i=await f.s.createInvoice(seller,f.b.id);f.gateway.loseConfirm();assert.equal((await f.s.confirmPayment(seller,confirm(i))).status,'paid');
 await assert.rejects(f.s.refundPayment(seller,i.id,{reason:'취소',consent:true}),/관리자/);await assert.rejects(f.s.refundPayment(admin,i.id,{reason:'취소',consent:false}),/확인/);
 f.gateway.loseCancel();const r=await f.s.refundPayment(admin,i.id,{reason:'업체 요청, 이용 전 전액 취소 합의',consent:true});assert.equal(r.status,'refunded');assert.equal((await f.s.account(seller)).bookings[0].status,'cancelled');
 assert.equal((await f.s.reconcilePayment(seller,i.id)).status,'refunded');assert.equal(f.gateway.calls.filter(x=>x.kind==='cancel').length,1);assert.equal((await f.ops.auditChain(admin)).valid,true);
 assert.equal((await f.db.query("SELECT count(*) AS n FROM ops_audit WHERE action='studio.payment.refunded'")).rows[0].n,1);
 }finally{await f.close();}});

test('uncertain provider approval persists before external call, blocks cancellation and survives process restart',async()=>{const f=await fixture();try{
 const i=await f.s.createInvoice(seller,f.b.id);const original=f.gateway.confirm;f.gateway.confirm=async()=>{throw Error('provider unreachable');};
 await assert.rejects(f.s.confirmPayment(seller,confirm(i)),/unreachable/);assert.equal((await f.s.invoiceList(seller))[0].status,'confirming');await assert.rejects(f.s.cancelBooking(seller,f.b.id,{reason:'의도치 않은 취소'}),/대조/);
 f.gateway.confirm=original;await original(confirm(i).paymentKey,i.order_id,i.amount_won,'studio-confirm-'+i.id);
 const restarted=liveService(f.pool,{clock:()=>f.now.value,gateway:f.gateway});assert.equal((await restarted.reconcilePayment(seller,i.id)).status,'paid');
 const p=f.gateway.payments.get(confirm(i).paymentKey);p.totalAmount=1;await assert.rejects(restarted.reconcilePayment(seller,i.id),/일치/);assert.equal((await restarted.invoiceList(seller))[0].amount_won,55000);
 }finally{await f.close();}});

test('unpaid/test invoices block commercial publication; provider channel and current signal required; stale LIVE degrades publicly',async()=>{const f=await fixture('live');try{
 const x=await f.s.saveBroadcast(seller,{bookingId:f.b.id,title:'통합 검증',description:'라이브 운영 검증',youtubeUrl:'https://youtu.be/abcdefghijk',hostName:'검증 진행자',producer:'검증 담당자',products:[],replayAllowed:true});
 await f.s.review(admin,x.id,{revision:1,checklist:{equipment:true,network:true,rights:true,products:true,staff:true}});const publish=()=>f.s.transition(admin,x.id,{revision:1,status:'scheduled',confirmed:true,note:'실방송 확인'});
 await assert.rejects(publish(),/YouTube/);f.gateway.setVideo('upcoming',false);await f.s.verifyProvider(admin,x.id,{revision:1});await assert.rejects(publish(),/YouTube/);
 f.gateway.setVideo('upcoming');await f.s.verifyProvider(admin,x.id,{revision:1});await assert.rejects(publish(),/이용료/);
 const i=await f.s.createInvoice(seller,f.b.id);await f.s.confirmPayment(seller,confirm(i));await publish();
 f.now.value=new Date('2026-11-21T01:00:00Z');await assert.rejects(f.s.transition(admin,x.id,{revision:2,status:'live',confirmed:true,note:'송출'}),/YouTube/);
 f.gateway.setVideo('live');await f.s.verifyProvider(admin,x.id,{revision:2});await f.s.transition(admin,x.id,{revision:2,status:'live',confirmed:true,note:'송출 확인'});assert.equal((await f.s.catalog()).broadcasts[0].status,'live');
 await assert.rejects(f.s.refundPayment(admin,i.id,{reason:'편성 중 환불',consent:true}),/방송/);
 f.now.value=new Date('2026-11-21T01:06:00Z');assert.equal((await f.s.catalog()).broadcasts[0].status,'signal_unverified');f.gateway.setVideo('ended');await f.s.monitor();assert.equal((await f.s.catalog()).broadcasts[0].provider_check.state,'ended');assert.equal((await f.s.catalog()).broadcasts[0].status,'signal_unverified');
 }finally{await f.close();}});

test('provider adapter uses official endpoints, Basic server credentials and idempotency; preview never accepts live charges',async()=>{
 const vars={STUDIO_TOSS_CLIENT_KEY:'live_ck_fixture',STUDIO_TOSS_SECRET_KEY:'live_sk_secret',STUDIO_LIVE_PAYMENTS_ENABLED:'true',CONTEXT:'deploy-preview',YOUTUBE_DATA_API_KEY:'server_secret',STUDIO_YOUTUBE_CHANNEL_ID:'UCabcdefghijklmnopqrstuv'};const env=k=>vars[k];assert.equal(providerConfiguration(env).billingEnabled,false);
 let requests=[];const gateway=externalProviders({env,fetcher:async(url,opts)=>{requests.push({url,opts});return Response.json(url.includes('googleapis')?{items:[{id:'abcdefghijk',snippet:{channelId:vars.STUDIO_YOUTUBE_CHANNEL_ID},status:{embeddable:true,privacyStatus:'unlisted',uploadStatus:'processed'},liveStreamingDetails:{actualStartTime:'2026-11-20'}}]}:{status:'DONE'});}});
 await assert.rejects(gateway.confirm('key','order',1,'idem'),/PG 설정/);assert.equal(requests.length,0);vars.CONTEXT='production';await gateway.confirm('key','order',55000,'same-key');assert.equal(requests[0].url,'https://api.tosspayments.com/v1/payments/confirm');assert.equal(requests[0].opts.headers['Idempotency-Key'],'same-key');assert.equal(requests[0].opts.headers.Authorization,'Basic '+Buffer.from('live_sk_secret:').toString('base64'));assert.equal((await gateway.inspectVideo('abcdefghijk')).state,'live');assert(!JSON.stringify(gateway.configuration()).includes('secret'));vars.STUDIO_TOSS_SECRET_KEY='test_sk_secret';assert.equal(gateway.configuration().billingEnabled,false);
});


test('lost mobile return is recovered by server order lookup without a second order or charge',async()=>{const f=await fixture();try{
 const i=await f.s.createInvoice(seller,f.b.id);assert.equal((await f.s.reconcilePayment(seller,i.id)).status,'created');
 f.gateway.payments.set('mobile_return_key',{paymentKey:'mobile_return_key',orderId:i.order_id,totalAmount:55000,balanceAmount:55000,currency:'KRW',status:'IN_PROGRESS'});
 assert.equal((await f.s.reconcilePayment(admin,i.id)).status,'created');
 const original=f.gateway.confirm;f.gateway.confirm=async(...args)=>{f.gateway.payments.delete('mobile_return_key');return original(...args);};
 assert.equal((await f.s.reconcilePayment(seller,i.id)).status,'paid');assert.equal(f.gateway.calls.filter(c=>c.kind==='confirm').length,1);
 }finally{await f.close();}});
