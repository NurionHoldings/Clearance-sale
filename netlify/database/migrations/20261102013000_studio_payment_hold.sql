ALTER TABLE live_invoices DROP CONSTRAINT live_invoices_status_check;
ALTER TABLE live_invoices ADD CONSTRAINT live_invoices_status_check CHECK(status IN ('created','confirming','paid','refund_pending','refunded','void','review_required'));
