import os, sqlite3, secrets, hashlib, hmac, re
from pathlib import Path
DB_PATH=os.environ.get("UNIVERSE_DB_PATH",str(Path(__file__).resolve().parents[1]/"data"/"universe.db"))
Path(DB_PATH).parent.mkdir(parents=True,exist_ok=True)
def connect():
    c=sqlite3.connect(DB_PATH,timeout=15); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,full_name TEXT NOT NULL,email TEXT NOT NULL UNIQUE COLLATE NOCASE,password_hash TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,title TEXT NOT NULL,discipline TEXT NOT NULL,task_type TEXT NOT NULL,prompt TEXT NOT NULL,result_json TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'completed',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
def normalize_email(email): return (email or "").strip().lower()
def validate_password(p):
    if len(p)<10:return "Password must contain at least 10 characters."
    if not re.search(r"[A-Z]",p):return "Password must include an uppercase letter."
    if not re.search(r"[a-z]",p):return "Password must include a lowercase letter."
    if not re.search(r"\d",p):return "Password must include a number."
    if not re.search(r"[^A-Za-z0-9]",p):return "Password must include a symbol."
    return None
def hash_password(password):
    salt=secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,600000)
    return f"pbkdf2_sha256$600000${salt.hex()}${digest.hex()}"
def verify_password(password,encoded):
    try:
        algo,rounds,salt,digest=encoded.split("$")
        if algo!="pbkdf2_sha256":return False
        actual=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),int(rounds)).hex()
        return hmac.compare_digest(actual,digest)
    except (ValueError,TypeError):return False
def safe_user(row):
    return None if not row else {"id":row["id"],"full_name":row["full_name"],"email":row["email"],"created_at":row["created_at"]}
def create_user(name,email,password):
    email=normalize_email(email)
    with connect() as c:
        if c.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone():raise ValueError("An account with this email already exists. Please log in.")
        try: cur=c.execute("INSERT INTO users(full_name,email,password_hash) VALUES(?,?,?)",(name.strip(),email,hash_password(password)))
        except sqlite3.IntegrityError:raise ValueError("An account with this email already exists. Please log in.")
        return safe_user(c.execute("SELECT * FROM users WHERE id=?",(cur.lastrowid,)).fetchone())
def authenticate_user(email,password):
    with connect() as c:
        row=c.execute("SELECT * FROM users WHERE email=?",(normalize_email(email),)).fetchone()
        return safe_user(row) if row and verify_password(password,row["password_hash"]) else None
def get_user_by_email(email):
    with connect() as c:return safe_user(c.execute("SELECT * FROM users WHERE email=?",(normalize_email(email),)).fetchone())
def update_password(user_id,password):
    with connect() as c:c.execute("UPDATE users SET password_hash=? WHERE id=?",(hash_password(password),int(user_id)))
