import {OpsError,id,uuid,text,integer,stable} from '../_ops/domain.mjs';

export function studioBilling({pool,tx,audit,booking,contract,valid,clock,gateway}) {
 const one=async(c,q,p=[])=>(await c.query(q,p)).rows[0];
 const login=a=>{if(!a?.verified)throw new OpsError('이메일 인증 후 로그인하세요.',401);};
 const admin=a=>{login(a);if(!a.admin)throw new OpsError('관리자 권한이 필요합니다.',403);};
 const configured=()=>{const c=gateway.configuration();if(!c.billingEnabled)throw new OpsError('스튜디오 결제 서비스 연결 전입니다.',503);return c;};
 const publicInvoice=i=>({id:i.id,booking_id:i.booking_id,order_id:i.order_id,amount_won:Number(i.amount_won),quote_version:i.quote_version,quote_snapshot:i.quote_snapshot,mode:i.mode,status:i.status,provider_status:i.provider_status,receipt_url:i.receipt_url,approved_at:i.approved_at,last_checked_at:i.last_checked_at,refund_reason:i.refund_reason});
 async function invoice(c,a,iid){const i=await one(c,'SELECT * FROM live_invoices WHERE id=$1',[uuid(iid)]);if(!i)throw new OpsError('청구 내역이 없습니다.',404);const b=await booking(c,a,i.booking_id);return {i,b};}
 async function payable(c,a,b){
  if(b.status!=='confirmed'||+clock()>=+new Date(b.starts_at))throw new OpsError('이용 시작 전 확정 예약만 결제할 수 있습니다.',409);
  const k=await contract(c,a,b.contract_id);if(!valid(k)||!b.studio_active)throw new OpsError('업체 계약·스튜디오 상태를 확인하세요.',409);
 }
 function matches(i,p){if(p.paymentKey!==i.payment_key||p.orderId!==i.order_id||p.totalAmount!==Number(i.amount_won)||p.currency!=='KRW')throw new OpsError('PG 결제와 청구서가 일치하지 않습니다. 관리자 확인이 필요합니다.',409);}
 function receipt(p){try{const u=new URL(p.receipt?.url);return u.protocol==='https:'&&(u.hostname==='tosspayments.com'||u.hostname.endsWith('.tosspayments.com'))?u.href:null;}catch{return null;}}
 async function record(a,iid,p){return tx(async c=>{
  const {i,b}=await invoice(c,a,iid);matches(i,p);
  if(['paid','refund_pending','refunded'].includes(i.status)&&!['DONE','CANCELED','PARTIAL_CANCELED'].includes(p.status))throw new OpsError('PG 상태가 이전 처리 결과보다 오래되었습니다. 다시 대조하세요.',409);
  let next=i.status;
  if(p.status==='DONE'){
   if(['refunded','void'].includes(i.status))throw new OpsError('종료한 청구의 PG 상태가 달라 관리자 대조가 필요합니다.',409);
   next=i.status==='refund_pending'?'refund_pending':'paid';
  }else if(p.status==='CANCELED'&&p.balanceAmount===0){next='refunded';}
  else if(['ABORTED','EXPIRED'].includes(p.status)&&i.status==='confirming'){next='void';}
  else if(p.status==='PARTIAL_CANCELED')throw new OpsError('PG에서 부분 취소가 감지되었습니다. 전체 환불 처리 전 관리자 대조가 필요합니다.',409);
  await c.query('UPDATE live_invoices SET status=$2,provider_status=$3,receipt_url=$4,approved_at=$5,last_checked_at=$6,updated_at=now() WHERE id=$1',[i.id,next,p.status,receipt(p),p.approvedAt||null,clock().toISOString()]);
  if(next==='refunded'&&b.status==='confirmed')await c.query("UPDATE live_bookings SET status='cancelled',decision_note=$2 WHERE id=$1",[b.id,i.refund_reason||'PG 전액 취소 확인']);
  if(next!==i.status||p.status!==i.provider_status)await audit(c,a,'studio.payment.'+next,i.id,{orderId:i.order_id,amountWon:Number(i.amount_won),mode:i.mode,providerStatus:p.status});
  return publicInvoice(await one(c,'SELECT * FROM live_invoices WHERE id=$1',[i.id]));
 });}
 async function checkMode(i){const config=configured();if(i.mode!==config.mode)throw new OpsError('청구 시점과 PG 테스트/운영 모드가 다릅니다. 기존 모드에서 먼저 처리하세요.',409);}
 return {
  publicInvoice,
  async createInvoice(a,bid){login(a);const config=configured();return tx(async c=>{
   if(config.mode==='live'&&!await one(c,"SELECT id FROM live_invoices WHERE mode='test' AND status='refunded' LIMIT 1"))throw new OpsError('같은 운영 DB에서 PG 테스트 승인·전액 취소 리허설을 먼저 완료하세요.',409);
   const b=await booking(c,a,bid);if(b.owner_id!==a.id)throw new OpsError('예약 업체 본인만 결제를 시작할 수 있습니다.',403);await payable(c,a,b);
   const amount=integer(Number(b.quote_won),1,100000000,'결제 금액');if(!b.accepted_quote||b.accepted_quote.quoteVersion!==b.quote_version||b.accepted_quote.amountWon!==amount)throw new OpsError('확정 견적을 확인하세요.',409);
   let i=await one(c,"SELECT * FROM live_invoices WHERE booking_id=$1 AND status<>'void'",[b.id]);
   if(!i){const iid=id(),order='studio_'+iid.replaceAll('-','');await c.query("INSERT INTO live_invoices(id,booking_id,order_id,amount_won,quote_version,quote_snapshot,mode,status) VALUES($1,$2,$3,$4,$5,$6,$7,'created')",[iid,b.id,order,amount,b.quote_version,JSON.stringify(b.accepted_quote),config.mode]);i=await one(c,'SELECT * FROM live_invoices WHERE id=$1',[iid]);await audit(c,a,'studio.invoice.created',iid,{bookingId:b.id,orderId:order,amount,mode:config.mode});}
   if(i.status!=='created')throw new OpsError('이미 처리 중이거나 종료한 청구입니다. 결제내역을 재조회하세요.',409);await checkMode(i);
   return {...publicInvoice(i),clientKey:config.clientKey,customerKey:'studio_'+a.id.replace(/[^A-Za-z0-9_-]/g,'_').slice(0,40),orderName:('다판다 '+b.studio_name+' 스튜디오 이용료').slice(0,100)};
  });},
  async confirmPayment(a,v){login(a);const paymentKey=text(v.paymentKey,'결제 식별자',200);const amount=integer(v.amount,1,100000000,'승인 금액');const orderId=text(v.orderId,'청구 주문번호',64);
   const i=await tx(async c=>{const i=await one(c,'SELECT * FROM live_invoices WHERE order_id=$1',[orderId]);if(!i)throw new OpsError('청구 주문번호를 확인하세요.',404);const b=await booking(c,a,i.booking_id);if(b.owner_id!==a.id)throw new OpsError('예약 업체 본인만 결제할 수 있습니다.',403);await checkMode(i);
    if(Number(i.amount_won)!==amount)throw new OpsError('청구 금액과 승인 금액이 다릅니다.',409);
    if(i.payment_key&&i.payment_key!==paymentKey)throw new OpsError('다른 결제 식별자가 이미 연결되었습니다.',409);
    if(i.status==='paid')return i;if(!['created','confirming'].includes(i.status))throw new OpsError('승인할 수 없는 청구입니다.',409);
    if(i.status==='created'){await payable(c,a,b);if(stable(i.quote_snapshot)!==stable(b.accepted_quote))throw new OpsError('견적이 변경되었습니다.',409);await c.query("UPDATE live_invoices SET status='confirming',payment_key=$2,updated_at=now() WHERE id=$1",[i.id,paymentKey]);await audit(c,a,'studio.payment.requested',i.id,{orderId,amount});}
    return {...i,payment_key:paymentKey};});
   if(i.status==='paid')return publicInvoice(i);
   // A persistent intent precedes the external charge. A timeout never creates a second order.
   let result;try{result=await gateway.confirm(paymentKey,orderId,amount,'studio-confirm-'+i.id);}catch(err){try{result=await gateway.lookup(paymentKey);}catch{throw err;}}
   return record(a,i.id,result);
  },
  async reconcilePayment(a,iid){login(a);const {i,b}=await invoice(pool,a,iid);await checkMode(i);if(!i.payment_key){if(b.owner_id!==a.id)return publicInvoice(i);const found=await gateway.lookupOrder(i.order_id);if(!found)return publicInvoice(i);if(found.orderId!==i.order_id||found.totalAmount!==Number(i.amount_won)||found.currency!=='KRW')throw new OpsError('PG 주문 내역과 견적이 다릅니다.',409);if(['IN_PROGRESS','DONE'].includes(found.status))return this.confirmPayment(a,{orderId:i.order_id,paymentKey:found.paymentKey,amount:Number(i.amount_won)});return publicInvoice(i);}let payment=await gateway.lookup(i.payment_key);matches(i,payment);if(i.status==='confirming'&&payment.status==='IN_PROGRESS'&&b.status==='confirmed'&&+clock()<+new Date(b.starts_at)){await payable(pool,a,b);payment=await gateway.confirm(i.payment_key,i.order_id,Number(i.amount_won),'studio-confirm-'+i.id);}if(i.status==='refund_pending'&&payment.status==='DONE')payment=await gateway.cancel(i.payment_key,i.refund_reason,'studio-refund-'+i.id);return record(a,i.id,payment);},
  async refundPayment(a,iid,v){admin(a);if(v.consent!==true)throw new OpsError('전액 환불과 예약 취소를 확인하세요.');const reason=text(v.reason,'전액 취소 사유',200);
   const i=await tx(async c=>{const {i,b}=await invoice(c,a,iid);await checkMode(i);if(!['paid','refund_pending'].includes(i.status))throw new OpsError('승인된 결제만 환불할 수 있습니다.',409);
    if(await one(c,"SELECT id FROM live_broadcasts WHERE booking_id=$1 AND status IN ('scheduled','live')",[b.id]))throw new OpsError('공개 편성·방송을 먼저 종료하거나 취소하세요.',409);
    if(i.status==='paid'){await c.query("UPDATE live_invoices SET status='refund_pending',refund_reason=$2,updated_at=now() WHERE id=$1",[i.id,reason]);await audit(c,a,'studio.refund.requested',i.id,{reason,amountWon:Number(i.amount_won)});}return {...i,refund_reason:i.refund_reason||reason};});
   // No partial refunds or bank account collection; full cancellation of card/simple-pay only.
   let result;try{result=await gateway.cancel(i.payment_key,i.refund_reason,'studio-refund-'+i.id);}catch(err){try{result=await gateway.lookup(i.payment_key);}catch{throw err;}}
   return record(a,i.id,result);
  },
  async invoiceList(a){login(a);const rows=(await pool.query(a.admin?'SELECT i.* FROM live_invoices i ORDER BY i.created_at DESC LIMIT 300':'SELECT i.* FROM live_invoices i JOIN live_bookings b ON b.id=i.booking_id JOIN ops_merchants m ON m.id=b.merchant_id WHERE m.owner_id=$1 ORDER BY i.created_at DESC LIMIT 100',a.admin?[]:[a.id])).rows;return rows.map(publicInvoice);},
 };
}
