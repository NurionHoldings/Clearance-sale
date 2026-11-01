import {OpsError,uuid,text,documentHTML} from './domain.mjs';
export function actorFromUser(user){if(!user?.id)return null;return {id:String(user.id),email:String(user.email||''),verified:Boolean(user.confirmedAt),admin:Array.isArray(user.roles)&&user.roles.includes('dapanda-admin')};}
const headers={'Cache-Control':'no-store, private','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; img-src data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"};
export function operationsHTTP({getActor,service,aiReview=async()=>{throw new OpsError('AI 모델 연결 전입니다. 규칙 검증 결과를 사용하세요.',503);}}){return async req=>{
 const json=(data,status=200)=>Response.json(data,{status,headers});
 try{
  const u=new URL(req.url),path=u.pathname.replace(/^\/ops-api\/?/,'').split('/').filter(Boolean);const [kind,key,action]=path;
  if(req.method!=='GET'&&req.method!=='POST')throw new OpsError('지원하지 않는 요청입니다.',405);
  if(req.method==='POST'){
   if(req.headers.get('origin')!==u.origin||req.headers.get('sec-fetch-site')==='cross-site')throw new OpsError('같은 사이트에서 요청하세요.',403);
   const length=Number(req.headers.get('content-length')||0);if(length>3*1024*1024)throw new OpsError('요청 파일이 너무 큽니다.',413);
  }
  const a=await getActor(req);if(kind==='session'&&req.method==='GET')return json({actor:a});
  if(!a?.verified)throw new OpsError('이메일 인증 후 로그인하세요.',401);
  const s=service();
  if(req.method==='GET'){
   if(kind==='overview'&&path.length===1)return json(await s.overview(a));
   if(kind==='audit'&&path.length===1)return json(await s.auditChain(a));
   if(kind==='contracts'&&key&&path.length<=3){const c=await s.getContract(a,key);if(action==='document')return new Response(documentHTML(c),{headers:{...headers,'Content-Type':'text/html; charset=utf-8','Content-Disposition':`inline; filename="dapanda-contract-${uuid(key)}.html"`}});if(action==='archive')return new Response(JSON.stringify(c,null,2),{headers:{...headers,'Content-Type':'application/json; charset=utf-8','Content-Disposition':`attachment; filename="dapanda-contract-${uuid(key)}.json"`}});if(!action)return json(c);}
   if(kind==='evidence'&&key&&path.length===2){const e=await s.getEvidence(a,key);return new Response(new Uint8Array(e.data),{headers:{...headers,'Content-Type':e.mime,'Content-Disposition':`attachment; filename="evidence-${uuid(key)}.${e.mime==='application/pdf'?'pdf':e.mime==='image/png'?'png':'jpg'}"`}});}
  }else{
   if(kind==='ledger'&&path.length===1){const f=await req.formData();const raw=f.get('data');let v;try{v=JSON.parse(String(raw));}catch{throw new OpsError('거래 자료 형식 오류입니다.');}const file=f.get('evidence');if(!file||typeof file.arrayBuffer!=='function'||file.size>2*1024*1024)throw new OpsError('2MB 이하 증빙 파일을 첨부하세요.');return json(await s.addLedger(a,v,{name:file.name,mime:file.type,data:Buffer.from(await file.arrayBuffer())}),201);}
   if(!req.headers.get('content-type')?.startsWith('application/json'))throw new OpsError('JSON 요청이 필요합니다.',415);
   const raw=await req.text();if(raw.length>24000)throw new OpsError('요청이 너무 큽니다.',413);let v;try{v=JSON.parse(raw);}catch{throw new OpsError('JSON 형식 오류입니다.');}
   if(kind==='merchant'&&path.length===1)return json(await s.saveMerchant(a,v));
   if(kind==='merchants'&&key&&action==='verify'&&path.length===3)return json(await s.verifyMerchant(a,key,v));
   if(kind==='contracts'&&key==='preview'&&path.length===2)return json(await s.previewContract(a,v));
   if(kind==='contracts'&&path.length===1)return json(await s.issueContract(a,v),201);
   if(kind==='contracts'&&key&&path.length===3){if(action==='read')return json(await s.readContract(a,key,v));if(action==='sign')return json(await s.signContract(a,key,v));if(action==='void')return json(await s.voidContract(a,key));}
   if(kind==='ledger'&&key&&action==='verify'&&path.length===3)return json(await s.verifyLedger(a,key,v));
   if(kind==='batches'&&path.length===1)return json(await s.prepare(a,v),201);
   if(kind==='batches'&&key&&path.length===3){
    if(action==='review')return json(await s.review(a,key));
    if(action==='approve')return json(await s.approve(a,key,v));
    if(action==='request')return json(await s.request(a,key,v),201);
    if(action==='cancel')return json(await s.cancel(a,key,v));
    if(action==='ai-review'){
     if(!a.admin)throw new OpsError('관리자 권한이 필요합니다.',403);
     const report=await s.review(a,key);const note=await aiReview({question:text(v.question,'검토 질문',1200),report});await s.saveAIReview(a,key,report.id,note);return json({report,note});
    }
   }
  }
  throw new OpsError('해당 기능을 찾을 수 없습니다.',404);
 }catch(e){return json({error:e instanceof OpsError?e.message:'서버 처리에 실패했습니다. 관리자 로그와 서비스 설정을 확인하세요.'},e instanceof OpsError?e.status:500);}
};}
