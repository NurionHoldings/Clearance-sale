import {OpsError} from '../_ops/domain.mjs';

// Only documented fixed provider hosts are used; neither browser input nor a webhook supplies a fetch URL.
export function providerConfiguration(env) {
 const clientKey=env('STUDIO_TOSS_CLIENT_KEY')||'',secretKey=env('STUDIO_TOSS_SECRET_KEY')||'';
 const mode=clientKey.startsWith('test_ck_')&&secretKey.startsWith('test_sk_')?'test':clientKey.startsWith('live_ck_')&&secretKey.startsWith('live_sk_')?'live':null;
 const billingEnabled=!!mode&&(mode==='test'||(env('STUDIO_LIVE_PAYMENTS_ENABLED')==='true'&&env('CONTEXT')==='production'));
 return {clientKey,secretKey,mode,billingEnabled,youtubeKey:env('YOUTUBE_DATA_API_KEY')||'',channelId:env('STUDIO_YOUTUBE_CHANNEL_ID')||''};
}
export function externalProviders({env,fetcher=fetch}) {
 const config=()=>providerConfiguration(env);
 async function toss(path,{body,key,allowNotFound=false}={}) {
  const c=config();if(!c.billingEnabled)throw new OpsError('스튜디오 PG 설정과 운영 결제 승인을 먼저 완료하세요.',503);
  let r;try{r=await fetcher('https://api.tosspayments.com/v1/payments/'+path,{method:body?'POST':'GET',headers:{Authorization:'Basic '+Buffer.from(c.secretKey+':').toString('base64'),...(body?{'Content-Type':'application/json','Idempotency-Key':key}:{})},body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(10000)});}catch{throw new OpsError('PG 응답을 확인하지 못했습니다. 재조회로 결과를 대조하세요. 다시 결제하지 마세요.',503);}
  let data;try{data=await r.json();}catch{throw new OpsError('PG 응답을 해석하지 못했습니다. 재조회하세요.',502);}
  if(allowNotFound&&r.status===404)return null;
  if(!r.ok)throw new OpsError('PG 처리 실패 ('+String(data.code||r.status).replace(/[^A-Z0-9_]/g,'').slice(0,80)+'). 결제내역을 재조회하세요.',502);
  return data;
 }
 return {
  configuration(){const c=config();return {billingEnabled:c.billingEnabled,mode:c.mode,clientKey:c.billingEnabled?c.clientKey:null,youtubeConfigured:!!c.youtubeKey&&/^UC[\w-]{22}$/.test(c.channelId)};},
  confirm(paymentKey,orderId,amount,key){return toss('confirm',{body:{paymentKey,orderId,amount},key});},
  lookupOrder(orderId){return toss('orders/'+encodeURIComponent(orderId),{allowNotFound:true});},
  lookup(paymentKey){return toss(encodeURIComponent(paymentKey));},
  cancel(paymentKey,reason,key){return toss(encodeURIComponent(paymentKey)+'/cancel',{body:{cancelReason:reason},key});},
  async inspectVideos(videoIds){
   if(!Array.isArray(videoIds)||videoIds.length>50||videoIds.some(id=>!/^[-_A-Za-z0-9]{11}$/.test(id)))throw new OpsError('방송 주소를 확인하세요.');
   const c=config();if(!c.youtubeKey||!/^UC[\w-]{22}$/.test(c.channelId))throw new OpsError('YouTube Data API 키와 운영 채널 ID를 먼저 연결하세요.',503);
   let r,data;try{r=await fetcher('https://www.googleapis.com/youtube/v3/videos?'+new URLSearchParams({part:'snippet,status,liveStreamingDetails',id:videoIds.join(','),key:c.youtubeKey}),{signal:AbortSignal.timeout(8000)});data=await r.json();}catch{throw new OpsError('YouTube 상태 조회가 지연됩니다. 잠시 후 재검증하세요.',503);}
   if(!r.ok)throw new OpsError('YouTube 조회 권한·할당량을 확인하세요.',503);
   return videoIds.map(videoId=>{const item=data.items?.find(v=>v.id===videoId);
   const available=!!item&&item.snippet?.channelId===c.channelId&&item.status?.embeddable===true&&['public','unlisted'].includes(item.status?.privacyStatus)&&item.status?.uploadStatus==='processed';
   const details=item?.liveStreamingDetails;
   return {youtubeId:videoId,available,state:!available?'unavailable':details?.actualEndTime?'ended':details?.actualStartTime?'live':details?.scheduledStartTime?'upcoming':'not-live',reason:!available?'운영 채널·공개 범위·외부 재생 허용을 확인하세요.':!details?'일반 동영상입니다. 라이브 방송 주소를 등록하세요.':null,source:'youtube-data-api',channelId:item?.snippet?.channelId===c.channelId?c.channelId:null};});
  },
  async inspectVideo(videoId){return (await this.inspectVideos([videoId]))[0];}
 };
}
