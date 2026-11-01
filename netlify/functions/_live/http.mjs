import {OpsError} from '../_ops/domain.mjs';
export function liveHTTP({service,getActor}){return async req=>{const respond=(data,status=200)=>Response.json(data,{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'same-origin'}});try{const u=new URL(req.url),p=u.pathname.replace(/^\/live-api\/?/,'').split('/').filter(Boolean),s=service();
 if(req.method==='GET'&&p.join('/')==='catalog')return respond(await s.catalog());
 const a=await getActor();if(!a?.verified)throw new OpsError('이메일 인증 후 로그인하세요.',401);
 if(req.method==='GET'&&p.join('/')==='account')return respond(await s.account(a));
 if(req.method!=='POST')throw new OpsError('해당 기능을 찾을 수 없습니다.',404);
 if(req.headers.get('origin')!==u.origin||req.headers.get('sec-fetch-site')==='cross-site')throw new OpsError('같은 사이트에서 요청하세요.',403);
 if(!req.headers.get('content-type')?.startsWith('application/json'))throw new OpsError('JSON 요청이 필요합니다.',415);const raw=await req.text();if(raw.length>50000)throw new OpsError('요청이 너무 큽니다.',413);let v;try{v=JSON.parse(raw);}catch{throw new OpsError('JSON 형식을 확인하세요.');}
 if(p.length===1){if(p[0]==='studios')return respond(await s.saveStudio(a,v));if(p[0]==='bookings')return respond(await s.requestBooking(a,v),201);if(p[0]==='broadcasts')return respond(await s.saveBroadcast(a,v));}
 if(p.length===3){if(p[0]==='bookings'){if(p[2]==='quote')return respond(await s.quote(a,p[1],v));if(p[2]==='accept')return respond(await s.accept(a,p[1],v));if(p[2]==='cancel')return respond(await s.cancelBooking(a,p[1],v));if(p[2]==='complete')return respond(await s.completeBooking(a,p[1],v));}if(p[0]==='broadcasts'){if(p[2]==='review')return respond(await s.review(a,p[1],v));if(p[2]==='status')return respond(await s.transition(a,p[1],v));}}
 throw new OpsError('해당 기능을 찾을 수 없습니다.',404);
 }catch(e){return respond({error:e instanceof OpsError?e.message:'처리하지 못했습니다. 잠시 후 다시 시도하세요.'},e instanceof OpsError?e.status:500);}};}
