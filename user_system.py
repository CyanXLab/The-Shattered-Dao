"""
《逆仙录·天道残卷》用户系统
注册/登录/管理员/SQLite持久化
"""
import sqlite3
import os
import hashlib
import secrets
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shattered_dao.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表结构"""
    conn = get_db()
    cur = conn.cursor()
    # 用户表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        created_at REAL,
        last_login REAL
    )
    """)
    # 玩家存档表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS player_saves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        save_name TEXT DEFAULT 'main',
        state_json TEXT,
        updated_at REAL,
        UNIQUE(user_id, save_name),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    # 全局世界状态（单例）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS world_state (
        id INTEGER PRIMARY KEY,
        state_json TEXT,
        updated_at REAL
    )
    """)
    conn.commit()
    # 创建默认管理员
    cur.execute("SELECT id FROM users WHERE username='admin'")
    if not cur.fetchone():
        register("admin", "admin123", is_admin=1)
        print("  默认管理员创建: admin / admin123")
    conn.close()


def _hash_password(password, salt):
    """密码哈希"""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def register(username, password, is_admin=0):
    """注册新用户"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    if cur.fetchone():
        conn.close()
        return {"ok": False, "msg": "用户名已存在"}
    salt = secrets.token_hex(16)
    pwd_hash = _hash_password(password, salt)
    cur.execute(
        "INSERT INTO users (username, password_hash, salt, is_admin, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?)",
        (username, pwd_hash, salt, is_admin, time.time(), time.time())
    )
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return {"ok": True, "msg": "注册成功", "user_id": uid, "username": username, "is_admin": is_admin}


def login(username, password):
    """登录"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, salt, is_admin FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"ok": False, "msg": "用户不存在"}
    pwd_hash = _hash_password(password, row["salt"])
    if pwd_hash != row["password_hash"]:
        conn.close()
        return {"ok": False, "msg": "密码错误"}
    cur.execute("UPDATE users SET last_login=? WHERE id=?", (time.time(), row["id"]))
    conn.commit()
    conn.close()
    return {"ok": True, "msg": "登录成功", "user_id": row["id"], "username": row["username"], "is_admin": row["is_admin"]}


def get_user(user_id):
    """获取用户信息"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, is_admin, created_at, last_login FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def list_users():
    """列出所有用户（管理员用）"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, is_admin, created_at, last_login FROM users ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_user(user_id):
    """删除用户（管理员用，不能删自己）"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM player_saves WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return {"ok": True, "msg": "用户已删除"}


def save_player_state(user_id, state_json, save_name="main"):
    """保存玩家状态"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO player_saves (user_id, save_name, state_json, updated_at) VALUES (?, ?, ?, ?)",
        (user_id, save_name, state_json, time.time())
    )
    conn.commit()
    conn.close()


def load_player_state(user_id, save_name="main"):
    """加载玩家状态"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT state_json FROM player_saves WHERE user_id=? AND save_name=?", (user_id, save_name))
    row = cur.fetchone()
    conn.close()
    return row["state_json"] if row else None


def list_player_saves(user_id):
    """列出玩家所有存档"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT save_name, updated_at FROM player_saves WHERE user_id=? ORDER BY updated_at DESC", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_player_save(user_id, save_name):
    """删除存档"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM player_saves WHERE user_id=? AND save_name=?", (user_id, save_name))
    conn.commit()
    conn.close()


def save_world_state(state_json):
    """保存全局世界状态"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO world_state (id, state_json, updated_at) VALUES (1, ?, ?)",
                (state_json, time.time()))
    conn.commit()
    conn.close()


def load_world_state():
    """加载全局世界状态"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT state_json FROM world_state WHERE id=1")
    row = cur.fetchone()
    conn.close()
    return row["state_json"] if row else None


# 初始化
init_db()
