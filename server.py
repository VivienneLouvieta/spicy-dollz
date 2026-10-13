#!/usr/bin/env python3
"""
Spicy Dollz backend: accounts, wallet + payments (Stripe), uploads.

Run:   python3 server.py            (listens on PORT, default 8000)
Env:
  STRIPE_SECRET_KEY       sk_test_... or sk_live_...  -> real card payments via Stripe Checkout
  STRIPE_WEBHOOK_SECRET   whsec_...                   -> optional, verifies /api/stripe/webhook
  PAYMENTS_TEST_MODE      1/0  (default 1 when no Stripe key) -> instant fake top-ups for testing
  SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASS SMTP_FROM   -> password reset emails
  PLATFORM_FEE_PCT        0..50 (default 0) -> share of tips/subscriptions kept by the platform
  TRUST_VISITOR_HEADER    1/0 (default 1) -> restore sessions from the X-Visitor-Id proxy header
  SECRET_KEY              signing key for media links (random per-install if unset; stored in data/)
  DATA_DIR                default ./data
"""
import base64, hashlib, hmac, json, os, re, secrets, smtplib, sqlite3, subprocess, threading, time, uuid
import shutil
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get("DATA_DIR", ROOT / "data"))
MEDIA = DATA / "media"
for d in (DATA, MEDIA, MEDIA / "img", MEDIA / "vid", MEDIA / "thumb"):
    d.mkdir(parents=True, exist_ok=True)

_sk = DATA / ".secret"
if os.environ.get("SECRET_KEY"):
    SECRET = os.environ["SECRET_KEY"].encode()
else:
    if not _sk.exists():
        _sk.write_text(secrets.token_hex(32))
    SECRET = _sk.read_text().strip().encode()

STRIPE_KEY = os.environ.get("STRIPE_SECRET_KEY", "").strip()
STRIPE_WHSEC = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
TEST_MODE = os.environ.get("PAYMENTS_TEST_MODE", "0" if STRIPE_KEY else "1") == "1"
FEE = max(0.0, min(50.0, float(os.environ.get("PLATFORM_FEE_PCT", "0")))) / 100
TRUST_VISITOR = os.environ.get("TRUST_VISITOR_HEADER", "1") == "1"
HAS_FFPROBE = subprocess.run(["which", "ffprobe"], capture_output=True).returncode == 0

# ---------- catalogue (server is the source of truth for prices) ----------
PACKS = [(105, 99), (174, 199), (258, 299), (450, 499), (894, 999), (1794, 1999)]  # coins, cents
PLANS = [("1 Month", 160, 1), ("3 Months", 399, 3), ("12 Months", 1199, 12)]       # name, cents, months
FRAMES = [("Comic Noir", 100), ("Pixel Chase", 150), ("Ruby Star", 120), ("Aqua Wing", 200), ("Film Roll", 180),
          ("Neon Arcade", 250), ("Sapphire Hat", 350), ("Wolf Scythe", 400), ("Moon Butterfly", 450),
          ("Jelly Glow", 300), ("Galaxy Orbit", 500)]
BANNERS = ["Spicy Dollz", "Neon Bunny", "Ink Duo", "Game Over", "Glitch Screen", "Pink Booth", "Crimson Edge", "Moonlit Yard"]
BANNER_PRICE = 99
SUB_PRICE = 900          # coins per month for a creator subscription
DAY = 86400000
BASES = ("dragon", "lime", "mint", "cobalt", "citron")
MONEY_KEYS = {"coins", "usd", "own", "prem", "tx", "st", "mv", "frv", "unread", "earned", "testmode"}

# ---------- database ----------
DB_PATH = DATA / "spicy.db"
_lock = threading.RLock()
db = sqlite3.connect(DB_PATH, check_same_thread=False, isolation_level=None)
db.row_factory = sqlite3.Row
db.execute("PRAGMA journal_mode=WAL")
db.execute("PRAGMA foreign_keys=ON")
db.executescript("""
CREATE TABLE IF NOT EXISTS users(
  id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, name_l TEXT UNIQUE NOT NULL,
  handle TEXT UNIQUE NOT NULL, handle_l TEXT UNIQUE NOT NULL, base TEXT NOT NULL,
  salt TEXT NOT NULL, pw TEXT NOT NULL, created INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS sessions(token_h TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  visitor TEXT, created INTEGER NOT NULL, seen INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS ix_sess_vis ON sessions(visitor);
CREATE TABLE IF NOT EXISTS oauth(provider TEXT NOT NULL, sub TEXT NOT NULL, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY(provider,sub));
CREATE TABLE IF NOT EXISTS kv(user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, k TEXT NOT NULL, v TEXT NOT NULL,
  PRIMARY KEY(user_id,k));
CREATE TABLE IF NOT EXISTS wallets(user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  coins INTEGER NOT NULL DEFAULT 0, usd_c INTEGER NOT NULL DEFAULT 0, earned INTEGER NOT NULL DEFAULT 0,
  tips_c INTEGER NOT NULL DEFAULT 0, subs_c INTEGER NOT NULL DEFAULT 0, gifts_c INTEGER NOT NULL DEFAULT 0,
  own TEXT NOT NULL DEFAULT '[]', prem INTEGER NOT NULL DEFAULT 0, unread INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS tx(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  k TEXT NOT NULL, t TEXT NOT NULL, n TEXT NOT NULL, a REAL NOT NULL, c INTEGER, m TEXT, d INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS ix_tx_user ON tx(user_id, d);
CREATE TABLE IF NOT EXISTS subs(subscriber TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  creator TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, expires INTEGER NOT NULL, PRIMARY KEY(subscriber,creator));
CREATE TABLE IF NOT EXISTS videos(id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  caption TEXT, aud TEXT NOT NULL, dur REAL NOT NULL, file TEXT NOT NULL, thumb TEXT, mime TEXT, views INTEGER DEFAULT 0, created INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS payments(id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  kind TEXT NOT NULL, item INTEGER NOT NULL, cents INTEGER NOT NULL, provider TEXT NOT NULL, ext_id TEXT,
  status TEXT NOT NULL, created INTEGER NOT NULL, credited INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS withdrawals(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  usd_c INTEGER NOT NULL, coins INTEGER NOT NULL, token TEXT, net TEXT, addr TEXT, status TEXT NOT NULL, created INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS resets(token_h TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS likes(user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, video_id TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  created INTEGER NOT NULL, PRIMARY KEY(user_id, video_id));
CREATE INDEX IF NOT EXISTS ix_likes_v ON likes(video_id);
CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY AUTOINCREMENT, video_id TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, text TEXT NOT NULL, created INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS ix_cm_v ON comments(video_id, created);
CREATE TABLE IF NOT EXISTS follows(follower TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, followee TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created INTEGER NOT NULL, PRIMARY KEY(follower, followee));
CREATE INDEX IF NOT EXISTS ix_fol_e ON follows(followee);
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, from_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  to_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, text TEXT NOT NULL, created INTEGER NOT NULL, read_at INTEGER);
CREATE INDEX IF NOT EXISTS ix_msg_pair ON messages(from_id, to_id, created);
CREATE INDEX IF NOT EXISTS ix_msg_to ON messages(to_id, read_at);
CREATE TABLE IF NOT EXISTS blocks(blocker TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, blocked TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY(blocker, blocked));
CREATE TABLE IF NOT EXISTS notifs(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  kind TEXT NOT NULL, actor_id TEXT, video_id TEXT, text TEXT, created INTEGER NOT NULL, read INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS ix_nt_u ON notifs(user_id, created);
CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY AUTOINCREMENT, reporter TEXT REFERENCES users(id) ON DELETE SET NULL,
  video_id TEXT, target_user TEXT, comment_id INTEGER, reason TEXT, status TEXT NOT NULL DEFAULT 'open', created INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS daily(user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, day TEXT NOT NULL,
  views INTEGER NOT NULL DEFAULT 0, likes INTEGER NOT NULL DEFAULT 0, followers INTEGER NOT NULL DEFAULT 0, subs INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(user_id, day));
""")


def _addcol(table, col, ddl):
    cols = [r[1] for r in db.execute(f"PRAGMA table_info({table})").fetchall()]
    if col not in cols:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


_addcol("videos", "kind", "kind TEXT NOT NULL DEFAULT 'video'")
_addcol("videos", "tags", "tags TEXT NOT NULL DEFAULT '[]'")
_addcol("videos", "removed", "removed INTEGER NOT NULL DEFAULT 0")
_addcol("users", "role", "role TEXT NOT NULL DEFAULT 'user'")
_addcol("users", "banned", "banned INTEGER NOT NULL DEFAULT 0")
db.execute("CREATE INDEX IF NOT EXISTS ix_vid_user ON videos(user_id, created)")
db.execute("CREATE INDEX IF NOT EXISTS ix_vid_created ON videos(created)")


def now_ms():
    return int(time.time() * 1000)


class Tx:
    """Serialised write transaction (BEGIN IMMEDIATE) so balances never race."""
    def __enter__(self):
        _lock.acquire()
        db.execute("BEGIN IMMEDIATE")
        return db

    def __exit__(self, et, ev, tb):
        try:
            db.execute("ROLLBACK" if et else "COMMIT")
        finally:
            _lock.release()
        return False


def q1(sql, *a):
    with _lock:
        return db.execute(sql, a).fetchone()


def qa(sql, *a):
    with _lock:
        return db.execute(sql, a).fetchall()


def err(status, msg, **extra):
    raise HTTPException(status, detail={"error": msg, **extra})


# ---------- security helpers ----------
def hash_pw(salt: str, pw: str) -> str:
    return hashlib.scrypt(pw.encode(), salt=salt.encode(), n=2 ** 14, r=8, p=1, dklen=32).hex()


def th(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


_rl = {}


def rate_limit(key: str, limit: int, window: int):
    t = time.time()
    hits = [x for x in _rl.get(key, []) if t - x < window]
    if len(hits) >= limit:
        err(429, "Too many attempts. Wait a minute and try again.")
    hits.append(t)
    _rl[key] = hits


def sign(path: str, ttl: int = 6 * 3600) -> str:
    exp = int(time.time()) + ttl
    sig = hmac.new(SECRET, f"{path}:{exp}".encode(), hashlib.sha256).hexdigest()[:32]
    return f"{path}?e={exp}&s={sig}"


def check_sig(path: str, e: str, s: str) -> bool:
    try:
        if int(e) < time.time():
            return False
    except Exception:
        return False
    good = hmac.new(SECRET, f"{path}:{e}".encode(), hashlib.sha256).hexdigest()[:32]
    return hmac.compare_digest(good, s or "")


def make_handle(name: str, exclude_id: Optional[str] = None) -> str:
    base = re.sub(r"[^A-Za-z0-9._]", "", name)[:24] or "user"
    h, i = base, 1
    while True:
        r = q1("SELECT id FROM users WHERE handle_l=?", h.lower())
        if not r or r["id"] == exclude_id:
            return h
        i += 1
        h = f"{base}{i}"


# ---------- app ----------
app = FastAPI(title="Spicy Dollz API", docs_url=None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(HTTPException)
async def http_exc(_req, exc: HTTPException):
    d = exc.detail if isinstance(exc.detail, dict) else {"error": str(exc.detail)}
    return JSONResponse(d, status_code=exc.status_code)


def visitor(req: Request) -> Optional[str]:
    v = req.headers.get("x-visitor-id")
    return v[:200] if (v and TRUST_VISITOR) else None


def current_user(req: Request, required=True):
    tok = (req.headers.get("authorization") or "").removeprefix("Bearer ").strip() or req.cookies.get("sd_s", "")
    row = None
    if tok:
        row = q1("SELECT u.*, s.token_h FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_h=?", th(tok))
    if not row and not tok:
        v = visitor(req)
        if v:
            row = q1("SELECT u.*, s.token_h FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.visitor=? ORDER BY s.seen DESC LIMIT 1", v)
    if not row:
        if required:
            err(401, "Please sign in again.")
        return None
    if row["banned"]:
        if required:
            err(403, "This account has been suspended.")
        return None
    with _lock:
        db.execute("UPDATE sessions SET seen=? WHERE token_h=?", (now_ms(), row["token_h"]))
    return row


def wallet_row(uid):
    r = q1("SELECT * FROM wallets WHERE user_id=?", uid)
    if not r:
        with _lock:
            db.execute("INSERT OR IGNORE INTO wallets(user_id) VALUES(?)", (uid,))
        r = q1("SELECT * FROM wallets WHERE user_id=?", uid)
    return r


def wallet_json(uid):
    w = wallet_row(uid)
    tx = qa("SELECT k,t,n,a,c,m,d FROM tx WHERE user_id=? ORDER BY d DESC, id DESC LIMIT 200", uid)
    return {
        "coins": w["coins"], "usd": w["usd_c"] / 100, "earned": min(w["earned"], w["coins"]),
        "st": {"tips": w["tips_c"] / 100, "subs": w["subs_c"] / 100, "gifts": w["gifts_c"] / 100},
        "own": json.loads(w["own"]), "prem": w["prem"], "unread": w["unread"], "mv": 1, "frv": 3,
        "tx": [{k: r[k] for k in ("k", "t", "n", "a", "c", "m", "d") if r[k] is not None} for r in tx],
        "testmode": TEST_MODE,
    }


def add_tx(c, uid, k, t, n, a, coins=None, m=""):
    c.execute("INSERT INTO tx(user_id,k,t,n,a,c,m,d) VALUES(?,?,?,?,?,?,?,?)", (uid, k, t, n, a, coins, m, now_ms()))


def media_url(rel: Optional[str]):
    return rel or None


def public_user(u, viewer_id=None):
    prof = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_prof'", u["id"])
    av = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_avatar'", u["id"])
    ban = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_upban'", u["id"])
    pref = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_w3'", u["id"])
    w = wallet_row(u["id"])
    p = json.loads(pref["v"]) if pref else {}
    prem = w["prem"] > now_ms()
    sub = None
    if viewer_id:
        s = q1("SELECT expires FROM subs WHERE subscriber=? AND creator=?", viewer_id, u["id"])
        sub = s["expires"] if s and s["expires"] > now_ms() else None
    vids = qa("SELECT * FROM videos WHERE user_id=? AND removed=0 ORDER BY created DESC", u["id"])
    feat = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_feat'", u["id"])
    return {
        "id": u["id"], "name": u["name"], "handle": u["handle"], "base": u["base"],
        "prof": json.loads(prof["v"]) if prof else {"bio": "", "l": {}},
        "avatar": av["v"] if av else None,
        "banner": (ban["v"] if ban else None) if (p.get("ban") == "up" and prem) else None,
        "banKey": p.get("ban") if p.get("ban") not in (None, "up") else None,
        "premium": prem, "subscribedUntil": sub, "isMe": viewer_id == u["id"],
        "subscribers": q1("SELECT COUNT(*) n FROM subs WHERE creator=? AND expires>?", u["id"], now_ms())["n"],
        "videos": [video_json(v, viewer_id) for v in vids],
        "counts": user_counts(u["id"]),
        "following": bool(viewer_id and q1("SELECT 1 FROM follows WHERE follower=? AND followee=?", viewer_id, u["id"])),
        "blocked": bool(viewer_id and q1("SELECT 1 FROM blocks WHERE blocker=? AND blocked=?", viewer_id, u["id"])),
        "feat": json.loads(feat["v"]) if feat else [],
        "featx": feat_items(u["id"], viewer_id),
    }


def user_counts(uid):
    return {
        "followers": q1("SELECT COUNT(*) n FROM follows WHERE followee=?", uid)["n"],
        "following": q1("SELECT COUNT(*) n FROM follows WHERE follower=?", uid)["n"],
        "likes": q1("SELECT COUNT(*) n FROM likes l JOIN videos v ON v.id=l.video_id WHERE v.user_id=?", uid)["n"],
        "views": q1("SELECT COALESCE(SUM(views),0) n FROM videos WHERE user_id=? AND removed=0", uid)["n"],
        "subs": q1("SELECT COUNT(*) n FROM subs WHERE creator=? AND expires>?", uid, now_ms())["n"],
        "posts": q1("SELECT COUNT(*) n FROM videos WHERE user_id=? AND removed=0", uid)["n"],
    }


def video_json(v, viewer_id=None, owner=None, play=False):
    ok = can_watch(v, viewer_id)
    thumb = None
    if v["thumb"]:
        if v["aud"] == "all":
            thumb = "/media/thumb/" + v["thumb"]
        elif ok:
            thumb = sign("/media/thumb/" + v["thumb"])
        else:
            thumb = "/media/thumb/" + v["thumb"].replace(".jpg", "_b.jpg")
    elif v["kind"] == "photo" and ok:
        thumb = sign(f"/media/vid/{v['file']}")
    vid = v["id"]
    out = {"id": vid, "caption": v["caption"] or "", "aud": v["aud"], "dur": v["dur"], "kind": v["kind"],
           "tags": json.loads(v["tags"] or "[]"), "thumb": thumb, "views": v["views"], "created": v["created"],
           "likes": q1("SELECT COUNT(*) n FROM likes WHERE video_id=?", vid)["n"],
           "comments": q1("SELECT COUNT(*) n FROM comments WHERE video_id=?", vid)["n"],
           "liked": bool(viewer_id and q1("SELECT 1 FROM likes WHERE video_id=? AND user_id=?", vid, viewer_id)),
           "locked": not ok}
    if owner is not None:
        out["user"] = owner
    if play and ok:
        out["url"] = sign(f"/media/vid/{v['file']}")
    return out


def session_payload(u, token=None):
    kv = {r["k"]: r["v"] for r in qa("SELECT k,v FROM kv WHERE user_id=?", u["id"])}
    prefs = json.loads(kv.get("sd_w3", "{}"))
    return {
        "token": token,
        "user": {"id": u["id"], "name": u["name"], "handle": u["handle"], "email": u["email"], "base": u["base"], "role": u["role"]},
        "kv": {k: v for k, v in kv.items() if k != "sd_w3"},
        "prefs": prefs, "wallet": wallet_json(u["id"]),
        "videos": [video_json(v, u["id"]) for v in qa("SELECT * FROM videos WHERE user_id=? AND removed=0 ORDER BY created DESC", u["id"])],
        "counts": user_counts(u["id"]),
        "featx": feat_items(u["id"], u["id"]),
        "telegram": bool(q1("SELECT 1 FROM oauth WHERE provider='telegram' AND user_id=?", u["id"])),
        "config": config_json(),
    }


def config_json():
    return {"payments": "stripe" if STRIPE_KEY else ("test" if TEST_MODE else "off"),
            "email": bool(os.environ.get("SMTP_HOST")), "social": ["telegram"] if TG_TOKEN else [], "fee": FEE,
            "telegram": {"bot_id": TG_TOKEN.split(":")[0], "bot": TG_BOT} if TG_TOKEN else None}


TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TG_BOT = os.environ.get("TELEGRAM_BOT_NAME", "").strip().lstrip("@")


def feat_items(uid, viewer_id=None):
    row = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_feat'", uid)
    arr = (json.loads(row["v"]) if row else []) + [None] * 6
    out = []
    for x in arr[:6]:
        if isinstance(x, str) and x.startswith("/media/img/"):
            out.append({"img": x})
        elif isinstance(x, str) and x.startswith("v:"):
            v = q1("SELECT * FROM videos WHERE id=? AND user_id=? AND removed=0", x[2:], uid)
            out.append({"post": video_json(v, viewer_id)} if v else None)
        else:
            out.append(None)
    return out


def tg_verify(data):
    if not TG_TOKEN:
        err(400, "Telegram sign in is not set up on this server yet.")
    if not isinstance(data, dict) or "hash" not in data or "id" not in data:
        err(400, "Telegram did not send a sign in result.")
    chk = "\n".join(f"{k}={data[k]}" for k in sorted(data) if k != "hash" and data[k] is not None)
    key = hashlib.sha256(TG_TOKEN.encode()).digest()
    if not hmac.compare_digest(hmac.new(key, chk.encode(), hashlib.sha256).hexdigest(), str(data["hash"])):
        err(401, "Telegram sign in could not be verified. Try again.")
    if time.time() - int(data.get("auth_date", 0)) > 86400:
        err(401, "That Telegram sign in expired. Try again.")
    return str(int(data["id"]))


def new_session(c, uid, req):
    token = secrets.token_urlsafe(32)
    v = visitor(req)
    if v:
        c.execute("DELETE FROM sessions WHERE visitor=?", (v,))
    c.execute("INSERT INTO sessions(token_h,user_id,visitor,created,seen) VALUES(?,?,?,?,?)", (th(token), uid, v, now_ms(), now_ms()))
    return token


# ---------- auth ----------
def with_cookie(payload, token, req):
    r = JSONResponse(payload)
    secure = req.url.scheme == "https" or req.headers.get("x-forwarded-proto") == "https"
    r.set_cookie("sd_s", token, max_age=60 * 86400, httponly=True, samesite="lax", secure=secure, path="/")
    return r

EMAIL_RX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@app.get("/api/config")
def api_config():
    return config_json()


@app.get("/api/session")
def api_session(req: Request):
    u = current_user(req, required=False)
    if not u:
        return {"user": None, "config": config_json()}
    return session_payload(u)


@app.post("/api/auth/signup")
async def signup(req: Request):
    b = await req.json()
    rate_limit("su:" + (req.client.host if req.client else "?"), 10, 600)
    name = str(b.get("name", "")).strip()[:30]
    name = re.sub(r"[<>&\"'`\\]", "", name)
    email = str(b.get("email", "")).strip().lower()[:200]
    pw = str(b.get("password", ""))
    base = b.get("base") if b.get("base") in BASES else "dragon"
    if len(name) < 2:
        err(400, "Display name needs at least 2 characters.", field="name")
    if not EMAIL_RX.match(email):
        err(400, "That email looks incomplete.", field="email")
    if len(pw) < 8 or len(pw) > 200:
        err(400, "Use at least 8 characters for your password.", field="password")
    if not b.get("adult"):
        err(400, "Confirm that you are 18 or older to continue.", field="adult")
    with Tx() as c:
        if c.execute("SELECT 1 FROM users WHERE email=? OR name_l=? OR handle_l=?", (email, name.lower(), name.lower())).fetchone():
            err(409, "That email or name is already registered. Use Sign in from your account colour.", field="email")
        uid = uuid.uuid4().hex
        salt = secrets.token_hex(16)
        handle = make_handle(name)
        c.execute("INSERT INTO users(id,email,name,name_l,handle,handle_l,base,salt,pw,created) VALUES(?,?,?,?,?,?,?,?,?,?)",
                  (uid, email, name, name.lower(), handle, handle.lower(), base, salt, hash_pw(salt, pw), now_ms()))
        c.execute("INSERT INTO wallets(user_id) VALUES(?)", (uid,))
        admins = [x.strip().lower() for x in os.environ.get("ADMIN_EMAILS", "").split(",") if x.strip()]
        first = c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"] == 1
        if email in admins or (not admins and first):
            c.execute("UPDATE users SET role='admin' WHERE id=?", (uid,))
        token = new_session(c, uid, req)
    return with_cookie(session_payload(q1("SELECT * FROM users WHERE id=?", uid), token), token, req)


@app.post("/api/auth/telegram")
async def auth_telegram(req: Request):
    b = await req.json()
    rate_limit("tg:" + (req.client.host if req.client else "?"), 20, 600)
    data = b.get("data") or {}
    sub = tg_verify(data)
    row = q1("SELECT user_id FROM oauth WHERE provider='telegram' AND sub=?", sub)
    created = False
    if row:
        u = q1("SELECT * FROM users WHERE id=?", row["user_id"])
        if u["banned"]:
            err(403, "This account has been suspended.")
        uid = u["id"]
        with Tx() as c:
            token = new_session(c, uid, req)
    else:
        if not b.get("adult"):
            err(400, "New here? Open Sign up, tick the 18+ box, then tap Telegram again.", code="adult")
        base = b.get("base") if b.get("base") in BASES else "dragon"
        nm = " ".join(str(data.get(k) or "") for k in ("first_name", "last_name")).strip() or str(data.get("username") or "Telegram user")
        nm = re.sub(r"[<>&\"'`\\]", "", nm)[:26] or "Telegram user"
        if len(nm) < 2:
            nm = nm + "_tg"
        name, i = nm, 1
        while q1("SELECT 1 FROM users WHERE name_l=? OR handle_l=?", name.lower(), name.lower()):
            i += 1
            name = f"{nm}{i}"
        email = f"tg{sub}@telegram.local"
        with Tx() as c:
            uid = uuid.uuid4().hex
            salt = secrets.token_hex(16)
            handle = make_handle(str(data.get("username") or name))
            c.execute("INSERT INTO users(id,email,name,name_l,handle,handle_l,base,salt,pw,created) VALUES(?,?,?,?,?,?,?,?,?,?)",
                      (uid, email, name, name.lower(), handle, handle.lower(), base, salt, hash_pw(salt, secrets.token_urlsafe(24)), now_ms()))
            c.execute("INSERT INTO wallets(user_id) VALUES(?)", (uid,))
            c.execute("INSERT INTO oauth VALUES('telegram',?,?)", (sub, uid))
            admins = [x.strip().lower() for x in os.environ.get("ADMIN_EMAILS", "").split(",") if x.strip()]
            if not admins and c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"] == 1:
                c.execute("UPDATE users SET role='admin' WHERE id=?", (uid,))
            ph = str(data.get("photo_url") or "")
            if re.match(r"^https://\S{3,500}$", ph):
                c.execute("INSERT INTO kv VALUES(?,?,?)", (uid, "sd_avatar", ph))
            token = new_session(c, uid, req)
        created = True
    out = session_payload(q1("SELECT * FROM users WHERE id=?", uid), token)
    out["created"] = created
    return with_cookie(out, token, req)


@app.post("/api/auth/telegram/link")
async def auth_telegram_link(req: Request):
    u = current_user(req)
    b = await req.json()
    sub = tg_verify(b.get("data") or {})
    other = q1("SELECT user_id FROM oauth WHERE provider='telegram' AND sub=?", sub)
    if other and other["user_id"] != u["id"]:
        err(409, "That Telegram account is already linked to another Spicy Dollz account.")
    with _lock:
        db.execute("DELETE FROM oauth WHERE provider='telegram' AND user_id=?", (u["id"],))
        db.execute("INSERT OR REPLACE INTO oauth VALUES('telegram',?,?)", (sub, u["id"]))
    return {"ok": True}


@app.delete("/api/auth/telegram/link")
def auth_telegram_unlink(req: Request):
    u = current_user(req)
    with _lock:
        db.execute("DELETE FROM oauth WHERE provider='telegram' AND user_id=?", (u["id"],))
    return {"ok": True}


@app.post("/api/auth/login")
async def login(req: Request):
    b = await req.json()
    ident = str(b.get("id", "")).strip().lower()[:200]
    pw = str(b.get("password", ""))
    rate_limit("li:" + ident, 8, 300)
    rate_limit("lip:" + (req.client.host if req.client else "?"), 40, 300)
    u = q1("SELECT * FROM users WHERE email=? OR name_l=? OR handle_l=?", ident, ident, ident)
    if not u or not hmac.compare_digest(hash_pw(u["salt"], pw), u["pw"]):
        err(401, "Wrong email, name or password.", field="password")
    if u["banned"]:
        err(403, "This account has been suspended.")
    if b.get("base") and b.get("base") != u["base"]:
        err(409, "wrong_base", code="wrong_base", base=u["base"])
    with Tx() as c:
        token = new_session(c, u["id"], req)
    return with_cookie(session_payload(u, token), token, req)


@app.post("/api/auth/logout")
def logout(req: Request):
    u = current_user(req, required=False)
    if u:
        with _lock:
            db.execute("DELETE FROM sessions WHERE token_h=?", (u["token_h"],))
    r = JSONResponse({"ok": True})
    r.delete_cookie("sd_s", path="/")
    return r


def send_mail(to, subject, body):
    host = os.environ.get("SMTP_HOST")
    if not host:
        return False
    msg = EmailMessage()
    msg["From"] = os.environ.get("SMTP_FROM", os.environ.get("SMTP_USER", "no-reply@spicydollz.app"))
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    port = int(os.environ.get("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=20) as s:
        s.starttls()
        if os.environ.get("SMTP_USER"):
            s.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASS", ""))
        s.send_message(msg)
    return True


@app.post("/api/auth/forgot")
async def forgot(req: Request):
    b = await req.json()
    email = str(b.get("email", "")).strip().lower()
    link_base = str(b.get("returnUrl", ""))[:500]
    rate_limit("fp:" + email, 3, 900)
    if not os.environ.get("SMTP_HOST"):
        return {"ok": False, "message": "Password reset emails are not switched on yet. The site owner needs to add an email service."}
    u = q1("SELECT * FROM users WHERE email=? OR name_l=? OR handle_l=?", email, email, email)
    if u and link_base.startswith(("https://", "http://")):
        tok = secrets.token_urlsafe(32)
        with _lock:
            db.execute("INSERT INTO resets VALUES(?,?,?)", (th(tok), u["id"], now_ms() + 3600000))
        try:
            send_mail(u["email"], "Reset your Spicy Dollz password",
                      f"Hi {u['name']},\n\nOpen this link within one hour to choose a new password:\n{link_base.split('#')[0]}#reset={tok}\n\nIf you did not ask for this, ignore this email.")
        except Exception as e:
            print("mail error", e)
    return {"ok": True, "message": "If that account exists, a reset link is on its way."}


@app.post("/api/auth/reset")
async def reset(req: Request):
    b = await req.json()
    tok, pw = str(b.get("token", "")), str(b.get("password", ""))
    if len(pw) < 8:
        err(400, "Use at least 8 characters for your password.")
    with Tx() as c:
        r = c.execute("SELECT * FROM resets WHERE token_h=?", (th(tok),)).fetchone()
        if not r or r["expires"] < now_ms():
            err(400, "This reset link has expired. Ask for a new one.")
        salt = secrets.token_hex(16)
        c.execute("UPDATE users SET salt=?, pw=? WHERE id=?", (salt, hash_pw(salt, pw), r["user_id"]))
        c.execute("DELETE FROM resets WHERE user_id=?", (r["user_id"],))
        c.execute("DELETE FROM sessions WHERE user_id=?", (r["user_id"],))
    return {"ok": True}


@app.post("/api/auth/password")
async def change_password(req: Request):
    u = current_user(req)
    b = await req.json()
    if not hmac.compare_digest(hash_pw(u["salt"], str(b.get("old", ""))), u["pw"]):
        err(400, "Your current password is not right.")
    pw = str(b.get("new", ""))
    if len(pw) < 8:
        err(400, "Use at least 8 characters for your password.")
    salt = secrets.token_hex(16)
    with Tx() as c:
        c.execute("UPDATE users SET salt=?, pw=? WHERE id=?", (salt, hash_pw(salt, pw), u["id"]))
        c.execute("DELETE FROM sessions WHERE user_id=? AND token_h<>?", (u["id"], u["token_h"]))
    return {"ok": True}


@app.patch("/api/me")
async def patch_me(req: Request):
    u = current_user(req)
    b = await req.json()
    name = re.sub(r"[<>&\"'`\\]", "", str(b.get("name", "")).strip())[:30]
    if len(name) < 2:
        err(400, "Display name needs at least 2 characters.")
    with Tx() as c:
        if c.execute("SELECT 1 FROM users WHERE (name_l=? OR handle_l=?) AND id<>?", (name.lower(), name.lower(), u["id"])).fetchone():
            err(409, "That name is already taken.")
        handle = make_handle(name, u["id"])
        c.execute("UPDATE users SET name=?, name_l=?, handle=?, handle_l=? WHERE id=?", (name, name.lower(), handle, handle.lower(), u["id"]))
    return {"name": name, "handle": handle}


@app.delete("/api/me")
async def delete_me(req: Request):
    u = current_user(req)
    b = await req.json()
    if not hmac.compare_digest(hash_pw(u["salt"], str(b.get("password", ""))), u["pw"]):
        err(400, "Your password is not right.")
    files = qa("SELECT file, thumb FROM videos WHERE user_id=?", u["id"])
    with Tx() as c:
        c.execute("DELETE FROM users WHERE id=?", (u["id"],))
    for f in files:
        for p in ((MEDIA / "vid" / f["file"]), (MEDIA / "thumb" / (f["thumb"] or "_"))):
            p.unlink(missing_ok=True)
    return {"ok": True}


# ---------- key/value prefs (profile, cosmetics) ----------
@app.put("/api/kv/{key}")
async def put_kv(key: str, req: Request):
    u = current_user(req)
    b = await req.json()
    v = b.get("v")
    if key == "sd_prof":
        p = v if isinstance(v, dict) else {}
        bio = str(p.get("bio", ""))[:300]
        links = {k: str(x)[:300] for k, x in (p.get("l") or {}).items() if k in ("linkme", "instagram", "x", "telegram", "tiktok") and re.match(r"^https?://", str(x))}
        val = json.dumps({"bio": bio, "l": links})
    elif key == "sd_w3":
        p = v if isinstance(v, dict) else {}
        if "unread" in p and not p.get("unread"):
            with _lock:
                db.execute("UPDATE wallets SET unread=0 WHERE user_id=?", (u["id"],))
        clean = {k: x for k, x in p.items() if k not in MONEY_KEYS}
        val = json.dumps(clean)
        if len(val) > 20000:
            err(413, "Settings are too large.")
    elif key == "sd_feat":
        arr = v if isinstance(v, list) else []
        def ok_f(x):
            if isinstance(x, str) and x.startswith("/media/img/"):
                return x
            if isinstance(x, str) and x.startswith("v:") and q1("SELECT 1 FROM videos WHERE id=? AND user_id=? AND removed=0", x[2:], u["id"]):
                return x
            return None
        val = json.dumps([ok_f(x) for x in arr[:6]])
    elif key == "sd_avatar":
        s = str(v or "")
        if not (s.startswith("data:image/svg+xml,") and len(s) < 4000) and not re.match(r"^https://\S{3,500}$", s) and not s.startswith("/media/img/"):
            err(400, "Upload the photo as a file instead.")
        val = s
    else:
        err(404, "Unknown setting.")
    with _lock:
        db.execute("INSERT INTO kv VALUES(?,?,?) ON CONFLICT(user_id,k) DO UPDATE SET v=excluded.v", (u["id"], key, val))
    return {"ok": True}


@app.delete("/api/kv/{key}")
def del_kv(key: str, req: Request):
    u = current_user(req)
    if key not in ("sd_avatar", "sd_upban"):
        err(404, "Unknown setting.")
    with _lock:
        db.execute("DELETE FROM kv WHERE user_id=? AND k=?", (u["id"], key))
    return {"ok": True}


@app.post("/api/clientlog")
async def clientlog(req: Request):
    u = current_user(req, required=False)
    try:
        b = await req.json()
    except Exception:
        b = {}
    rate_limit("cl:" + (req.client.host if req.client else "?"), 120, 600)
    line = json.dumps({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "u": u["handle"] if u else None,
                       "ua": req.headers.get("user-agent", "")[:200], "ev": str(b.get("ev", ""))[:60], "msg": str(b.get("msg", ""))[:500]})
    with open(DATA / "client.log", "a") as f:
        f.write(line + "\n")
    return {"ok": True}


# ---------- chunked uploads (proxies cap request bodies, so big files arrive in pieces) ----------
TMP = DATA / "tmp"
TMP.mkdir(parents=True, exist_ok=True)
HEIF_BRANDS = (b"heic", b"heix", b"hevc", b"hevx", b"heim", b"heis", b"mif1", b"msf1", b"avif")


def is_heif(head):
    return head[4:8] == b"ftyp" and head[8:12] in HEIF_BRANDS


def to_jpeg(src, dst, maxw):
    try:
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-frames:v", "1", "-vf",
                            f"scale='min({maxw},iw)':-2", "-q:v", "3", str(dst)], timeout=60, capture_output=True)
        return r.returncode == 0 and dst.exists() and dst.stat().st_size > 0
    except Exception:
        return False


def chunk_path(uid, cid):
    if not re.fullmatch(r"[a-f0-9]{32}", cid or ""):
        err(400, "Upload expired. Please try again.")
    p = TMP / f"{uid}_{cid}.part"
    if not p.exists():
        err(400, "Upload expired. Please try again.")
    return p


@app.post("/api/chunks")
def chunk_start(req: Request):
    u = current_user(req)
    rate_limit("ck:" + u["id"], 60, 3600)
    t = time.time()
    for old in TMP.glob("*.part"):
        if t - old.stat().st_mtime > 6 * 3600:
            old.unlink(missing_ok=True)
    cid = uuid.uuid4().hex
    (TMP / f"{u['id']}_{cid}.part").write_bytes(b"")
    return {"id": cid}


@app.post("/api/chunks/{cid}")
async def chunk_put(cid: str, req: Request):
    u = current_user(req)
    p = chunk_path(u["id"], cid)
    body = await req.body()
    if len(body) > 9 * 1024 * 1024:
        err(413, "Chunk too large.")
    if p.stat().st_size + len(body) > MAX_VIDEO:
        p.unlink(missing_ok=True)
        err(413, f"Files can be up to {MAX_VIDEO // 1048576} MB.")
    with open(p, "ab") as f:
        f.write(body)
    return {"size": p.stat().st_size}


# ---------- image uploads ----------
IMG_SIG = [(b"\xff\xd8\xff", "jpg", "image/jpeg"), (b"\x89PNG\r\n\x1a\n", "png", "image/png"),
           (b"GIF87a", "gif", "image/gif"), (b"GIF89a", "gif", "image/gif")]


def sniff_img(data: bytes):
    for sig, ext, mime in IMG_SIG:
        if data.startswith(sig):
            return ext
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


@app.post("/api/upload/{kind}")
async def upload_image(kind: str, req: Request, file: Optional[UploadFile] = File(None), data: Optional[str] = Form(None),
                       chunk: Optional[str] = Form(None)):
    u = current_user(req)
    if kind not in ("avatar", "banner", "feat"):
        err(404, "Unknown upload.")
    if chunk:
        cp = chunk_path(u["id"], chunk)
        if cp.stat().st_size > 40 * 1024 * 1024:
            cp.unlink(missing_ok=True)
            err(413, "That image is too large (max 40 MB).")
        raw = cp.read_bytes()
        cp.unlink(missing_ok=True)
    elif file is not None:
        raw = await file.read(40 * 1024 * 1024 + 1)
    elif data and data.startswith("data:image/"):
        try:
            raw = base64.b64decode(data.split(",", 1)[1])
        except Exception:
            err(400, "This image could not be read.")
    else:
        err(400, "Choose an image.")
    limit = 2 * 1024 * 1024 if kind == "avatar" else 6 * 1024 * 1024
    ext = sniff_img(raw)
    if len(raw) > 40 * 1024 * 1024:
        err(413, "That image is too large (max 40 MB).")
    if (not ext or len(raw) > limit) and ext != "gif":
        # phone photos: HEIC or very large JPG/PNG -> resized JPG
        src = TMP / f"{uuid.uuid4().hex}.in"
        out = TMP / f"{uuid.uuid4().hex}.jpg"
        src.write_bytes(raw)
        ok = to_jpeg(src, out, 800 if kind == "avatar" else 2000)
        src.unlink(missing_ok=True)
        if not ok:
            out.unlink(missing_ok=True)
            err(400, "This image could not be read. Please choose a JPG, PNG, WebP, GIF or HEIC photo.")
        raw = out.read_bytes()
        out.unlink(missing_ok=True)
        ext = "jpg"
    if len(raw) > limit:
        err(413, "That image is too large (max %d MB)." % (limit // 1048576))
    if kind == "banner" and wallet_row(u["id"])["prem"] <= now_ms():
        err(402, "Uploading your own banner is included with Spicy Premium.")
    name = f"{uuid.uuid4().hex}.{ext}"
    (MEDIA / "img" / name).write_bytes(raw)
    if kind == "feat":
        slot = max(0, min(5, int(req.query_params.get("slot", "0"))))
        cur = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_feat'", u["id"])
        arr = (json.loads(cur["v"]) if cur else []) + [None] * 6
        arr = arr[:6]
        old = arr[slot]
        arr[slot] = "/media/img/" + name
        with _lock:
            db.execute("INSERT INTO kv VALUES(?,?,?) ON CONFLICT(user_id,k) DO UPDATE SET v=excluded.v", (u["id"], "sd_feat", json.dumps(arr)))
        if old:
            (MEDIA / "img" / old.rsplit("/", 1)[1]).unlink(missing_ok=True)
        return {"url": "/media/img/" + name, "feat": arr}
    key = "sd_avatar" if kind == "avatar" else "sd_upban"
    old = q1("SELECT v FROM kv WHERE user_id=? AND k=?", u["id"], key)
    with _lock:
        db.execute("INSERT INTO kv VALUES(?,?,?) ON CONFLICT(user_id,k) DO UPDATE SET v=excluded.v", (u["id"], key, "/media/img/" + name))
    if old and old["v"].startswith("/media/img/"):
        (MEDIA / "img" / old["v"].rsplit("/", 1)[1]).unlink(missing_ok=True)
    return {"url": "/media/img/" + name}


@app.get("/media/img/{name}")
def get_img(name: str):
    p = MEDIA / "img" / Path(name).name
    if not p.exists():
        err(404, "Not found")
    return FileResponse(p, headers={"Cache-Control": "public, max-age=31536000, immutable"})


@app.get("/media/thumb/{name}")
def get_thumb(name: str, e: str = "", s: str = ""):
    name = Path(name).name
    p = MEDIA / "thumb" / name
    if not p.exists():
        err(404, "Not found")
    if not name.endswith("_b.jpg"):
        v = q1("SELECT aud FROM videos WHERE thumb=?", name)
        if v and v["aud"] != "all" and not check_sig(f"/media/thumb/{name}", e, s):
            err(403, "Locked")
    return FileResponse(p, headers={"Cache-Control": "public, max-age=31536000, immutable"})


# ---------- videos ----------
def probe(path: Path):
    if not HAS_FFPROBE:
        return None
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_type:format=duration",
                            "-of", "json", str(path)], capture_output=True, text=True, timeout=60)
        j = json.loads(r.stdout or "{}")
        if not j.get("streams"):
            return False
        return float(j.get("format", {}).get("duration") or 0)
    except Exception:
        return None


def make_thumb(src: Path, dst: Path, at: float):
    if not HAS_FFPROBE:
        return False
    try:
        seek = ["-ss", str(at)] if at and at > 0 else []
        subprocess.run(["ffmpeg", "-y", "-v", "error", *seek, "-i", str(src), "-frames:v", "1",
                        "-vf", "scale='min(480,iw)':-2", str(dst)], timeout=60, capture_output=True)
        if seek and not (dst.exists() and dst.stat().st_size > 0):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-frames:v", "1",
                            "-vf", "scale='min(480,iw)':-2", str(dst)], timeout=60, capture_output=True)
        return dst.exists() and dst.stat().st_size > 0
    except Exception:
        return False


MAX_VIDEO = int(os.environ.get("MAX_VIDEO_MB", "500")) * 1024 * 1024


@app.post("/api/videos")
async def upload_video(req: Request, file: Optional[UploadFile] = File(None), caption: str = Form(""), aud: str = Form("all"),
                       dur: float = Form(0), thumb: Optional[str] = Form(None), chunk: Optional[str] = Form(None), tags: str = Form("")):
    u = current_user(req)
    if aud not in ("all", "subs", "prem"):
        aud = "all"
    vid = uuid.uuid4().hex
    rate_limit("up:" + u["id"], 30, 3600)
    cp = chunk_path(u["id"], chunk) if chunk else None
    if cp is None and file is None:
        err(400, "Choose a video or photo.")
    if cp is not None:
        with open(cp, "rb") as fh:
            head = fh.read(64)
    else:
        head = await file.read(64)
    heif = is_heif(head)
    img_ext = "heic" if heif else sniff_img(head)
    kind = "photo" if img_ext else "video"
    if not img_ext and not (head[4:8] == b"ftyp" or head[:4] == b"\x1a\x45\xdf\xa3"):
        err(400, "Please choose a video (MP4, MOV, WebM) or a photo (JPG, PNG, WebP, GIF).")
    if kind == "photo" and aud == "prem":
        err(400, "Premium posts are long videos. Choose Everyone or Subscribers only for photos.")
    ext = img_ext or ("webm" if head[:4] == b"\x1a\x45\xdf\xa3" else ("mov" if b"qt  " in head[8:12] else "mp4"))
    dst = MEDIA / "vid" / f"{vid}.{ext}"
    size = len(head)
    if cp is not None:
        if cp.stat().st_size > MAX_VIDEO:
            cp.unlink(missing_ok=True)
            err(413, f"Videos can be up to {MAX_VIDEO // 1048576} MB.")
        shutil.move(str(cp), str(dst))
    else:
      with open(dst, "wb") as f:
        f.write(head)
        while True:
            piece = await file.read(1024 * 1024)
            if not piece:
                break
            size += len(piece)
            if size > MAX_VIDEO:
                f.close()
                dst.unlink(missing_ok=True)
                err(413, f"Videos can be up to {MAX_VIDEO // 1048576} MB.")
            f.write(piece)
    if heif:
        jp = MEDIA / "vid" / f"{vid}.jpg"
        ok = to_jpeg(dst, jp, 2400)
        dst.unlink(missing_ok=True)
        if not ok:
            err(400, "This HEIC photo could not be converted. Please choose a JPG or PNG.")
        dst, ext = jp, "jpg"
    real = probe(dst) if kind == "video" else 0.0
    if real is False:
        dst.unlink(missing_ok=True)
        err(400, "This file has no playable video.")
    duration = (real if real else max(0.0, float(dur or 0))) if kind == "video" else 0.0
    if aud == "prem" and duration < 120:
        dst.unlink(missing_ok=True)
        err(400, "Premium videos need to be at least 2:00 long.")
    tname = None
    tp = MEDIA / "thumb" / f"{vid}.jpg"
    if make_thumb(dst, tp, 0 if kind == "photo" else min(1.0, duration / 2)):
        tname = tp.name
    elif thumb and thumb.startswith("data:image/"):
        try:
            raw = base64.b64decode(thumb.split(",", 1)[1])
            if sniff_img(raw) and len(raw) < 1024 * 1024:
                tp.write_bytes(raw)
                tname = tp.name
        except Exception:
            pass
    if tname and HAS_FFPROBE:
        try:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tp), "-vf", "scale=96:-2,boxblur=8:3", str(MEDIA / "thumb" / f"{vid}_b.jpg")], timeout=30, capture_output=True)
        except Exception:
            pass
    mime = {"mp4": "video/mp4", "mov": "video/quicktime", "webm": "video/webm", "jpg": "image/jpeg", "png": "image/png", "webp": "image/webp", "gif": "image/gif"}[ext]
    cap = caption.strip()[:300]
    extra = [t.strip().lstrip("#").lower() for t in str(tags or "").split(",")]
    extra = [t for t in extra if re.fullmatch(r"[a-z0-9_]{2,30}", t)]
    tags = list(dict.fromkeys(extra + sorted({t.lower() for t in re.findall(r"#([A-Za-z0-9_]{2,30})", cap)})))[:10]
    with _lock:
        db.execute("INSERT INTO videos(id,user_id,caption,aud,dur,file,thumb,mime,views,created,kind,tags) VALUES(?,?,?,?,?,?,?,?,0,?,?,?)",
                   (vid, u["id"], cap, aud, duration, dst.name, tname, mime, now_ms(), kind, json.dumps(tags)))
    return video_json(q1("SELECT * FROM videos WHERE id=?", vid), u["id"])


def can_watch(v, uid):
    if v["aud"] == "all" or (uid and v["user_id"] == uid):
        return True
    if not uid:
        return False
    s = q1("SELECT expires FROM subs WHERE subscriber=? AND creator=?", uid, v["user_id"])
    return bool(s and s["expires"] > now_ms())


@app.get("/api/videos/{vid}/play")
def play(vid: str, req: Request):
    u = current_user(req, required=False)
    v = q1("SELECT * FROM videos WHERE id=? AND removed=0", vid)
    if not v:
        err(404, "This post was removed.")
    if not can_watch(v, u["id"] if u else None):
        err(403, "Subscribe to unlock this video.", code="locked")
    count_view(v, u["id"] if u else None)
    return {"url": sign(f"/media/vid/{v['file']}"), "kind": v["kind"]}


@app.get("/media/vid/{name}")
def get_vid(name: str, e: str = "", s: str = ""):
    name = Path(name).name
    if not check_sig(f"/media/vid/{name}", e, s):
        err(403, "This link has expired. Reload the page.")
    p = MEDIA / "vid" / name
    if not p.exists():
        err(404, "Not found")
    return FileResponse(p, headers={"Cache-Control": "private, max-age=3600"})


@app.delete("/api/videos/{vid}")
def delete_video(vid: str, req: Request):
    u = current_user(req)
    v = q1("SELECT * FROM videos WHERE id=? AND user_id=?", vid, u["id"])
    if not v:
        err(404, "Video not found.")
    with _lock:
        db.execute("DELETE FROM videos WHERE id=?", (vid,))
    (MEDIA / "vid" / v["file"]).unlink(missing_ok=True)
    if v["thumb"]:
        (MEDIA / "thumb" / v["thumb"]).unlink(missing_ok=True)
    return {"ok": True}


# ---------- creators ----------
@app.get("/api/users/{handle}")
def get_user(handle: str, req: Request):
    me = current_user(req, required=False)
    u = q1("SELECT * FROM users WHERE handle_l=? AND banned=0", handle.lstrip("@").lower())
    if not u:
        err(404, "No creator with that name.")
    return public_user(u, me["id"] if me else None)


@app.get("/api/users")
def search_users(q: str = ""):
    q = q.strip().lstrip("@#").lower()[:40]
    rows = qa("SELECT * FROM users WHERE banned=0 AND (name_l LIKE ? OR handle_l LIKE ?) ORDER BY created DESC LIMIT 30", f"%{q}%", f"%{q}%")
    out = []
    for u in rows:
        av = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_avatar'", u["id"])
        n = q1("SELECT COUNT(*) n FROM videos WHERE user_id=?", u["id"])["n"]
        out.append({"name": u["name"], "handle": u["handle"], "avatar": av["v"] if av else None, "videos": n})
    return out


# ---------- wallet ----------
@app.get("/api/wallet")
def get_wallet(req: Request):
    return wallet_json(current_user(req)["id"])


def need_coins(c, uid, amount):
    w = c.execute("SELECT * FROM wallets WHERE user_id=?", (uid,)).fetchone()
    if w["coins"] < amount:
        err(402, "Not enough Spicy Dollz. Top up first.", code="funds")
    return w


@app.post("/api/tip")
async def tip(req: Request):
    u = current_user(req)
    b = await req.json()
    coins = int(b.get("coins", 0))
    note = re.sub(r"[<>]", "", str(b.get("note", "")))[:80] or "Tip"
    if coins < 100 or coins > 100000:
        err(400, "Tips are between 100 and 100,000 Spicy Dollz.")
    to = q1("SELECT * FROM users WHERE handle_l=?", str(b.get("to", "")).lstrip("@").lower())
    if not to:
        err(404, "Creator not found.")
    if to["id"] == u["id"]:
        err(400, "You can't tip yourself. Share your profile link so fans can tip you.")
    net = coins - int(round(coins * FEE))
    with Tx() as c:
        need_coins(c, u["id"], coins)
        c.execute("INSERT OR IGNORE INTO wallets(user_id) VALUES(?)", (to["id"],))
        c.execute("UPDATE wallets SET coins=coins-? WHERE user_id=?", (coins, u["id"]))
        c.execute("UPDATE wallets SET coins=coins+?, earned=earned+?, tips_c=tips_c+?, unread=unread+1 WHERE user_id=?", (net, net, net, to["id"]))
        add_tx(c, u["id"], "tipout", "out", "@" + to["handle"], coins / 100, coins, note)
        add_tx(c, to["id"], "tips", "in", "@" + u["handle"], net / 100, net, note)
        c.execute("INSERT INTO notifs(user_id,kind,actor_id,text,created) VALUES(?,?,?,?,?)", (to["id"], "tip", u["id"], f"sent you a {coins:,} coin tip", now_ms()))
    return {"wallet": wallet_json(u["id"])}


@app.post("/api/subscribe")
async def subscribe(req: Request):
    u = current_user(req)
    b = await req.json()
    to = q1("SELECT * FROM users WHERE handle_l=?", str(b.get("to", "")).lstrip("@").lower())
    if not to:
        err(404, "Creator not found.")
    if to["id"] == u["id"]:
        err(400, "This is your own profile. Fans subscribe from your shared link.")
    net = SUB_PRICE - int(round(SUB_PRICE * FEE))
    with Tx() as c:
        s = c.execute("SELECT expires FROM subs WHERE subscriber=? AND creator=?", (u["id"], to["id"])).fetchone()
        if s and s["expires"] > now_ms():
            err(409, "You are already subscribed.")
        need_coins(c, u["id"], SUB_PRICE)
        c.execute("INSERT OR IGNORE INTO wallets(user_id) VALUES(?)", (to["id"],))
        c.execute("UPDATE wallets SET coins=coins-? WHERE user_id=?", (SUB_PRICE, u["id"]))
        c.execute("UPDATE wallets SET coins=coins+?, earned=earned+?, subs_c=subs_c+?, unread=unread+1 WHERE user_id=?", (net, net, net, to["id"]))
        exp = now_ms() + 30 * DAY
        c.execute("INSERT INTO subs VALUES(?,?,?) ON CONFLICT(subscriber,creator) DO UPDATE SET expires=excluded.expires", (u["id"], to["id"], exp))
        add_tx(c, u["id"], "subout", "out", "@" + to["handle"], SUB_PRICE / 100, SUB_PRICE, "One month")
        add_tx(c, to["id"], "subs", "in", "@" + u["handle"], net / 100, net, "New subscriber")
        c.execute("INSERT INTO notifs(user_id,kind,actor_id,text,created) VALUES(?,?,?,?,?)", (to["id"], "sub", u["id"], "subscribed to you", now_ms()))
        bump(c, to["id"], "subs")
    return {"wallet": wallet_json(u["id"]), "expires": exp}


@app.post("/api/unsubscribe")
async def unsubscribe(req: Request):
    u = current_user(req)
    b = await req.json()
    to = q1("SELECT * FROM users WHERE handle_l=?", str(b.get("to", "")).lstrip("@").lower())
    if to:
        with _lock:
            db.execute("DELETE FROM subs WHERE subscriber=? AND creator=?", (u["id"], to["id"]))
    return {"ok": True}


@app.post("/api/wallet/buy")
async def buy_item(req: Request):
    u = current_user(req)
    b = await req.json()
    item = str(b.get("item", ""))
    m = re.match(r"^([fb])(\d+)$", item)
    if not m:
        err(400, "Unknown item.")
    kind, i = m.group(1), int(m.group(2))
    if kind == "f":
        if i >= len(FRAMES):
            err(400, "Unknown frame.")
        name, price, label = FRAMES[i][0], FRAMES[i][1], "Avatar frame"
    else:
        if i < 1 or i >= len(BANNERS):
            err(400, "Unknown banner.")
        name, price, label = BANNERS[i], BANNER_PRICE, "Banner"
    with Tx() as c:
        w = c.execute("SELECT * FROM wallets WHERE user_id=?", (u["id"],)).fetchone()
        own = json.loads(w["own"])
        if item in own or w["prem"] > now_ms():
            return {"wallet": wallet_json(u["id"]), "already": True}
        need_coins(c, u["id"], price)
        own.append(item)
        c.execute("UPDATE wallets SET coins=coins-?, own=? WHERE user_id=?", (price, json.dumps(own), u["id"]))
        add_tx(c, u["id"], "mall", "out", name, price / 100, price, label)
    return {"wallet": wallet_json(u["id"])}


@app.post("/api/wallet/convert")
async def convert(req: Request):
    u = current_user(req)
    b = await req.json()
    d = int(b.get("dir", 0))
    with Tx() as c:
        w = c.execute("SELECT * FROM wallets WHERE user_id=?", (u["id"],)).fetchone()
        if d == 0:
            usd_c = int(round(float(b.get("amt", 0)) * 100))
            if usd_c <= 0 or usd_c > w["usd_c"]:
                err(402, "Not enough balance.")
            c.execute("UPDATE wallets SET usd_c=usd_c-?, coins=coins+? WHERE user_id=?", (usd_c, usd_c, u["id"]))
            add_tx(c, u["id"], "conv", "out", f"{usd_c} Spicy Dollz", usd_c / 100, None, "Spicy Dollz")
        else:
            coins = int(b.get("amt", 0))
            if coins <= 0 or coins > w["coins"]:
                err(402, "Not enough Spicy Dollz.")
            c.execute("UPDATE wallets SET coins=coins-?, usd_c=usd_c+?, earned=MAX(0, earned-?) WHERE user_id=?", (coins, coins, coins, u["id"]))
            add_tx(c, u["id"], "cash", "in", f"{coins:,} Spicy Dollz", coins / 100, coins, "100 = $1")
    return {"wallet": wallet_json(u["id"])}


@app.post("/api/wallet/withdraw")
async def withdraw(req: Request):
    u = current_user(req)
    b = await req.json()
    usd_c = int(round(float(b.get("usd", 0)) * 100))
    token, net, addr = (str(b.get(k, ""))[:60] for k in ("token", "net", "addr"))
    if usd_c < 1000:
        err(400, "Minimum withdrawal is $10.")
    if not addr or len(addr) < 8:
        err(400, "Add your crypto payout details first.")
    coins = usd_c
    with Tx() as c:
        w = c.execute("SELECT * FROM wallets WHERE user_id=?", (u["id"],)).fetchone()
        avail = min(w["coins"], w["earned"])
        if coins > avail:
            err(402, f"You can withdraw up to ${avail / 100:,.2f}. Only money earned from fans can be withdrawn; topped-up coins stay in the app.")
        c.execute("UPDATE wallets SET coins=coins-?, earned=earned-? WHERE user_id=?", (coins, coins, u["id"]))
        c.execute("INSERT INTO withdrawals(user_id,usd_c,coins,token,net,addr,status,created) VALUES(?,?,?,?,?,?,?,?)",
                  (u["id"], usd_c, coins, token, net, addr, "pending", now_ms()))
        masked = addr[:6] + "..." + addr[-4:]
        add_tx(c, u["id"], "out", "out", f"{token} · {net}", usd_c / 100, None, masked + " · pending")
    return {"wallet": wallet_json(u["id"])}


@app.post("/api/premium/cancel")
def cancel_premium(req: Request):
    u = current_user(req)
    with _lock:
        db.execute("UPDATE wallets SET prem=0 WHERE user_id=?", (u["id"],))
    return {"wallet": wallet_json(u["id"])}


# ---------- payments ----------
def credit(pid: str):
    """Credit a paid payment exactly once."""
    with Tx() as c:
        p = c.execute("SELECT * FROM payments WHERE id=?", (pid,)).fetchone()
        if not p or p["credited"]:
            return
        uid = p["user_id"]
        if p["kind"] == "pack":
            coins, cents = PACKS[p["item"]]
            c.execute("UPDATE wallets SET coins=coins+? WHERE user_id=?", (coins, uid))
            add_tx(c, uid, "top", "in", "Spicy Wallet", cents / 100, coins, f"Coin pack ${cents / 100:.2f}" + (" · test" if p["provider"] == "test" else ""))
        else:
            name, cents, months = PLANS[p["item"]]
            w = c.execute("SELECT prem FROM wallets WHERE user_id=?", (uid,)).fetchone()
            start = max(w["prem"], now_ms())
            c.execute("UPDATE wallets SET prem=?, coins=coins+? WHERE user_id=?", (start + months * 30 * DAY, 100 * months, uid))
            add_tx(c, uid, "mall", "out", "Spicy Premium " + name, cents / 100, None, "Platform membership" + (" · test" if p["provider"] == "test" else ""))
        c.execute("UPDATE payments SET credited=1, status='paid' WHERE id=?", (pid,))


def stripe(method, path, data=None):
    r = requests.request(method, "https://api.stripe.com/v1" + path, data=data, auth=(STRIPE_KEY, ""), timeout=30)
    j = r.json()
    if r.status_code >= 400:
        raise HTTPException(502, detail={"error": "Payment provider error: " + j.get("error", {}).get("message", "unknown")})
    return j


@app.post("/api/pay/checkout")
async def checkout(req: Request):
    u = current_user(req)
    b = await req.json()
    kind = b.get("kind")
    i = int(b.get("i", -1))
    if kind == "pack" and 0 <= i < len(PACKS):
        coins, cents = PACKS[i]
        title = f"{coins} Spicy Dollz"
    elif kind == "premium" and 0 <= i < len(PLANS):
        name, cents, months = PLANS[i]
        title = f"Spicy Premium · {name}"
        if wallet_row(u["id"])["prem"] > now_ms():
            err(409, "Spicy Premium is already active.")
    else:
        err(400, "Unknown product.")
    pid = uuid.uuid4().hex
    ret = str(b.get("returnUrl", "")).split("#")[0][:500]
    if STRIPE_KEY:
        if not ret.startswith(("https://", "http://")):
            ret = "https://stripe.com"
        s = stripe("POST", "/checkout/sessions", {
            "mode": "payment",
            "line_items[0][quantity]": 1,
            "line_items[0][price_data][currency]": "usd",
            "line_items[0][price_data][unit_amount]": cents,
            "line_items[0][price_data][product_data][name]": title,
            "client_reference_id": u["id"],
            "customer_email": u["email"],
            "metadata[payment_id]": pid,
            "success_url": ret + "#paid",
            "cancel_url": ret + "#cancelled",
        })
        with _lock:
            db.execute("INSERT INTO payments VALUES(?,?,?,?,?,?,?,?,?,0)", (pid, u["id"], kind, i, cents, "stripe", s["id"], "open", now_ms()))
        return {"mode": "stripe", "id": pid, "url": s["url"]}
    if TEST_MODE:
        with _lock:
            db.execute("INSERT INTO payments VALUES(?,?,?,?,?,?,?,?,?,0)", (pid, u["id"], kind, i, cents, "test", None, "open", now_ms()))
        credit(pid)
        return {"mode": "test", "id": pid, "status": "paid", "wallet": wallet_json(u["id"])}
    err(503, "Payments are not set up yet.")


@app.get("/api/pay/{pid}")
def pay_status(pid: str, req: Request):
    u = current_user(req)
    p = q1("SELECT * FROM payments WHERE id=? AND user_id=?", pid, u["id"])
    if not p:
        err(404, "Payment not found.")
    if not p["credited"] and p["provider"] == "stripe" and STRIPE_KEY:
        s = stripe("GET", f"/checkout/sessions/{p['ext_id']}")
        if s.get("payment_status") == "paid":
            credit(pid)
        elif s.get("status") == "expired":
            with _lock:
                db.execute("UPDATE payments SET status='expired' WHERE id=?", (pid,))
    p = q1("SELECT * FROM payments WHERE id=?", pid)
    return {"status": p["status"], "wallet": wallet_json(u["id"]) if p["credited"] else None}


@app.post("/api/stripe/webhook")
async def stripe_webhook(req: Request):
    payload = await req.body()
    if STRIPE_WHSEC:
        sig = req.headers.get("stripe-signature", "")
        parts = dict(x.split("=", 1) for x in sig.split(",") if "=" in x)
        t = parts.get("t", "")
        expected = hmac.new(STRIPE_WHSEC.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
        if not t or not hmac.compare_digest(expected, parts.get("v1", "")) or abs(time.time() - int(t)) > 600:
            return JSONResponse({"error": "bad signature"}, status_code=400)
    else:
        return JSONResponse({"error": "webhook secret not set"}, status_code=400)
    ev = json.loads(payload)
    if ev.get("type") in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
        obj = ev["data"]["object"]
        pid = (obj.get("metadata") or {}).get("payment_id")
        if pid and obj.get("payment_status") == "paid":
            credit(pid)
    return {"received": True}



# ======================= social =======================
def today():
    return time.strftime("%Y-%m-%d", time.gmtime())


def bump(c, uid, field, n=1):
    c.execute(f"INSERT INTO daily(user_id,day,{field}) VALUES(?,?,?) ON CONFLICT(user_id,day) DO UPDATE SET {field}={field}+?", (uid, today(), n, n))


_seen = {}


def count_view(v, viewer_id):
    key = (v["id"], viewer_id or "anon")
    t = time.time()
    if t - _seen.get(key, 0) < 1800 or (viewer_id and viewer_id == v["user_id"]):
        return
    _seen[key] = t
    with Tx() as c:
        c.execute("UPDATE videos SET views=views+1 WHERE id=?", (v["id"],))
        bump(c, v["user_id"], "views")


def mini(u):
    if not u:
        return None
    av = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_avatar'", u["id"])
    return {"handle": u["handle"], "name": u["name"], "avatar": av["v"] if av else None,
            "premium": wallet_row(u["id"])["prem"] > now_ms()}


_mini_cache = {}


def mini_id(uid):
    r = q1("SELECT * FROM users WHERE id=?", uid)
    return mini(r)


def blocked_ids(uid):
    if not uid:
        return set()
    return {r["x"] for r in qa("SELECT blocked x FROM blocks WHERE blocker=? UNION SELECT blocker x FROM blocks WHERE blocked=?", uid, uid)}


def is_blocked(a, b):
    return bool(q1("SELECT 1 FROM blocks WHERE (blocker=? AND blocked=?) OR (blocker=? AND blocked=?)", a, b, b, a))


def notify(c, uid, kind, actor, text, video_id=None):
    if uid == actor:
        return
    c.execute("INSERT INTO notifs(user_id,kind,actor_id,video_id,text,created) VALUES(?,?,?,?,?,?)", (uid, kind, actor, video_id, text, now_ms()))


def post_rows(where, args, limit, viewer):
    bl = blocked_ids(viewer)
    rows = qa(f"SELECT v.* FROM videos v JOIN users u ON u.id=v.user_id WHERE v.removed=0 AND u.banned=0 AND {where} LIMIT ?", *args, limit * 2 + 20)
    out, cache = [], {}
    for v in rows:
        if v["user_id"] in bl:
            continue
        if v["user_id"] not in cache:
            cache[v["user_id"]] = mini_id(v["user_id"])
        j = video_json(v, viewer, cache[v["user_id"]], play=True)
        j["following"] = bool(viewer and q1("SELECT 1 FROM follows WHERE follower=? AND followee=?", viewer, v["user_id"]))
        j["mine"] = viewer == v["user_id"]
        out.append(j)
        if len(out) >= limit:
            break
    return out


def score_sort(items):
    t = now_ms()
    def sc(j):
        age_h = max(0, (t - j["created"]) / 3600000)
        return (j["likes"] * 3 + j["comments"] * 4 + j["views"] + 2) / ((age_h + 2) ** 1.15)
    return sorted(items, key=sc, reverse=True)


@app.get("/api/feed")
def feed(req: Request, tag: str = "", scope: str = "for", limit: int = 30):
    u = current_user(req, required=False)
    viewer = u["id"] if u else None
    limit = max(1, min(60, limit))
    if tag:
        t = re.sub(r"[^a-z0-9_]", "", tag.lower().lstrip("#"))[:30]
        return score_sort(post_rows("v.tags LIKE ? ORDER BY v.created DESC", [f'%"{t}"%'], limit, viewer))
    if scope == "following" and viewer:
        return post_rows("v.user_id IN (SELECT followee FROM follows WHERE follower=?) ORDER BY v.created DESC", [viewer], limit, viewer)
    items = post_rows("1=1 ORDER BY v.created DESC", [], 200, viewer)
    if viewer:
        fol = {r["followee"] for r in qa("SELECT followee FROM follows WHERE follower=?", viewer)}
        prefs = q1("SELECT v FROM kv WHERE user_id=? AND k='sd_w3'", viewer)
        liked_tags = set(((json.loads(prefs["v"]) if prefs else {}).get("set") or {}).get("tags") or [])
        for j in items:
            boost = (2.5 if j["user"] and j["user"]["handle"] and j["following"] else 1) * (1.6 if liked_tags & set(j["tags"]) else 1)
            j["_b"] = boost
    ranked = score_sort(items)
    if viewer:
        pos = {j["id"]: i for i, j in enumerate(ranked)}
        ranked.sort(key=lambda j: -j.get("_b", 1) / (1 + pos[j["id"]]))
    for j in ranked:
        j.pop("_b", None)
    return ranked[:limit]


@app.get("/api/home")
def home(req: Request):
    u = current_user(req, required=False)
    viewer = u["id"] if u else None
    bl = blocked_ids(viewer)
    pub = [j for j in post_rows("1=1 ORDER BY v.created DESC", [], 120, viewer)]
    popular = score_sort(pub)[:12]
    creators = qa("""SELECT u.*, (SELECT COUNT(*) FROM follows f WHERE f.followee=u.id) f,
                     (SELECT COUNT(*) FROM subs s WHERE s.creator=u.id AND s.expires>?) s,
                     (SELECT COUNT(*) FROM videos v WHERE v.user_id=u.id AND v.removed=0) p
                     FROM users u WHERE u.banned=0""", now_ms())
    creators = [c for c in creators if c["id"] not in bl and c["id"] != viewer]
    top = sorted([c for c in creators if c["p"] > 0], key=lambda c: (c["f"] + 3 * c["s"], c["p"]), reverse=True)[:10]
    newest = sorted(creators, key=lambda c: c["created"], reverse=True)[:10]
    tagc = {}
    for j in pub:
        for t in j["tags"]:
            tagc[t] = tagc.get(t, 0) + 1
    tags = sorted(tagc.items(), key=lambda x: -x[1])[:12]
    rows = [{"tag": t, "posts": [j for j in popular + pub if t in j["tags"]][:8]} for t, _ in tags[:3]]
    for r in rows:
        seen, uniq = set(), []
        for j in r["posts"]:
            if j["id"] not in seen:
                seen.add(j["id"]); uniq.append(j)
        r["posts"] = uniq
    def cj(c):
        m = mini(c); m["followers"] = c["f"]; m["posts"] = c["p"]; return m
    return {"popular": popular, "top": [cj(c) for c in top], "newest": [cj(c) for c in newest],
            "tags": [{"tag": t, "n": n} for t, n in tags], "rows": rows}


@app.get("/api/search")
def search(req: Request, q: str = ""):
    u = current_user(req, required=False)
    bl = blocked_ids(u["id"] if u else None)
    qq = q.strip().lstrip("@#").lower()[:40]
    if not qq:
        return {"creators": [], "tags": []}
    rows = qa("SELECT * FROM users WHERE banned=0 AND (name_l LIKE ? OR handle_l LIKE ?) ORDER BY created DESC LIMIT 20", f"%{qq}%", f"%{qq}%")
    tagc = {}
    for r in qa("SELECT tags FROM videos WHERE removed=0 AND tags LIKE ?", f"%{qq}%"):
        for t in json.loads(r["tags"]):
            if qq in t:
                tagc[t] = tagc.get(t, 0) + 1
    return {"creators": [mini(r) for r in rows if r["id"] not in bl],
            "tags": [{"tag": t, "n": n} for t, n in sorted(tagc.items(), key=lambda x: -x[1])[:10]]}


@app.get("/api/videos/{vid}")
def get_post(vid: str, req: Request):
    u = current_user(req, required=False)
    r = post_rows("v.id=?", [vid], 1, u["id"] if u else None)
    if not r:
        err(404, "This post was removed.")
    return r[0]


@app.post("/api/videos/{vid}/view")
def view_post(vid: str, req: Request):
    u = current_user(req, required=False)
    v = q1("SELECT * FROM videos WHERE id=? AND removed=0", vid)
    if v and can_watch(v, u["id"] if u else None):
        count_view(v, u["id"] if u else None)
    return {"ok": True}


@app.post("/api/videos/{vid}/like")
async def like_post(vid: str, req: Request):
    u = current_user(req)
    b = await req.json()
    v = q1("SELECT * FROM videos WHERE id=? AND removed=0", vid)
    if not v:
        err(404, "This post was removed.")
    want = bool(b.get("on", True))
    with Tx() as c:
        had = c.execute("SELECT 1 FROM likes WHERE user_id=? AND video_id=?", (u["id"], vid)).fetchone()
        if want and not had:
            c.execute("INSERT INTO likes VALUES(?,?,?)", (u["id"], vid, now_ms()))
            bump(c, v["user_id"], "likes")
            notify(c, v["user_id"], "like", u["id"], "liked your post", vid)
        elif not want and had:
            c.execute("DELETE FROM likes WHERE user_id=? AND video_id=?", (u["id"], vid))
    return {"liked": want, "likes": q1("SELECT COUNT(*) n FROM likes WHERE video_id=?", vid)["n"]}


@app.get("/api/videos/{vid}/comments")
def list_comments(vid: str, req: Request):
    u = current_user(req, required=False)
    bl = blocked_ids(u["id"] if u else None)
    v = q1("SELECT user_id FROM videos WHERE id=?", vid)
    rows = qa("SELECT c.*, u.handle, u.name FROM comments c JOIN users u ON u.id=c.user_id WHERE c.video_id=? AND u.banned=0 ORDER BY c.created LIMIT 500", vid)
    return [{"id": r["id"], "handle": r["handle"], "name": r["name"], "text": r["text"], "created": r["created"],
             "mine": bool(u and (u["id"] == r["user_id"] or (v and v["user_id"] == u["id"]) or u["role"] == "admin"))}
            for r in rows if r["user_id"] not in bl]


@app.post("/api/videos/{vid}/comments")
async def add_comment(vid: str, req: Request):
    u = current_user(req)
    b = await req.json()
    text = str(b.get("text", "")).strip()[:500]
    if not text:
        err(400, "Write a comment first.")
    rate_limit("cm:" + u["id"], 20, 60)
    v = q1("SELECT * FROM videos WHERE id=? AND removed=0", vid)
    if not v:
        err(404, "This post was removed.")
    if is_blocked(u["id"], v["user_id"]):
        err(403, "You can't comment on this post.")
    if not can_watch(v, u["id"]):
        err(403, "Subscribe to comment on this post.")
    with Tx() as c:
        cur = c.execute("INSERT INTO comments(video_id,user_id,text,created) VALUES(?,?,?,?)", (vid, u["id"], text, now_ms()))
        notify(c, v["user_id"], "comment", u["id"], "commented: " + text[:60], vid)
    return {"id": cur.lastrowid, "handle": u["handle"], "name": u["name"], "text": text, "created": now_ms(), "mine": True}


@app.delete("/api/comments/{cid}")
def del_comment(cid: int, req: Request):
    u = current_user(req)
    r = q1("SELECT c.*, v.user_id owner FROM comments c JOIN videos v ON v.id=c.video_id WHERE c.id=?", cid)
    if not r:
        err(404, "Comment not found.")
    if u["id"] not in (r["user_id"], r["owner"]) and u["role"] != "admin":
        err(403, "You can't delete this comment.")
    with _lock:
        db.execute("DELETE FROM comments WHERE id=?", (cid,))
    return {"ok": True}


def user_by_handle(h):
    u = q1("SELECT * FROM users WHERE handle_l=? AND banned=0", str(h).lstrip("@").lower())
    if not u:
        err(404, "No creator with that name.")
    return u


@app.post("/api/follow/{handle}")
async def follow(handle: str, req: Request):
    u = current_user(req)
    b = await req.json()
    t = user_by_handle(handle)
    if t["id"] == u["id"]:
        err(400, "You can't follow yourself.")
    if is_blocked(u["id"], t["id"]):
        err(403, "You can't follow this account.")
    want = bool(b.get("on", True))
    with Tx() as c:
        had = c.execute("SELECT 1 FROM follows WHERE follower=? AND followee=?", (u["id"], t["id"])).fetchone()
        if want and not had:
            c.execute("INSERT INTO follows VALUES(?,?,?)", (u["id"], t["id"], now_ms()))
            bump(c, t["id"], "followers")
            notify(c, t["id"], "follow", u["id"], "started following you")
        elif not want and had:
            c.execute("DELETE FROM follows WHERE follower=? AND followee=?", (u["id"], t["id"]))
            bump(c, t["id"], "followers", -1)
    return {"following": want, "followers": q1("SELECT COUNT(*) n FROM follows WHERE followee=?", t["id"])["n"]}


@app.get("/api/users/{handle}/list/{kind}")
def follow_list(handle: str, kind: str, req: Request):
    t = user_by_handle(handle)
    if kind == "followers":
        rows = qa("SELECT u.* FROM follows f JOIN users u ON u.id=f.follower WHERE f.followee=? AND u.banned=0 ORDER BY f.created DESC LIMIT 200", t["id"])
    else:
        rows = qa("SELECT u.* FROM follows f JOIN users u ON u.id=f.followee WHERE f.follower=? AND u.banned=0 ORDER BY f.created DESC LIMIT 200", t["id"])
    return [mini(r) for r in rows]


@app.get("/api/me/liked")
def my_liked(req: Request):
    u = current_user(req)
    return post_rows("v.id IN (SELECT video_id FROM likes WHERE user_id=?) ORDER BY v.created DESC", [u["id"]], 60, u["id"])


# ---------- messages + notifications ----------
@app.get("/api/inbox")
def inbox(req: Request):
    u = current_user(req)
    me = u["id"]
    bl = blocked_ids(me)
    rows = qa("""SELECT CASE WHEN from_id=? THEN to_id ELSE from_id END other, MAX(created) last
                 FROM messages WHERE from_id=? OR to_id=? GROUP BY other ORDER BY last DESC LIMIT 100""", me, me, me)
    convs = []
    for r in rows:
        if r["other"] in bl:
            continue
        o = q1("SELECT * FROM users WHERE id=?", r["other"])
        if not o or o["banned"]:
            continue
        lm = q1("SELECT * FROM messages WHERE ((from_id=? AND to_id=?) OR (from_id=? AND to_id=?)) ORDER BY created DESC LIMIT 1", me, o["id"], o["id"], me)
        unread = q1("SELECT COUNT(*) n FROM messages WHERE from_id=? AND to_id=? AND read_at IS NULL", o["id"], me)["n"]
        replied = q1("SELECT 1 FROM messages WHERE from_id=? AND to_id=?", me, o["id"])
        follows_them = q1("SELECT 1 FROM follows WHERE follower=? AND followee=?", me, o["id"])
        m = mini(o)
        m.update({"last": lm["text"][:80], "lastMine": lm["from_id"] == me, "at": lm["created"], "unread": unread,
                  "folder": "main" if (replied or follows_them) else "req",
                  "active": bool(q1("SELECT 1 FROM sessions WHERE user_id=? AND seen>?", o["id"], now_ms() - 300000))})
        convs.append(m)
    nts = qa("SELECT * FROM notifs WHERE user_id=? ORDER BY created DESC LIMIT 60", me)
    notifs = []
    for n in nts:
        a = mini_id(n["actor_id"]) if n["actor_id"] else None
        if n["actor_id"] in bl:
            continue
        notifs.append({"id": n["id"], "kind": n["kind"], "text": n["text"], "at": n["created"], "read": bool(n["read"]),
                       "actor": a, "video": n["video_id"]})
    return {"convs": convs, "notifs": notifs,
            "unread": sum(c["unread"] for c in convs) + sum(1 for n in notifs if not n["read"])}


@app.post("/api/notifs/read")
def notifs_read(req: Request):
    u = current_user(req)
    with _lock:
        db.execute("UPDATE notifs SET read=1 WHERE user_id=?", (u["id"],))
    return {"ok": True}


@app.get("/api/inbox/{handle}")
def thread(handle: str, req: Request, after: int = 0):
    u = current_user(req)
    o = user_by_handle(handle)
    rows = qa("""SELECT * FROM messages WHERE ((from_id=? AND to_id=?) OR (from_id=? AND to_id=?)) AND id>?
                 ORDER BY id DESC LIMIT 200""", u["id"], o["id"], o["id"], u["id"], after)
    with _lock:
        db.execute("UPDATE messages SET read_at=? WHERE from_id=? AND to_id=? AND read_at IS NULL", (now_ms(), o["id"], u["id"]))
    return {"user": mini(o), "blocked": is_blocked(u["id"], o["id"]),
            "messages": [{"id": r["id"], "mine": r["from_id"] == u["id"], "text": r["text"], "at": r["created"],
                          "read": bool(r["read_at"])} for r in reversed(rows)]}


@app.post("/api/inbox/{handle}")
async def send_msg(handle: str, req: Request):
    u = current_user(req)
    b = await req.json()
    o = user_by_handle(handle)
    text = str(b.get("text", "")).strip()[:1000]
    if not text:
        err(400, "Write a message first.")
    if o["id"] == u["id"]:
        err(400, "You can't message yourself.")
    if is_blocked(u["id"], o["id"]):
        err(403, "You can't message this account.")
    rate_limit("msg:" + u["id"], 30, 60)
    with Tx() as c:
        cur = c.execute("INSERT INTO messages(from_id,to_id,text,created) VALUES(?,?,?,?)", (u["id"], o["id"], text, now_ms()))
    return {"id": cur.lastrowid, "mine": True, "text": text, "at": now_ms(), "read": False}


# ---------- blocks + reports ----------
@app.get("/api/blocks")
def list_blocks(req: Request):
    u = current_user(req)
    return [mini(r) for r in qa("SELECT u.* FROM blocks b JOIN users u ON u.id=b.blocked WHERE b.blocker=?", u["id"])]


@app.post("/api/blocks")
async def add_block(req: Request):
    u = current_user(req)
    b = await req.json()
    t = q1("SELECT * FROM users WHERE handle_l=?", str(b.get("handle", "")).lstrip("@").lower())
    if not t:
        err(404, "No account with that name.")
    if t["id"] == u["id"]:
        err(400, "You cannot block yourself.")
    with Tx() as c:
        c.execute("INSERT OR IGNORE INTO blocks VALUES(?,?)", (u["id"], t["id"]))
        c.execute("DELETE FROM follows WHERE (follower=? AND followee=?) OR (follower=? AND followee=?)", (u["id"], t["id"], t["id"], u["id"]))
    return mini(t)


@app.delete("/api/blocks/{handle}")
def del_block(handle: str, req: Request):
    u = current_user(req)
    t = q1("SELECT * FROM users WHERE handle_l=?", handle.lstrip("@").lower())
    if t:
        with _lock:
            db.execute("DELETE FROM blocks WHERE blocker=? AND blocked=?", (u["id"], t["id"]))
    return {"ok": True}


@app.post("/api/report")
async def report(req: Request):
    u = current_user(req)
    b = await req.json()
    rate_limit("rp:" + u["id"], 20, 3600)
    reason = re.sub(r"[<>]", "", str(b.get("reason", "")))[:300] or "Other"
    vid = b.get("video")
    tu = None
    if b.get("handle"):
        t = q1("SELECT id FROM users WHERE handle_l=?", str(b["handle"]).lstrip("@").lower())
        tu = t["id"] if t else None
    if not vid and not tu and not b.get("comment"):
        err(400, "Nothing to report.")
    with _lock:
        db.execute("INSERT INTO reports(reporter,video_id,target_user,comment_id,reason,created) VALUES(?,?,?,?,?,?)",
                   (u["id"], vid, tu, b.get("comment"), reason, now_ms()))
    return {"ok": True}


def need_admin(req):
    u = current_user(req)
    if u["role"] != "admin":
        err(403, "Admins only.")
    return u


@app.get("/api/admin/reports")
def admin_reports(req: Request):
    need_admin(req)
    out = []
    for r in qa("SELECT * FROM reports WHERE status='open' ORDER BY created DESC LIMIT 100"):
        v = q1("SELECT * FROM videos WHERE id=?", r["video_id"]) if r["video_id"] else None
        tu = q1("SELECT * FROM users WHERE id=?", r["target_user"] or (v["user_id"] if v else "")) if (r["target_user"] or v) else None
        rp = q1("SELECT handle FROM users WHERE id=?", r["reporter"]) if r["reporter"] else None
        out.append({"id": r["id"], "reason": r["reason"], "at": r["created"], "reporter": rp["handle"] if rp else None,
                    "video": {"id": v["id"], "caption": v["caption"], "kind": v["kind"], "removed": bool(v["removed"]),
                              "url": sign(f"/media/vid/{v['file']}")} if v else None,
                    "user": {"handle": tu["handle"], "name": tu["name"], "banned": bool(tu["banned"])} if tu else None})
    return out


@app.post("/api/admin/reports/{rid}/close")
def admin_close(rid: int, req: Request):
    need_admin(req)
    with _lock:
        db.execute("UPDATE reports SET status='closed' WHERE id=?", (rid,))
    return {"ok": True}


@app.post("/api/admin/posts/{vid}/remove")
def admin_remove(vid: str, req: Request):
    need_admin(req)
    with _lock:
        db.execute("UPDATE videos SET removed=1 WHERE id=?", (vid,))
        db.execute("UPDATE reports SET status='closed' WHERE video_id=?", (vid,))
    return {"ok": True}


@app.post("/api/admin/users/{handle}/ban")
async def admin_ban(handle: str, req: Request):
    a = need_admin(req)
    b = await req.json()
    t = q1("SELECT * FROM users WHERE handle_l=?", handle.lower())
    if not t or t["id"] == a["id"]:
        err(400, "Can't change that account.")
    on = 1 if b.get("on", True) else 0
    with _lock:
        db.execute("UPDATE users SET banned=? WHERE id=?", (on, t["id"]))
        if on:
            db.execute("DELETE FROM sessions WHERE user_id=?", (t["id"],))
            db.execute("UPDATE reports SET status='closed' WHERE target_user=?", (t["id"],))
    return {"ok": True}


# ---------- stats ----------
@app.get("/api/stats")
def stats(req: Request, days: int = 30):
    u = current_user(req)
    days = max(7, min(365, days))
    rows = {r["day"]: r for r in qa("SELECT * FROM daily WHERE user_id=? AND day>=?", u["id"],
                                     time.strftime("%Y-%m-%d", time.gmtime(time.time() - days * 86400)))}
    series = {"views": [], "likes": [], "followers": [], "subs": []}
    for i in range(days - 1, -1, -1):
        d = time.strftime("%Y-%m-%d", time.gmtime(time.time() - i * 86400))
        r = rows.get(d)
        for k in series:
            series[k].append(r[k] if r else 0)
    return {"totals": user_counts(u["id"]), "daily": series}

# ---------- admin backup ----------
@app.post("/api/admin/backup")
def admin_backup_link(req: Request):
    u = current_user(req)
    if u["role"] != "admin":
        err(403, "Admins only.")
    return {"url": sign("/api/admin/backup/file", ttl=600)}


@app.get("/api/admin/backup/file")
def admin_backup_file(e: str = "", s: str = ""):
    import zipfile
    if not check_sig("/api/admin/backup/file", e, s):
        err(403, "This backup link expired. Create a new one.")
    TMP.mkdir(exist_ok=True)
    for old in TMP.glob("backup-*.zip"):
        old.unlink(missing_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dbcopy = TMP / f"db-{stamp}.sqlite"
    with _lock:
        dst = sqlite3.connect(dbcopy)
        db.backup(dst)
        dst.close()
    out = TMP / f"backup-{stamp}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
        z.write(dbcopy, "spicy.db")
        for f in MEDIA.rglob("*"):
            if f.is_file():
                z.write(f, "media/" + str(f.relative_to(MEDIA)))
    dbcopy.unlink(missing_ok=True)
    return FileResponse(out, filename=f"spicy-dollz-backup-{stamp}.zip", media_type="application/zip")


# ---------- static (self-hosting) ----------
@app.get("/", response_class=HTMLResponse)
def index():
    p = ROOT / "public" / "index.html"
    return FileResponse(p) if p.exists() else HTMLResponse("Spicy Dollz API")


@app.get("/api/health")
def health():
    return {"ok": True, "payments": config_json()["payments"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
