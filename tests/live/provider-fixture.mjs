export function providerFixture({mode='test'}={}){
 const payments=new Map(),calls=[];let state='upcoming',available=true,loseConfirmResponse=false,loseCancelResponse=false;
 return {payments,calls,setMode(value){mode=value;},setVideo(s,a=true){state=s;available=a;},loseConfirm(){loseConfirmResponse=true;},loseCancel(){loseCancelResponse=true;},
 configuration:()=>({billingEnabled:true,mode,clientKey:mode+'_ck_fixture',youtubeConfigured:true}),
 async inspectVideos(ids){return Promise.all(ids.map(id=>this.inspectVideo(id)));},
 async inspectVideo(id){return {youtubeId:id,available,state,source:'youtube-data-api',reason:available?null:'외부 재생 불가'};},
 async confirm(key,orderId,amount,idempotency){calls.push({kind:'confirm',key,idempotency});let p=payments.get(key);if(!p){p={paymentKey:key,orderId,totalAmount:amount,balanceAmount:amount,currency:'KRW',status:'DONE',method:'카드',approvedAt:'2026-11-20T00:00:00Z',receipt:{url:'https://dashboard.tosspayments.com/receipt'}};payments.set(key,p);}if(loseConfirmResponse){loseConfirmResponse=false;throw Error('network response lost');}return {...p};},
 async lookupOrder(order){return [...payments.values()].find(p=>p.orderId===order)||null;},
 async lookup(key){const p=payments.get(key);if(!p)throw Error('missing payment');return {...p};},
 async cancel(key,reason,idempotency){calls.push({kind:'cancel',key,idempotency});const p=payments.get(key);Object.assign(p,{status:'CANCELED',balanceAmount:0});if(loseCancelResponse){loseCancelResponse=false;throw Error('network response lost');}return {...p};}
 };
}
