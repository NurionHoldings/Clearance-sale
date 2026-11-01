export const MAX_VENDORS = 100;
export const MAX_PRODUCTS_PER_VENDOR = 50;
export const activeVendors = (known, apps) => [...known, ...apps.filter(a => a.status !== 'rejected')];
export const vendorSlots = (known, apps) => Math.max(0, MAX_VENDORS - activeVendors(known, apps).length);
const nameKey = name => String(name).normalize('NFKC').replace(/\s+/g, '').toLowerCase();
export function applicationError(known, apps, name, replacingId = null) {
 const others = apps.filter(a => a.id !== replacingId);
 if (activeVendors(known, others).some(v => nameKey(v.name) === nameKey(name))) return '이미 등록되었거나 심사 중인 업체명입니다.';
 if (!vendorSlots(known, others)) return '입점 정원 100개가 찼습니다. 심사 대기 업체도 정원에 포함됩니다.';
 return '';
}
export const vendorProductCount = (rows, id) => rows.filter(p => p.sellerId === id).length;
export function draftError(vendors, rows, draft) {
 if (!vendors.some(v => v.id === draft.sellerId)) return '승인된 체험 업체를 선택하세요.';
 if (vendorProductCount(rows, draft.sellerId) >= MAX_PRODUCTS_PER_VENDOR) return '이 업체는 상품 등록 한도 50개에 도달했습니다.';
 if (!draft.title?.trim() || draft.title.length > 80) return '상품명은 1~80자로 입력하세요.';
 if (!Number.isSafeInteger(draft.price) || draft.price < 1) return '가격은 1원 이상의 정수로 입력하세요.';
 if (!Number.isSafeInteger(draft.quantity) || draft.quantity < 0) return '수량은 0 이상의 정수로 입력하세요.';
 return '';
}
