import sqlite3
import uuid

def init_db():
    conn = sqlite3.connect('casino.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    coin_balance INTEGER DEFAULT 0,
                    mc_nickname TEXT,
                    login_code TEXT UNIQUE
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    user_id TEXT,
                    item_type TEXT,
                    quantity INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS item_values (
                    item_type TEXT PRIMARY KEY,
                    coin_value INTEGER
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    default_items = [
        ('diamond', 10),
        ('gold_ingot', 5),
        ('iron_ingot', 2),
        ('emerald', 8)
    ]
    c.executemany('INSERT OR IGNORE INTO item_values (item_type, coin_value) VALUES (?, ?)', default_items)
    conn.commit()
    conn.close()

def add_user(user_id, mc_nickname, base_balance=100):
    conn = sqlite3.connect('casino.db')
    c = conn.cursor()
    c.execute('SELECT login_code FROM users WHERE id = ?', (user_id,))
    existing_user = c.fetchone()
    if existing_user:
        conn.close()
        return existing_user[0]  
    login_code = str(uuid.uuid4())
    try:
        c.execute('''INSERT INTO users (id, coin_balance, mc_nickname, login_code)
                     VALUES (?, ?, ?, ?)''', (user_id, base_balance, mc_nickname, login_code))
        conn.commit()
        return login_code
    except sqlite3.IntegrityError:
        conn.close()
        return None
    finally:
        conn.close()

def get_user(user_id):
    """retrieve user data by tg id"""
    conn = sqlite3.connect('casino.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def validate_login(login_code):
    """validate login code for the website."""
    conn = sqlite3.connect('casino.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE login_code = ?', (login_code,))
    user = c.fetchone()
    conn.close()
    return user

def create_session(user_id):
    """create a session token for a user"""
    conn = sqlite3.connect('casino.db')
    c = conn.cursor()
    token = str(uuid.uuid4())
    c.execute('INSERT INTO sessions (token, user_id) VALUES (?, ?)', (token, user_id))
    conn.commit()
    conn.close()
    return token

def validate_session(token, user_id):
    """validate a session token for a user."""
    conn = sqlite3.connect('casino.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT user_id FROM sessions WHERE token = ? AND user_id = ?', (token, user_id))
    session = c.fetchone()
    conn.close()
    return session is not None

def update_balance(user_id, amount):
    """update user's coin balance (positive or negative amount)."""
    conn = sqlite3.connect('casino.db')
    c = conn.cursor()
    c.execute('UPDATE users SET coin_balance = coin_balance + ? WHERE id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def add_item(user_id, item_type, quantity):
    """Add items to a user's inventory."""
    conn = sqlite3.connect('casino.db')
    c = conn.cursor()
    c.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_type = ?', (user_id, item_type))
    existing = c.fetchone()
    if existing:
        c.execute('UPDATE inventory SET quantity = quantity + ? WHERE user_id = ? AND item_type = ?',
                  (quantity, user_id, item_type))
    else:
        c.execute('INSERT INTO inventory (user_id, item_type, quantity) VALUES (?, ?, ?)',
                  (user_id, item_type, quantity))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()

    login_code = add_user('1111121', 'bogdan', 5000)
    print(f"hi, vot tvoi code: {login_code}")