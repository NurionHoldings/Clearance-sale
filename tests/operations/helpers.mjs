import {PGlite} from '@electric-sql/pglite';
import {readFileSync} from 'node:fs';
import {createOperations} from '../../netlify/functions/_ops/service.mjs';
export const admin={id:'platform-owner',email:'admin@example.test',verified:true,admin:true};
export const seller={id:'merchant-one',email:'seller@example.test',verified:true,admin:false};
export const outsider={id:'merchant-two',email:'other@example.test',verified:true,admin:false};
export const terms={commissionBps:350,commissionVat:'exclusive',includeShipping:false,pgMode:'actual',pgBps:0,pgVat:'inclusive',pgRefund:'return',delayDays:2,cycle:'매월 15일·말일',effectiveFrom:'2026-11-01',effectiveTo:'2027-10-31',specialTerms:''};
export const profile={name:'테스트입점사',businessNumber:'1234567890',representative:'테스트대표',contact:'000-0000',address:'테스트 주소'};
export const proof={name:'provider-statement.pdf',mime:'application/pdf',data:Buffer.from('%PDF-1.4\nfixture evidence')};
export async function setup(){const db=new PGlite();await db.exec(readFileSync('netlify/database/migrations/20261101170000_merchant_operations.sql','utf8'));let tail=Promise.resolve();const pool={query:(...a)=>db.query(...a),async connect(){const old=tail;let release;tail=new Promise(r=>release=r);await old;return {query:(...a)=>db.query(...a),release};}};const clock=()=>new Date('2026-11-20T00:00:00Z');const s=createOperations(pool,{clock});return {db,pool,s,close:()=>db.close()};}
export async function signedFixture(s){const m=await s.saveMerchant(seller,profile);await s.verifyMerchant(admin,m.id,{checked:true,reference:'BANK-VERIFIED-001'});const p=await s.previewContract(admin,{merchantId:m.id,terms});const k=await s.issueContract(admin,{...p,providerName:'플랫폼담당',consent:true});const r=await s.readContract(seller,k.id,{documentHash:k.document_hash});const signed=await s.signContract(seller,k.id,{...r,documentHash:k.document_hash,name:'테스트대표',authority:true,consent:true});return {m,k:signed};}
export async function sale(s,k,reference='PG-SALE-001',gross=100000){const l=await s.addLedger(admin,{contractId:k.id,kind:'sale',provider:'PG-test',reference,gross,shipping:10000,pgFee:3000,confirmedAt:'2026-11-10T00:00:00Z'},proof);await s.verifyLedger(admin,l.id,{checked:true});return l;}
export const range=k=>({contractId:k.id,from:'2026-11-01T00:00:00Z',to:'2026-11-19T23:59:59Z'});
