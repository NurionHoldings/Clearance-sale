import os
import tempfile
import unittest
from backend.core import (connect,create_seller,authenticate,principal,create_product,
                          list_products,add_variant,reserve,release,create_order,mark_order_paid,
                          cancel_order,get_order,seller_dashboard,seller_orders,Denied,Conflict)

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
    def test_order_paid_commits_inventory_once(self):
        pid=create_product(self.db,self.pa,'운동화','신발',30000)
        vid=add_variant(self.db,self.pa,pid,'RUN-260',3)
        rid=reserve(self.db,self.pa,vid,2,'reserve-paid')
        oid=create_order(self.db,self.pa,rid,'order-paid')
        self.assertEqual(oid,create_order(self.db,self.pa,rid,'order-paid'))
        mark_order_paid(self.db,self.pa,oid)
        mark_order_paid(self.db,self.pa,oid)
        stock=self.db.execute("SELECT on_hand,reserved FROM variants WHERE id=?",(vid,)).fetchone()
        self.assertEqual(stock,(1,0))
        self.assertEqual(get_order(self.db,self.pa,oid)[2],'paid')
        with self.assertRaises(Conflict):
            cancel_order(self.db,self.pa,oid)
    def test_order_cancel_releases_inventory(self):
        pid=create_product(self.db,self.pa,'재킷','의류',20000)
        vid=add_variant(self.db,self.pa,pid,'JACKET-M',4)
        rid=reserve(self.db,self.pa,vid,1,'reserve-cancel')
        oid=create_order(self.db,self.pa,rid,'order-cancel')
        cancel_order(self.db,self.pa,oid)
        cancel_order(self.db,self.pa,oid)
        stock=self.db.execute("SELECT on_hand,reserved FROM variants WHERE id=?",(vid,)).fetchone()
        self.assertEqual(stock,(4,0))
        self.assertEqual(get_order(self.db,self.pa,oid)[2],'cancelled')
        with self.assertRaises(Conflict):
            mark_order_paid(self.db,self.pa,oid)
    def test_order_tenant_isolation(self):
        pid=create_product(self.db,self.pa,'헬멧','라이더용품',45000)
        vid=add_variant(self.db,self.pa,pid,'HELMET-L',1)
        rid=reserve(self.db,self.pa,vid,1,'reserve-isolation')
        oid=create_order(self.db,self.pa,rid,'order-isolation')
        with self.assertRaises(Denied):
            get_order(self.db,self.pb,oid)
        with self.assertRaises(Denied):
            mark_order_paid(self.db,self.pb,oid)
    def test_seller_dashboard_isolation(self):
        pid=create_product(self.db,self.pa,'재킷','의류',20000)
        vid=add_variant(self.db,self.pa,pid,'JACKET-XL',5)
        rid=reserve(self.db,self.pa,vid,2,'dashboard-reserve')
        create_order(self.db,self.pa,rid,'dashboard-order')
        a=seller_dashboard(self.db,self.pa)
        b=seller_dashboard(self.db,self.pb)
        self.assertEqual(a['stock'],{'on_hand':5,'reserved':2,'available':3})
        self.assertEqual(b['stock'],{'on_hand':0,'reserved':0,'available':0})
        self.assertEqual(a['orders']['pending_payment'],1)
        self.assertEqual(b['orders'],{})
        self.assertEqual(len(seller_orders(self.db,self.pa)),1)
        self.assertEqual(seller_orders(self.db,self.pb),[])
        self.assertFalse(a['payment_verified'])
        with self.assertRaises(ValueError): seller_orders(self.db,self.pa,101)

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
