"""Clearance-sale P0 backend foundation (stdlib only).

Local development only. No live PG, public signup, or production deployment.
Run: python -m unittest discover -s tests
"""
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sellers (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, status TEXT NOT NULL
 CHECK(status IN ('applied','approved','suspended')));
CREATE TABLE IF NOT EXISTS users (
 id TEXT PRIMARY KEY, seller_id TEXT NOT NULL REFERENCES sellers(id),
 username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
 role TEXT NOT NULL CHECK(role IN ('seller_admin','seller_staff')));
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id),
 expires_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS products (
 id TEXT PRIMARY KEY, seller_id TEXT NOT NULL REFERENCES sellers(id),
 name TEXT NOT NULL, category TEXT NOT NULL, price INTEGER NOT NULL CHECK(price>=0),
 status TEXT NOT NULL CHECK(status IN ('draft','listed','blocked')),
 UNIQUE(id,seller_id));
CREATE TABLE IF NOT EXISTS variants (
 id TEXT PRIMARY KEY, product_id TEXT NOT NULL, seller_id TEXT NOT NULL,
 sku TEXT NOT NULL, on_hand INTEGER NOT NULL CHECK(on_hand>=0),
 reserved INTEGER NOT NULL DEFAULT 0 CHECK(reserved>=0 AND reserved<=on_hand),
 FOREIGN KEY(product_id,seller_id) REFERENCES products(id,seller_id),
 UNIQUE(seller_id,sku), UNIQUE(id,seller_id));
CREATE TABLE IF NOT EXISTS stock_reservations (
 id TEXT PRIMARY KEY, seller_id TEXT NOT NULL, variant_id TEXT NOT NULL,
 quantity INTEGER NOT NULL CHECK(quantity>0),
 idempotency_key TEXT NOT NULL, status TEXT NOT NULL
 CHECK(status IN ('held','released','committed')),
 FOREIGN KEY(variant_id,seller_id) REFERENCES variants(id,seller_id),
 UNIQUE(seller_id,idempotency_key));
CREATE TABLE IF NOT EXISTS audit_events (
 id TEXT PRIMARY KEY, seller_id TEXT NOT NULL, actor_id TEXT NOT NULL,
 event TEXT NOT NULL, subject_id TEXT NOT NULL, created_at INTEGER NOT NULL);
"""
CATEGORIES = ('의류','모자','신발','운동복','특정 스포츠 동호회 용품','라이더용품')

class Denied(Exception): pass
class Conflict(Exception): pass

def connect(path):
    db = sqlite3.connect(path, timeout=10, isolation_level=None)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=10000")
    db.executescript(SCHEMA)
    return db

@contextmanager
def transaction(db):
    db.execute("BEGIN IMMEDIATE")
    try:
        yield
        db.commit()
    except BaseException:
        db.rollback()
        raise

def password_hash(password):
    if len(password)<12: raise ValueError("minimum 12 characters")
    salt=os.urandom(16)
    digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,310000)
    return "pbkdf2_sha256$310000$"+salt.hex()+"$"+digest.hex()

def verify_password(password, encoded):
    try:
        algorithm, iterations, salt, expected=encoded.split("$")
        if algorithm!="pbkdf2_sha256": return False
        got=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),int(iterations))
        return hmac.compare_digest(got,bytes.fromhex(expected))
    except (ValueError,TypeError):
        return False

def create_seller(db, name, username, password):
    if not name.strip() or not username.strip(): raise ValueError("name and username required")
    sid,uid=secrets.token_hex(16),secrets.token_hex(16)
    hashed=password_hash(password)
    with transaction(db):
        db.execute("INSERT INTO sellers VALUES (?,?,?)",(sid,name.strip(),'applied'))
        db.execute("INSERT INTO users VALUES (?,?,?,?,?)",(uid,sid,username,hashed,'seller_admin'))
    return sid

def authenticate(db, username, password):
    row=db.execute("SELECT id,password_hash FROM users WHERE username=?",(username,)).fetchone()
    if not row or not verify_password(password,row[1]): raise Denied("invalid credentials")
    token=secrets.token_urlsafe(32)
    db.execute("INSERT INTO sessions VALUES (?,?,?)",
               (hashlib.sha256(token.encode()).hexdigest(),row[0],int(time.time())+3600))
    return token

def principal(db, token):
    if not token: raise Denied("authentication required")
    row=db.execute("""SELECT u.id,u.seller_id,u.role,s.status FROM sessions t
       JOIN users u ON t.user_id=u.id JOIN sellers s ON s.id=u.seller_id
       WHERE t.token_hash=? AND t.expires_at>?""",
       (hashlib.sha256(token.encode()).hexdigest(),int(time.time()))).fetchone()
    if not row or row[3]!='approved': raise Denied("approved seller required")
    return dict(zip(('user_id','seller_id','role','seller_status'),row))

def _audit(db,p,event,subject):
    db.execute("INSERT INTO audit_events VALUES (?,?,?,?,?,?)",
               (secrets.token_hex(16),p['seller_id'],p['user_id'],event,subject,int(time.time())))

def create_product(db,p,name,category,price):
    if p['role']!='seller_admin': raise Denied("admin required")
    if category not in CATEGORIES or not name.strip() or not isinstance(price,int) or isinstance(price,bool) or price<0:
        raise ValueError("invalid product")
    pid=secrets.token_hex(16)
    with transaction(db):
        db.execute("INSERT INTO products VALUES (?,?,?,?,?,?)",
                   (pid,p['seller_id'],name.strip(),category,price,'draft'))
        _audit(db,p,'product.created',pid)
    return pid

def list_products(db,p):
    return db.execute("SELECT id,name,category,price,status FROM products WHERE seller_id=? ORDER BY name",
                      (p['seller_id'],)).fetchall()

def add_variant(db,p,product_id,sku,on_hand):
    if p['role']!='seller_admin': raise Denied("admin required")
    if not sku.strip() or not isinstance(on_hand,int) or isinstance(on_hand,bool) or on_hand<0:
        raise ValueError("invalid stock")
    vid=secrets.token_hex(16)
    with transaction(db):
        owner=db.execute("SELECT id FROM products WHERE id=? AND seller_id=?",
                         (product_id,p['seller_id'])).fetchone()
        if not owner: raise Denied("product not owned")
        db.execute("INSERT INTO variants(id,product_id,seller_id,sku,on_hand) VALUES (?,?,?,?,?)",
                   (vid,product_id,p['seller_id'],sku.strip(),on_hand))
        _audit(db,p,'variant.created',vid)
    return vid

def reserve(db,p,variant_id,quantity,key):
    """Internal stock reservation primitive, not a public checkout endpoint.

    Requires an authenticated approved seller principal. Payment and order state
    machines are intentionally not implemented in this milestone.
    """
    if not isinstance(quantity,int) or isinstance(quantity,bool) or quantity<=0 or not key:
        raise ValueError("invalid reservation")
    with transaction(db):
        prior=db.execute("SELECT id,variant_id,quantity FROM stock_reservations WHERE seller_id=? AND idempotency_key=?",
                         (p['seller_id'],key)).fetchone()
        if prior:
            if prior[1:]!=(variant_id,quantity): raise Conflict("idempotency mismatch")
            return prior[0]
        changed=db.execute("""UPDATE variants SET reserved=reserved+?
          WHERE id=? AND seller_id=? AND on_hand-reserved>=?""",
          (quantity,variant_id,p['seller_id'],quantity)).rowcount
        if changed!=1: raise Conflict("insufficient stock or wrong seller")
        rid=secrets.token_hex(16)
        db.execute("INSERT INTO stock_reservations VALUES (?,?,?,?,?,?)",
                   (rid,p['seller_id'],variant_id,quantity,key,'held'))
        _audit(db,p,'stock.reserved',rid)
        return rid

def release(db,p,reservation_id):
    with transaction(db):
        row=db.execute("SELECT variant_id,quantity,status FROM stock_reservations WHERE id=? AND seller_id=?",
                       (reservation_id,p['seller_id'])).fetchone()
        if not row: raise Denied("reservation not owned")
        if row[2]=='released': return
        if row[2]!='held': raise Conflict("committed reservation")
        db.execute("UPDATE variants SET reserved=reserved-? WHERE id=? AND seller_id=?",
                   (row[1],row[0],p['seller_id']))
        db.execute("UPDATE stock_reservations SET status='released' WHERE id=? AND seller_id=?",
                   (reservation_id,p['seller_id']))
        _audit(db,p,'stock.released',reservation_id)
