import test from 'node:test';
import assert from 'node:assert/strict';
import {setup,admin,seller,outsider,terms,profile,proof,signedFixture,sale,range} from './helpers.mjs';
import {calculate,hash,contractText,documentHTML,terms as validateTerms} from '../../netlify/functions/_ops/domain.mjs';
import {operationsHTTP,actorFromUser} from '../../netlify/functions/_ops/http.mjs';

test('integer fee math covers VAT modes, shipping basis, actual PG, percentage PG and refund policy',()=>{
 const rows=[{id:'one',kind:'sale',reference:'sale',gross:100000,shipping:10000,pg_fee:3000}];
 const a=calculate(terms,rows);assert.equal(a.totals.commissionSupply,3150);assert.equal(a.totals.commissionVat,315);assert.equal(a.totals.payable,93535);
 assert.equal(calculate({...terms,commissionVat:'inclusive'},rows).totals.commission,3150);
 assert.equal(calculate({...terms,includeShipping:true},rows).totals.commission,3850);
 assert.equal(calculate({...terms,pgMode:'platform'},rows).totals.pg,0);
 assert.equal(calculate({...terms,pgMode:'rate',pgBps:300,pgVat:'exclusive'},rows).totals.pg,3300);
 const refund=[{...rows[0],kind:'refund',gross:20000,shipping:2000,pg_fee:-600}];
 assert.equal(calculate(terms,refund).totals.payable,-18707);
 assert.equal(calculate({...terms,pgMode:'rate',pgBps:300,pgRefund:'retain'},refund).totals.pg,0);
 assert.equal(calculate({...terms,pgMode:'rate',pgBps:300,pgRefund:'return'},refund).totals.pg,-600);
 assert.throws(()=>validateTerms({...terms,effectiveFrom:'2026-99-50'}));
 assert.equal(hash(Buffer.from('abc')),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
});

test('real SQL lifecycle preserves signatures, archives, reviewed totals, approval, one request and audit chain',async()=>{const f=await setup();try{const {s,db}=f;const {k}=await signedFixture(s);assert.equal(k.status,'signed');assert.equal(hash(k.document_text),k.document_hash);assert.equal(contractText(k.payload),k.document_text);assert(documentHTML(k).includes('테스트대표'));await sale(s,k);const b=await s.prepare(admin,range(k));assert.equal(b.snapshot.calculation.totals.payable,93535);
 await assert.rejects(s.request(admin,b.id,{checked:true,contentHash:b.content_hash}),/승인/);
 const report=await s.review(admin,b.id);assert.deepEqual(report.blockers,[]);
 await assert.rejects(s.approve(admin,b.id,{checked:true,contentHash:'wrong',reason:'대조'}),/원본/);
 await s.approve(admin,b.id,{checked:true,contentHash:b.content_hash,reason:'원 PG 증빙·계약·수취인 대조'});
 const request=await s.request(admin,b.id,{checked:true,contentHash:b.content_hash});assert.equal(request.actualTransfer,false);
 await assert.rejects(s.request(admin,b.id,{checked:true,contentHash:b.content_hash}),/승인/);
 await assert.rejects(s.prepare(admin,range(k)),/미정산/);
 const view=await s.overview(seller);assert.equal(view.requests.length,1);assert.equal(view.requests[0].amount,93535);assert.equal(view.audit.length,0);
 assert.equal((await s.auditChain(admin)).valid,true);
 await db.query("UPDATE ops_audit SET digest='tampered' WHERE seq=1");assert.equal((await s.auditChain(admin)).valid,false);
 }finally{await f.close();}});

test('tenant isolation, verified identity and signature receipt guard block forged access and stale contracts',async()=>{const f=await setup();try{const {s}=f;const m=await s.saveMerchant(seller,profile);await assert.rejects(s.saveMerchant({...seller,verified:false},profile),/인증/);await assert.rejects(s.verifyMerchant(seller,m.id,{checked:true,reference:'forged'}),/관리자/);await s.verifyMerchant(admin,m.id,{checked:true,reference:'bank-reference'});const p=await s.previewContract(admin,{merchantId:m.id,terms});const k=await s.issueContract(admin,{...p,providerName:'플랫폼담당',consent:true});
 await assert.rejects(s.getContract(outsider,k.id),/본인/);await assert.rejects(s.signContract(seller,k.id,{documentHash:k.document_hash,receiptId:'11111111-1111-4111-8111-111111111111',name:'대표',consent:true,authority:true}),/열람/);
 const r=await s.readContract(seller,k.id,{documentHash:k.document_hash});await assert.rejects(s.signContract(admin,k.id,{...r,documentHash:k.document_hash,name:'관리자',consent:true,authority:true}),/본인/);
 await s.saveMerchant(seller,{...profile,address:'변경된 주소'});await assert.rejects(s.signContract(seller,k.id,{...r,documentHash:k.document_hash,name:'대표',consent:true,authority:true}),/변경/);
 const spoof=actorFromUser({id:'x',confirmedAt:'now',userMetadata:{roles:['dapanda-admin']}});assert.equal(spoof.admin,false);
 }finally{await f.close();}});

test('partial refunds require original sale and cannot exceed gross/shipping or create duplicate events',async()=>{const f=await setup();try{const {s,k}= {s:f.s,...await signedFixture(f.s)};const l=await sale(s,k);const data={contractId:k.id,kind:'refund',parentId:l.id,provider:'PG-test',reference:'REFUND-1',gross:20000,shipping:2000,pgFee:-600,confirmedAt:'2026-11-12T00:00:00Z'};const r=await s.addLedger(admin,data,proof);await s.verifyLedger(admin,r.id,{checked:true});await assert.rejects(s.addLedger(admin,data,proof),/이미 등록/);await assert.rejects(s.addLedger(admin,{...data,reference:'REFUND-2',gross:90000},proof),/초과/);
 const b=await s.prepare(admin,{...range(k),from:'2026-11-13T00:00:00Z'});assert.equal(b.snapshot.calculation.totals.gross,-20000);assert((await s.review(admin,b.id)).blockers.some(x=>x.includes('0원')));await assert.rejects(s.approve(admin,b.id,{checked:true,reason:'강제',contentHash:b.content_hash}),/0원/);
 await s.cancel(admin,b.id,{reason:'차기 매출과 합산'});const combined=await s.prepare(admin,range(k));assert.equal(combined.snapshot.calculation.totals.payable,74828);
 }finally{await f.close();}});

test('new refunds and merchant changes after approval block payment request and release claims on cancellation',async()=>{const f=await setup();try{const {s}=f;const {k}=await signedFixture(s);const l=await sale(s,k);const b=await s.prepare(admin,range(k));await s.review(admin,b.id);await s.approve(admin,b.id,{checked:true,reason:'대조 완료',contentHash:b.content_hash});
 await s.addLedger(admin,{contractId:k.id,kind:'refund',parentId:l.id,provider:'PG-test',reference:'NEW-REFUND',gross:1000,shipping:0,pgFee:0,confirmedAt:'2026-11-15T00:00:00Z'},proof);await assert.rejects(s.request(admin,b.id,{checked:true,contentHash:b.content_hash}),/환불/);await s.cancel(admin,b.id,{reason:'추가 환불 재대조'});assert.equal((await f.db.query('SELECT count(*) AS n FROM ops_batch_lines')).rows[0].n,0);
 }finally{await f.close();}});

test('tampered contract/evidence and premature/unverified rows fail checks; file signatures are validated',async()=>{const f=await setup();try{const {s}=f;const {k}=await signedFixture(s);const data={contractId:k.id,kind:'sale',provider:'PG-test',reference:'bad-file',gross:100000,shipping:0,pgFee:0,confirmedAt:'2026-11-10T00:00:00Z'};
 await assert.rejects(s.addLedger(admin,data,{...proof,data:Buffer.from('<svg>fake</svg>')}),/形式|형식/);const l=await s.addLedger(admin,{...data,reference:'pending'},proof);await assert.rejects(s.prepare(admin,range(k)),/미정산/);await s.verifyLedger(admin,l.id,{checked:true});const b=await s.prepare(admin,range(k));await f.db.query("UPDATE ops_evidence SET sha256='bad' WHERE id=(SELECT evidence_id FROM ops_ledger WHERE id=$1)",[l.id]);assert((await s.review(admin,b.id)).blockers.some(x=>x.includes('증빙')));
 await f.db.query("UPDATE ops_contracts SET document_text='changed' WHERE id=$1",[k.id]);await assert.rejects(s.review(admin,b.id),/원문/);
 }finally{await f.close();}});

test('HTTP endpoints require origin + verified server identity, reject fake role, keep documents private',async()=>{const f=await setup();try{const {s}=f;const {k}=await signedFixture(s);let actor=null;const handler=operationsHTTP({getActor:async()=>actor,service:()=>s});const call=(path,method='GET',body,origin='https://example.test')=>handler(new Request('https://example.test/ops-api/'+path,{method,headers:{origin,'content-type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)}));
 assert.equal((await call('overview')).status,401);actor=seller;assert.equal((await call('merchant','POST',profile,'https://evil.test')).status,403);actor=outsider;assert.equal((await call('contracts/'+k.id+'/document')).status,403);actor=seller;const doc=await call('contracts/'+k.id+'/document');assert.equal(doc.status,200);assert.match(doc.headers.get('cache-control'),/no-store/);assert((await doc.text()).includes('서명본 SHA-256'));assert.equal((await call('contracts/'+k.id+'/archive')).headers.get('content-disposition').startsWith('attachment'),true);
 const overview=await (await call('overview')).json();assert.equal(overview.actor.admin,false);assert.equal((await call('audit')).status,403);
 }finally{await f.close();}});

test('previews bind issuance to the exact reviewed text, and profile edits invalidate approved payouts',async()=>{const f=await setup();try{const {s}=f;const m=await s.saveMerchant(seller,profile);await s.verifyMerchant(admin,m.id,{checked:true,reference:'bank-ref'});const p=await s.previewContract(admin,{merchantId:m.id,terms});await assert.rejects(s.issueContract(admin,{...p,documentHash:'forged',providerName:'담당',consent:true}),/미리보기/);const k=await s.issueContract(admin,{...p,providerName:'담당',consent:true});const r=await s.readContract(seller,k.id,{documentHash:k.document_hash});await s.signContract(seller,k.id,{...r,documentHash:k.document_hash,name:'대표',authority:true,consent:true});await sale(s,k);const b=await s.prepare(admin,range(k));await s.review(admin,b.id);await s.approve(admin,b.id,{checked:true,reason:'대조',contentHash:b.content_hash});await s.saveMerchant(seller,{...profile,contact:'변경 연락처'});await assert.rejects(s.request(admin,b.id,{checked:true,contentHash:b.content_hash}),/검증참조|변경/);
 }finally{await f.close();}});

test('refunds reserved by a different draft cannot be bypassed by requesting an earlier approved batch',async()=>{const f=await setup();try{const {s}=f;const {k}=await signedFixture(s);const l=await sale(s,k);const first=await s.prepare(admin,range(k));await s.review(admin,first.id);await s.approve(admin,first.id,{checked:true,reason:'대조',contentHash:first.content_hash});const r=await s.addLedger(admin,{contractId:k.id,kind:'refund',parentId:l.id,provider:'PG-test',reference:'LATER-REFUND',gross:10000,shipping:0,pgFee:0,confirmedAt:'2026-11-15T00:00:00Z'},proof);await s.verifyLedger(admin,r.id,{checked:true});await s.prepare(admin,range(k));await assert.rejects(s.request(admin,first.id,{checked:true,contentHash:first.content_hash}),/환불/);
 }finally{await f.close();}});

test('contract effective dates follow Korea business date around UTC midnight',async()=>{const f=await setup();try{const {s}=f;const {k}=await signedFixture(s);const v={contractId:k.id,kind:'sale',provider:'PG-test',reference:'KST-FIRST-DAY',gross:10000,shipping:0,pgFee:0,confirmedAt:'2026-10-31T15:30:00Z'};await s.addLedger(admin,v,proof);await assert.rejects(s.addLedger(admin,{...v,reference:'BEFORE-KST-START',confirmedAt:'2026-10-31T14:59:00Z'},proof),/계약 기간/);
 }finally{await f.close();}});
