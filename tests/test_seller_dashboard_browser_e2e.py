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

    def test_inventory_search_combines_with_status_and_preview(self):
        search = self.page.locator("#product-search")
        search.fill("A-101")
        self.assertEqual(self.page.locator("#products tr").count(), 1)
        self.assertIn("가전 전시상품", self.page.locator("#products").inner_text())
        self.page.locator("#status").select_option("out_of_stock")
        self.assertEqual(self.page.locator("#products tr").count(), 0)
        self.page.locator("#status").select_option("all")
        search.fill("시연 상품")
        self.assertEqual(self.page.locator("#products tr").count(), 0)
        self.page.locator("#draft-preview").click()
        self.assertEqual(self.page.locator("#products tr").count(), 1)
        self.assertIn("미등록 시연", self.page.locator("#products").inner_text())
        self.page.locator("#clear-draft-preview").click()
        self.assertEqual(self.page.locator("#products tr").count(), 0)
        search.fill("")
        self.assertEqual(self.page.locator("#products tr").count(), 5)

    def test_inventory_sorting_and_empty_result_guidance(self):
        self.page.locator("#sort-order").select_option("available_asc")
        self.assertEqual(self.page.locator("#products tr").first.locator("td").first.inner_text(), "C-303")
        self.page.locator("#sort-order").select_option("available_desc")
        self.assertEqual(self.page.locator("#products tr").first.locator("td").first.inner_text(), "A-101")
        self.page.locator("#product-search").fill("존재하지않는상품")
        self.assertEqual(self.page.locator("#products tr").count(), 0)
        self.assertIn("검색어와 일치하는 상품이 없습니다.", self.page.locator("#empty").inner_text())
        self.page.locator("#product-search").fill("")
        self.page.locator("#status").select_option("inactive")
        self.page.locator("#product-search").fill("A-101")
        self.assertIn("검색어와 일치하는 상품이 없습니다.", self.page.locator("#empty").inner_text())

    def test_quick_inventory_filters_and_reset(self):
        self.page.locator("#product-search").fill("A-101")
        self.page.locator("#show-low-stock").click()
        self.assertEqual(self.page.locator("#status").input_value(), "low_stock")
        self.assertEqual(self.page.locator("#product-search").input_value(), "")
        self.assertEqual(self.page.locator("#products tr").count(), 2)
        self.page.locator("#show-out-of-stock").click()
        self.assertEqual(self.page.locator("#status").input_value(), "out_of_stock")
        self.assertEqual(self.page.locator("#products tr").count(), 1)
        self.page.locator("#sort-order").select_option("available_desc")
        self.page.locator("#reset-inventory-filters").click()
        self.assertEqual(self.page.locator("#status").input_value(), "all")
        self.assertEqual(self.page.locator("#sort-order").input_value(), "sku_asc")
        self.assertEqual(self.page.locator("#products tr").count(), 5)

    def test_stock_severity_and_accessible_product_details(self):
        self.assertIn("긴급 · 품절", self.page.locator("#alerts").inner_text())
        self.assertIn("주의 · 재고 부족", self.page.locator("#alerts").inner_text())
        details = self.page.locator("#products tr").first.locator("details")
        self.assertFalse(details.evaluate("(el) => el.open"))
        details.locator("summary").click()
        self.assertTrue(details.evaluate("(el) => el.open"))
        self.assertIn("예약: 3개", details.inner_text())
        self.assertIn("가상 샘플 데이터", details.inner_text())
        self.page.locator("#draft-preview").click()
        preview = self.page.locator("#products tr").filter(has_text="미등록 시연")
        preview.locator("summary").click()
        self.assertIn("임시 시연 데이터", preview.inner_text())

    def test_mobile_inventory_cards_and_stock_meters(self):
        self.page.set_viewport_size({"width": 375, "height": 812})
        self.assertEqual(self.page.locator("#products tr").count(), 5)
        self.assertEqual(self.page.locator("#products progress").count(), 4)
        first = self.page.locator("#products tr").first
        self.assertEqual(first.locator('td[data-label="상품 코드"]').count(), 1)
        self.assertEqual(first.locator("progress").get_attribute("max"), "12")
        self.assertEqual(first.locator("progress").get_attribute("value"), "9")
        self.assertEqual(self.page.locator("thead").evaluate("(el) => getComputedStyle(el).display"), "none")
        self.assertEqual(first.evaluate("(el) => getComputedStyle(el).display"), "block")
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"),
            self.page.evaluate("window.innerWidth"),
        )

    def test_mobile_filters_and_active_filter_summary(self):
        self.page.set_viewport_size({"width": 375, "height": 812})
        self.assertIn("전체", self.page.locator("#active-filters").inner_text())
        self.page.locator("#product-search").fill("의류")
        self.page.locator("#sort-order").select_option("available_asc")
        summary = self.page.locator("#active-filters").inner_text()
        self.assertIn("검색어: 의류", summary)
        self.assertIn("판매 가능 적은 순", summary)
        self.assertEqual(self.page.locator("#products tr").count(), 1)
        self.page.locator("#show-low-stock").click()
        self.assertNotIn("검색어:", self.page.locator("#active-filters").inner_text())
        self.assertIn("재고 부족", self.page.locator("#active-filters").inner_text())
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"),
            self.page.evaluate("window.innerWidth"),
        )

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
