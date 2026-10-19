import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "seller-dashboard-demo.html"


class SellerDashboardDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")

    def test_sample_only_disclosure(self):
        self.assertIn("시연 전용", self.page)
        self.assertIn("가상 데이터", self.page)
        self.assertIn("운영 사용 금지", self.page)

    def test_accessible_controls_and_mobile_layout(self):
        for token in ('id="status"', 'id="threshold"', 'aria-live="polite"', '@media(max-width:600px)'):
            with self.subTest(token=token):
                self.assertIn(token, self.page)

    def test_read_only_without_remote_requests(self):
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "WebSocket", "<form"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.page)

    def test_dashboard_navigation_and_safe_dom_updates(self):
        self.assertIn('id="metrics"', self.page)
        self.assertIn('id="alerts"', self.page)
        self.assertIn('id="products"', self.page)
        self.assertIn('replaceChildren(', self.page)
        self.assertNotIn('innerHTML', self.page)

    def test_status_badge_only_in_status_column(self):
        self.assertIn('for(const [column,value] of', self.page)
        self.assertIn('if(column===5)', self.page)
        self.assertNotIn('if(value===statusText)', self.page)

    def test_accessible_table_and_filtered_result_announcement(self):
        self.assertIn('<caption class="muted">가상 상품 재고 목록', self.page)
        self.assertIn('id="result-count" class="muted" role="status" aria-live="polite"', self.page)
        self.assertIn('$("result-count").textContent=', self.page)

    def test_product_draft_preview_korean_validation(self):
        for token in ('id="draft-sku"', 'id="draft-name"', 'id="draft-price"',
                      'id="draft-stock"', 'id="draft-reserved"',
                      'id="draft-preview"', 'id="draft-errors"',
                      '이미 등록된 상품 코드입니다.', '등록 전 검사',
                      '실제 상품 등록은 진행되지 않았습니다.'):
            with self.subTest(token=token):
                self.assertIn(token, self.page)
        self.assertIn('source.some(item=>item.sku.trim()===sku)', self.page)
        self.assertIn('document.createElement("li")', self.page)

    def test_inventory_statuses(self):
        for status in ("active", "inactive", "low_stock", "out_of_stock"):
            self.assertIn('value="' + status + '"', self.page)


if __name__ == "__main__":
    unittest.main()
