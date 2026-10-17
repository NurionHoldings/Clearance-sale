import os
import tempfile
import unittest
from backend.core import (connect,create_seller,authenticate,principal,create_product,
                          list_products,add_variant,reserve,release,Denied,Conflict)

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=connect(os.path.join(self.tmp.name,'test.db'))
        self.a=create_seller(self.db,'A','seller_a','correct-horse-battery-A')
        self.b=create_seller(self.db,'B','seller_b','correct-horse-battery-B')
        self.db.execute("UPDATE sellers SET status='approved'")
        self.pa=principal(self.db,authenticate(self.db,'seller_a','correct-horse-battery-A'))
        self.pb=principal(self.db,authenticate(self.db,'seller_b','correct-horse-battery-B'))
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def test_pending_seller_denied(self):
        self.db.execute("UPDATE sellers SET status='applied' WHERE id=?",(self.a,))
        with self.assertRaises(Denied):
            principal(self.db,authenticate(self.db,'seller_a','correct-horse-battery-A'))
    def test_tenant_product_isolation(self):
        pid=create_product(self.db,self.pa,'신발','신발',20000)
        self.assertEqual(len(list_products(self.db,self.pa)),1)
        self.assertEqual(len(list_products(self.db,self.pb)),0)
        with self.assertRaises(Denied):
            add_variant(self.db,self.pb,pid,'SKU-1',3)
    def test_atomic_stock_reservation_and_idempotency(self):
        pid=create_product(self.db,self.pa,'모자','모자',9000)
        vid=add_variant(self.db,self.pa,pid,'CAP-BLACK',2)
        rid=reserve(self.db,self.pa,vid,2,'order-1')
        self.assertEqual(rid,reserve(self.db,self.pa,vid,2,'order-1'))
        with self.assertRaises(Conflict):
            reserve(self.db,self.pa,vid,1,'order-2')
        with self.assertRaises(Conflict):
            reserve(self.db,self.pa,vid,1,'order-1')
        with self.assertRaises(Conflict):
            reserve(self.db,self.pb,vid,1,'other-seller')
        release(self.db,self.pa,rid)
        release(self.db,self.pa,rid)
        self.assertEqual(self.db.execute("SELECT reserved FROM variants WHERE id=?",(vid,)).fetchone()[0],0)
    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            create_product(self.db,self.pa,'상품','신발',-1)
        pid=create_product(self.db,self.pa,'상품','신발',1)
        with self.assertRaises(ValueError):
            add_variant(self.db,self.pa,pid,'SKU',-1)
    def test_failed_auth(self):
        with self.assertRaises(Denied):
            authenticate(self.db,'seller_a','wrong')

if __name__=='__main__':
    unittest.main()
