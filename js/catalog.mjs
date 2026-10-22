export const CHANNEL_LABEL = {
  direct: '플랫폼 직접판매',
  marketplace: '입점업체 중개판매'
};

export const listings = [
  { id: 'p-appliance', title: '전시 가전 특가 세트', category: '가전', condition: '전시', region: '경기', qtyOnHand: 4, qtyReserved: 1, price: 189000, listPrice: 320000, channel: 'marketplace', sellerId: 's-home', sellerOfRecord: '샘플가전 정리', status: 'approved' },
  { id: 'p-fashion', title: '시즌오프 의류 묶음', category: '패션', condition: '시즌오프', region: '서울', qtyOnHand: 20, qtyReserved: 0, price: 49000, listPrice: 120000, channel: 'direct', sellerId: 'platform', sellerOfRecord: '땡처리 마켓(데모 운영사)', status: 'approved' },
  { id: 'p-chair', title: '사무용 의자 재고정리', category: '가구', condition: '신품', region: '인천', qtyOnHand: 12, qtyReserved: 3, price: 39000, listPrice: 89000, channel: 'marketplace', sellerId: 's-office', sellerOfRecord: '샘플오피스', status: 'approved' },
  { id: 'p-kitchen', title: '식당 주방집기 패키지', category: '산업·사업용', condition: '중고', region: '부산', qtyOnHand: 2, qtyReserved: 2, price: 550000, listPrice: 900000, channel: 'marketplace', sellerId: 's-food', sellerOfRecord: '샘플외식자재', status: 'approved' },
  { id: 'p-living', title: '생활용품 재고 박스', category: '생활', condition: '리퍼브', region: '대전', qtyOnHand: 8, qtyReserved: 0, price: 29000, listPrice: 65000, channel: 'direct', sellerId: 'platform', sellerOfRecord: '땡처리 마켓(데모 운영사)', status: 'approved' },
  { id: 'p-tool', title: '공구 세트 창고정리', category: '산업·사업용', condition: '신품', region: '대구', qtyOnHand: 6, qtyReserved: 1, price: 75000, listPrice: 150000, channel: 'marketplace', sellerId: 's-tool', sellerOfRecord: '샘플공구', status: 'approved' }
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
