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

    def test_inventory_statuses(self):
        for status in ("active", "inactive", "low_stock", "out_of_stock"):
            self.assertIn('value="' + status + '"', self.page)


if __name__ == "__main__":
    unittest.main()
