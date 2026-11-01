export const menswearVendors = [{id:'beverly-hills-polo',name:'비버리힐스 폴로'},{id:'lee-won-jae',name:'이원재'},{id:'top-gun',name:'TOP GUN'}];
export const menswearListings = [
  { id:'p-menswear', title:'남성 이월 경량 패딩', kind:'아우터', condition:'이월 신품', region:'서울', qtyOnHand:35, qtyReserved:4, price:39000, listPrice:99000, color:'딥 네이비', swatch:'#253b50', sizes:['95','100','105','110'], material:'겉감 나일론 100% · 충전재 폴리에스터', description:'가볍게 걸치기 좋은 경량 패딩. 단정한 실루엣으로 일상과 출근길에 활용하는 구성입니다.' },
  { id:'p-men-knit', title:'코튼 블렌드 라운드 니트', kind:'니트', condition:'이월 신품', region:'경기', qtyOnHand:28, qtyReserved:3, price:29000, listPrice:69000, color:'오트밀', swatch:'#c3af91', sizes:['95','100','105'], material:'면 60% · 폴리에스터 40%', description:'차분한 오트밀 컬러와 기본 라운드넥. 셔츠 위에 겹쳐 입거나 한 벌로 가볍게 연출하기 좋습니다.' },
  { id:'p-men-shirt', title:'데일리 옥스퍼드 셔츠', kind:'셔츠', condition:'이월 신품', region:'서울', qtyOnHand:42, qtyReserved:5, price:24000, listPrice:59000, color:'라이트 블루', swatch:'#92afbf', sizes:['95','100','105','110'], material:'면 100%', description:'옷장에 오래 두고 입기 좋은 기본 셔츠. 산뜻한 블루 컬러에 단정한 칼라를 더했습니다.' },
  { id:'p-men-trousers', title:'컴포트 테이퍼드 팬츠', kind:'팬츠', condition:'이월 신품', region:'인천', qtyOnHand:24, qtyReserved:2, price:32000, listPrice:79000, color:'차콜', swatch:'#555b60', sizes:['30','32','34','36'], material:'폴리에스터 75% · 레이온 20% · 폴리우레탄 5%', description:'허벅지부터 밑단까지 자연스럽게 좁아지는 핏. 니트와 셔츠에 차분하게 어울리는 기본 팬츠입니다.' },
  { id:'p-men-coat', title:'울 블렌드 싱글 코트', kind:'아우터', condition:'전시', region:'경기', qtyOnHand:8, qtyReserved:1, price:69000, listPrice:179000, color:'카멜', swatch:'#a9815d', sizes:['100','105'], material:'모 50% · 폴리에스터 50%', description:'간결한 싱글 여밈과 차분한 카멜 컬러. 전시 상품의 상태를 확인하는 상세 화면 예시입니다.' },
  { id:'p-men-cardigan', title:'소프트 브이넥 카디건', kind:'니트', condition:'이월 신품', region:'서울', qtyOnHand:6, qtyReserved:6, price:35000, listPrice:89000, color:'포레스트', swatch:'#54665c', sizes:['95','100','105'], material:'아크릴 50% · 면 50%', description:'부드러운 인상의 브이넥과 버튼 여밈. 판매가능 수량이 없는 상품을 안내하는 예시입니다.' }
].map((p)=>({...p, category:'이월의류', subcategory:'남성복', channel:'marketplace', sellerId:'s-fashion', sellerOfRecord:'샘플패션유통', status:'approved'}));
export const menswearKinds=['전체','아우터','니트','셔츠','팬츠'];
export function menswearState(params=new URLSearchParams()) {
  return {vendor:menswearVendors.some(v=>v.id===params.get('vendor'))?params.get('vendor'):'all',kind:menswearKinds.includes(params.get('kind'))?params.get('kind'):'전체',q:(params.get('q')||'').slice(0,80),price:['under30','30to50','over50'].includes(params.get('price'))?params.get('price'):'all',condition:['이월 신품','전시'].includes(params.get('condition'))?params.get('condition'):'all',stock:params.get('stock')==='1',sort:['price-asc','price-desc','discount'].includes(params.get('sort'))?params.get('sort'):'default'};
}
export function filterMenswear(state,rows=menswearListings) {
  const items=rows.filter(p=>(state.vendor==='all'||p.sellerId===state.vendor)&&(state.kind==='전체'||p.kind===state.kind)&&(state.condition==='all'||p.condition===state.condition)&&(!state.stock||p.qtyOnHand-p.qtyReserved>0)&&(`${p.title} ${p.color} ${p.kind}`.toLowerCase().includes(state.q.trim().toLowerCase()))&&(state.price==='all'||(state.price==='under30'&&p.price<30000)||(state.price==='30to50'&&p.price>=30000&&p.price<50000)||(state.price==='over50'&&p.price>=50000)));
  if(state.sort==='price-asc')items.sort((a,b)=>a.price-b.price);
  if(state.sort==='price-desc')items.sort((a,b)=>b.price-a.price);
  if(state.sort==='discount')items.sort((a,b)=>(1-b.price/b.listPrice)-(1-a.price/a.listPrice));
  return items;
}
