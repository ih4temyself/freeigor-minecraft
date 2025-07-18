import sqlite3
import uuid

DB_PATH = "casino.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = _connect()
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,              -- telegram_id or other external stable id (string)
            mc_nickname TEXT,
            coin_balance INTEGER NOT NULL DEFAULT 0,
            login_code TEXT UNIQUE            -- persistent login token you share to website
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS item_values (
            item_type TEXT PRIMARY KEY,
            coin_value INTEGER NOT NULL
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (item_type) REFERENCES item_values(item_type) ON DELETE CASCADE,
            UNIQUE(user_id, item_type)
        )
    """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    )

    default_items = [
        ("diamond", 10),
        ("gold_ingot", 5),
        ("iron_ingot", 2),
        ("emerald", 8),
    ]
    c.executemany(
        """
        INSERT OR IGNORE INTO item_values (item_type, coin_value) VALUES (?, ?)
    """,
        default_items,
    )

    conn.commit()
    conn.close()


def add_user(user_id, mc_nickname, base_balance=100):
    conn = _connect()
    c = conn.cursor()

    c.execute("SELECT login_code FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if row:
        conn.close()
        return row["login_code"]

    login_code = str(uuid.uuid4())
    c.execute(
        """
        INSERT INTO users (id, mc_nickname, coin_balance, login_code)
        VALUES (?, ?, ?, ?)
    """,
        (user_id, mc_nickname, base_balance, login_code),
    )
    conn.commit()
    conn.close()
    return login_code


def reset_login_code(user_id):
    new_code = str(uuid.uuid4())
    conn = _connect()
    c = conn.cursor()
    c.execute("UPDATE users SET login_code = ? WHERE id = ?", (new_code, user_id))
    if c.rowcount == 0:
        conn.close()
        return None
    conn.commit()
    conn.close()
    return new_code


def get_user(user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row


def validate_login(login_code):
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE login_code = ?", (login_code,))
    row = c.fetchone()
    conn.close()
    return row


def create_session(user_id):
    token = str(uuid.uuid4())
    conn = _connect()
    c = conn.cursor()
    c.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()
    return token


def validate_session(token):
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT user_id FROM sessions WHERE token = ?", (token,))
    row = c.fetchone()
    conn.close()
    return row["user_id"] if row else None


def update_balance(user_id, amount):
    conn = _connect()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET coin_balance = coin_balance + ? WHERE id = ?",
        (amount, user_id),
    )
    conn.commit()
    conn.close()


def get_balance(user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT coin_balance FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row["coin_balance"] if row else None


def add_item(user_id, item_type, quantity):
    conn = _connect()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO inventory (user_id, item_type, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, item_type) DO UPDATE SET quantity = quantity + excluded.quantity
    """,
        (user_id, item_type, quantity),
    )
    conn.commit()
    conn.close()


def get_inventory(user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute(
        """
        SELECT item_type, quantity
        FROM inventory
        WHERE user_id = ?
        ORDER BY item_type
    """,
        (user_id,),
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Quick test bootstrap
if __name__ == "__main__":
    init_db()
    code = add_user("1111121", "bogdan", 5000)
    print("hi, vot tvoi code:", code)
