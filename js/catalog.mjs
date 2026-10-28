export const CHANNEL_LABEL = {
  direct: '플랫폼 직접판매',
  marketplace: '입점업체 중개판매'
};

export const CATEGORY_GROUPS = ["이월의류","신발류","모자","귀금속","농식품","공산품","가전제품"];

export const listings = [
  { id: "p-menswear", title: "남성 이월 경량 패딩", category: "이월의류", subcategory: "남성복", condition: "이월 신품", region: "서울", qtyOnHand: 35, qtyReserved: 4, price: 39000, listPrice: 99000, channel: 'marketplace', sellerId: 's-fashion', sellerOfRecord: "샘플패션유통", status: 'approved' },
  { id: "p-womenswear", title: "여성 시즌오프 니트", category: "이월의류", subcategory: "여성복", condition: "이월 신품", region: "경기", qtyOnHand: 48, qtyReserved: 6, price: 19000, listPrice: 59000, channel: 'marketplace', sellerId: 's-fashion', sellerOfRecord: "샘플패션유통", status: 'approved' },
  { id: "p-sportswear", title: "운동복 트레이닝 세트", category: "이월의류", subcategory: "운동복", condition: "이월 신품", region: "대구", qtyOnHand: 30, qtyReserved: 2, price: 29000, listPrice: 79000, channel: 'direct', sellerId: 'platform', sellerOfRecord: "(주)대현산업 플랫폼사업부(데모 운영사)", status: 'approved' },
  { id: "p-hikingwear", title: "등산용 방풍 재킷", category: "이월의류", subcategory: "등산복", condition: "이월 신품", region: "부산", qtyOnHand: 22, qtyReserved: 3, price: 45000, listPrice: 119000, channel: 'marketplace', sellerId: 's-outdoor', sellerOfRecord: "샘플아웃도어", status: 'approved' },
  { id: "p-sneakers", title: "이월 운동화", category: "신발류", subcategory: "운동화", condition: "이월 신품", region: "경기", qtyOnHand: 55, qtyReserved: 5, price: 39000, listPrice: 89000, channel: 'marketplace', sellerId: 's-shoes', sellerOfRecord: "샘플슈즈", status: 'approved' },
  { id: "p-dress-shoes", title: "남성 정장 구두", category: "신발류", subcategory: "구두", condition: "이월 신품", region: "서울", qtyOnHand: 24, qtyReserved: 1, price: 49000, listPrice: 129000, channel: 'marketplace', sellerId: 's-shoes', sellerOfRecord: "샘플슈즈", status: 'approved' },
  { id: "p-hikingboots", title: "방수 등산화", category: "신발류", subcategory: "등산화", condition: "이월 신품", region: "강원", qtyOnHand: 18, qtyReserved: 2, price: 59000, listPrice: 149000, channel: 'marketplace', sellerId: 's-outdoor', sellerOfRecord: "샘플아웃도어", status: 'approved' },
  { id: "p-cap", title: "야구모자 재고정리", category: "모자", subcategory: "야구모자", condition: "신품 재고", region: "인천", qtyOnHand: 80, qtyReserved: 8, price: 9000, listPrice: 29000, channel: 'marketplace', sellerId: 's-accessories', sellerOfRecord: "샘플잡화", status: 'approved' },
  { id: "p-hikinghat", title: "등산용 챙모자", category: "모자", subcategory: "등산모자", condition: "이월 신품", region: "강원", qtyOnHand: 42, qtyReserved: 3, price: 14000, listPrice: 39000, channel: 'marketplace', sellerId: 's-accessories', sellerOfRecord: "샘플잡화", status: 'approved' },
  { id: "p-silver-necklace", title: "실버 목걸이 재고정리", category: "귀금속", subcategory: "목걸이", condition: "신품 재고", region: "서울", qtyOnHand: 12, qtyReserved: 1, price: 39000, listPrice: 79000, channel: 'marketplace', sellerId: 's-jewelry', sellerOfRecord: "샘플주얼리", status: 'approved' },
  { id: "p-gold-ring", title: "14K 반지 이월 디자인", category: "귀금속", subcategory: "반지", condition: "이월 신품", region: "서울", qtyOnHand: 5, qtyReserved: 0, price: 179000, listPrice: 299000, channel: 'marketplace', sellerId: 's-jewelry', sellerOfRecord: "샘플주얼리", status: 'approved' },
  { id: "p-rice", title: "국내산 쌀 10kg 재고정리", category: "농식품", subcategory: "쌀·곡물", condition: "포장 신품", region: "충북", qtyOnHand: 40, qtyReserved: 4, price: 25000, listPrice: 35000, channel: 'marketplace', sellerId: 's-farm', sellerOfRecord: "샘플농산유통", status: 'approved' },
  { id: "p-apples", title: "사과 3kg 산지 재고정리", category: "농식품", subcategory: "과일", condition: "신선식품 예시", region: "경북", qtyOnHand: 32, qtyReserved: 2, price: 19000, listPrice: 29000, channel: 'marketplace', sellerId: 's-farm', sellerOfRecord: "샘플농산유통", status: 'approved' },
  { id: "p-kitchenware", title: "스테인리스 주방용품 세트", category: "공산품", subcategory: "주방용품", condition: "신품 재고", region: "대전", qtyOnHand: 60, qtyReserved: 6, price: 22000, listPrice: 49000, channel: 'direct', sellerId: 'platform', sellerOfRecord: "(주)대현산업 플랫폼사업부(데모 운영사)", status: 'approved' },
  { id: "p-tools", title: "가정용 공구 세트", category: "공산품", subcategory: "공구", condition: "신품 재고", region: "대구", qtyOnHand: 25, qtyReserved: 3, price: 29000, listPrice: 69000, channel: 'marketplace', sellerId: 's-industry', sellerOfRecord: "샘플공산품", status: 'approved' },
  { id: "p-refurb-tv", title: "리퍼 43인치 TV", category: "가전제품", subcategory: "리퍼 가전", condition: "리퍼브", region: "경기", qtyOnHand: 8, qtyReserved: 2, price: 189000, listPrice: 329000, channel: 'marketplace', sellerId: 's-appliances', sellerOfRecord: "샘플리퍼가전", status: 'approved' },
  { id: "p-refurb-vacuum", title: "리퍼 무선청소기", category: "가전제품", subcategory: "리퍼 가전", condition: "리퍼브", region: "인천", qtyOnHand: 10, qtyReserved: 1, price: 79000, listPrice: 189000, channel: 'marketplace', sellerId: 's-appliances', sellerOfRecord: "샘플리퍼가전", status: 'approved' },
  { id: "p-display-microwave", title: "전시 전자레인지", category: "가전제품", subcategory: "전시상품", condition: "전시", region: "부산", qtyOnHand: 4, qtyReserved: 4, price: 59000, listPrice: 129000, channel: 'marketplace', sellerId: 's-appliances', sellerOfRecord: "샘플리퍼가전", status: 'approved' }
];

export function discountPct(price, listPrice) {
  if (!(listPrice > price && price > 0)) return null;
  return Math.round((1 - price / listPrice) * 100);
}

export function availableQty(listing) {
  const onHand = Number(listing.qtyOnHand);
  const reserved = Number(listing.qtyReserved);
  if (!Number.isFinite(onHand) || !Number.isFinite(reserved) || onHand < 0 || reserved < 0) return 0;
  return Math.max(0, onHand - reserved);
}

export function inventoryConsistent(listing) {
  const onHand = Number(listing.qtyOnHand);
  const reserved = Number(listing.qtyReserved);
  return Number.isFinite(onHand) && Number.isFinite(reserved) && onHand >= 0 && reserved >= 0 && reserved <= onHand;
}

export function liveListings(rows = listings) {
  return rows.filter((x) => x.status === 'approved');
}

export function channelLabel(listing) {
  return CHANNEL_LABEL[listing.channel] || listing.channel;
}

export function liabilityParty(listing) {
  return listing.channel === 'direct' ? 'platform' : 'seller';
}

export function liabilityCopy(listing) {
  if (listing.channel === 'direct') {
    return '직접판매 설계: 주문·반품·세금계산서 책임은 플랫폼(법적 판매자)입니다. 시제품이므로 주문을 생성하거나 재고를 차감하지 않습니다.';
  }
  return '중개판매 설계: 주문·반품·세금계산서 책임은 입점 판매자(법적 판매자)입니다. 플랫폼은 중개자입니다. 시제품이므로 주문을 생성하지 않습니다.';
}

export function stockCopy(listing) {
  const available = availableQty(listing);
  return listing.condition + ' · ' + listing.region + ' · 보유 ' + listing.qtyOnHand + ' · 예약 ' + listing.qtyReserved + ' · 판매가능 ' + available;
}

/** Future order row. Does not reserve, deduct, or mark paid. */
export function freezeOrderSnapshot(listing, qtyRequested = 1) {
  const available = availableQty(listing);
  const party = liabilityParty(listing);
  return {
    kind: 'order-snapshot-draft',
    executable: false,
    listingId: listing.id,
    qtyRequested,
    qtyOnHand: listing.qtyOnHand,
    qtyReserved: listing.qtyReserved,
    qtyAvailableAtDraft: available,
    wouldOversell: qtyRequested > available,
    channel: listing.channel,
    sellerId: listing.sellerId,
    sellerOfRecord: listing.sellerOfRecord,
    price: listing.price,
    fulfillmentLiability: party,
    taxInvoiceIssuer: party,
    settlementMode: listing.channel === 'direct' ? 'platform-revenue' : 'marketplace-payable',
    paymentState: 'not-started',
    inventoryEffect: 'none'
  };
}
