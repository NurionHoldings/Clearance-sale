import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SellerDashboardNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.demo = ROOT / "seller-dashboard-demo.html"

    def test_home_links_to_existing_demo(self):
        self.assertIn('href="seller-dashboard-demo.html"', self.home)
        self.assertTrue(self.demo.is_file())

    def test_link_is_labeled_and_keyboard_visible(self):
        self.assertIn('aria-label="판매자 재고 대시보드 샘플 체험"', self.home)
        self.assertIn('header nav a:focus-visible', self.home)

    def test_demo_does_not_claim_operational_access(self):
        page = self.demo.read_text(encoding="utf-8")
        self.assertIn("시연 전용", page)
        self.assertIn("서버 통신 없음", page)


if __name__ == "__main__":
    unittest.main()
