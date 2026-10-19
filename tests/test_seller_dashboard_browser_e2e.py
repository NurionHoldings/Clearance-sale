"""Optional real-browser regression for the standalone read-only seller demo.

Run: python -m unittest tests.test_seller_dashboard_browser_e2e -v
Requires locally installed playwright and Chromium. Missing dependencies skip safely.
No server, network, credentials, or production data are required.
"""
import unittest
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "seller-dashboard-demo.html"

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


@unittest.skipUnless(sync_playwright is not None, "Playwright is not installed")
class SellerDashboardBrowserE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.manager = sync_playwright()
            cls.playwright = cls.manager.start()
            cls.browser = cls.playwright.chromium.launch(headless=True)
        except Exception as exc:
            if hasattr(cls, "manager"):
                cls.manager.stop()
            raise unittest.SkipTest("Chromium unavailable: " + str(exc))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.manager.stop()

    def setUp(self):
        self.page = self.browser.new_page()
        self.page.goto(PAGE.as_uri())
        self.assertIn("전체 5개", self.page.locator("#result-count").inner_text())

    def tearDown(self):
        self.page.close()

    def test_preview_edit_recheck_and_reset(self):
        self.page.locator("#draft-preview").click()
        self.assertIn("전체 6개", self.page.locator("#result-count").inner_text())
        self.assertEqual(self.page.locator("#products tr").count(), 6)
        self.assertEqual(self.page.get_by_text("(미등록 시연)", exact=False).count(), 1)
        self.assertTrue(self.page.locator("#preview-disclosure").is_visible())

        self.page.locator("#draft-name").fill("수정된 시연 상품")
        self.assertIn("전체 5개", self.page.locator("#result-count").inner_text())
        self.assertFalse(self.page.locator("#preview-disclosure").is_visible())
        self.assertEqual(self.page.locator("#draft-result").inner_text(), "")

        self.page.locator("#draft-preview").click()
        self.assertIn("전체 6개", self.page.locator("#result-count").inner_text())
        self.assertIn("수정된 시연 상품", self.page.locator("#products").inner_text())
        self.page.locator("#clear-draft-preview").click()
        self.assertIn("전체 5개", self.page.locator("#result-count").inner_text())
        self.assertFalse(self.page.locator("#preview-disclosure").is_visible())

    def test_invalid_input_and_reload_do_not_persist(self):
        self.page.locator("#draft-sku").fill("A-101")
        self.page.locator("#draft-preview").click()
        self.assertIn("이미 등록된 상품 코드입니다.", self.page.locator("#draft-errors").inner_text())
        self.assertIn("전체 5개", self.page.locator("#result-count").inner_text())
        self.page.locator("#draft-sku").fill("NEW-002")
        self.page.locator("#draft-stock").fill("1")
        self.page.locator("#draft-reserved").fill("2")
        self.page.locator("#draft-preview").click()
        self.assertIn("예약 수량은 보유 수량을 초과할 수 없습니다.", self.page.locator("#draft-errors").inner_text())
        self.assertIn("전체 5개", self.page.locator("#result-count").inner_text())
        self.page.locator("#draft-reserved").fill("0")
        self.page.locator("#draft-preview").click()
        self.assertIn("전체 6개", self.page.locator("#result-count").inner_text())
        self.page.reload()
        self.assertIn("전체 5개", self.page.locator("#result-count").inner_text())
        self.assertFalse(self.page.locator("#preview-disclosure").is_visible())

    def test_filters_include_ephemeral_item_without_storage(self):
        self.page.locator("#draft-stock").fill("0")
        self.page.locator("#draft-preview").click()
        self.page.locator("#status").select_option("out_of_stock")
        self.assertEqual(self.page.locator("#products tr").count(), 2)
        self.assertIn("미등록 시연", self.page.locator("#products").inner_text())
        self.page.locator("#clear-draft-preview").click()
        self.assertEqual(self.page.locator("#products tr").count(), 1)


if __name__ == "__main__":
    unittest.main()
