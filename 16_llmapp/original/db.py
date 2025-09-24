import sqlite3
from flask import g, current_app

DB_NAME = "reports.db"

# =====================
# データベース接続管理
# =====================
def get_db():
    """リクエストごとにDB接続を取得、すでに接続がある場合は再利用"""
    if 'db' not in g:
        try:
            g.db = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
            g.db.row_factory = sqlite3.Row  # カラム名でアクセス可能に
        except sqlite3.Error as e:
            current_app.logger.error(f"DB接続エラー: {e}")
            g.db = None
    return g.db

def close_db(e=None):
    """リクエスト終了時にDB接続を閉じる"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Flaskアプリで使用する場合は、app.pyで以下を設定:
# app.teardown_appcontext(close_db)

# =====================
# 初期化
# =====================
def init_db():
    db = sqlite3.connect(DB_NAME)
    try:
        c = db.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                photo_path TEXT,
                latitude TEXT,
                longitude TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()
    except sqlite3.Error as e:
        print(f"DB初期化エラー: {e}")
    finally:
        db.close()

# =====================
# データ操作
# =====================
def insert_report(photo_path, latitude, longitude):
    db = get_db()
    if db is None:
        return False
    try:
        c = db.cursor()
        c.execute('''
            INSERT INTO reports (photo_path, latitude, longitude)
            VALUES (?, ?, ?)
        ''', (photo_path, latitude, longitude))
        db.commit()
        return True
    except sqlite3.Error as e:
        current_app.logger.error(f"DB挿入エラー: {e}")
        return False

def get_all_reports():
    db = get_db()
    if db is None:
        return []
    try:
        c = db.cursor()
        c.execute('''
            SELECT id, photo_path, latitude, longitude, created_at
            FROM reports
            ORDER BY created_at DESC
        ''')
        rows = c.fetchall()
        return rows
    except sqlite3.Error as e:
        current_app.logger.error(f"DB取得エラー: {e}")
        return []