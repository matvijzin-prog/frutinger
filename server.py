from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('frutinger.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            avatar TEXT DEFAULT '🍎',
            status TEXT DEFAULT 'В сети'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def read_root():
    return FileResponse("index.html")

# === ВХОД И РЕГИСТРАЦИЯ ===
@app.post("/login")
async def login_user(request: Request):
    data = await request.json()
    username = data["username"]
    password = data["password"]
    
    conn = sqlite3.connect('frutinger.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user is None:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return {"status": "registered", "message": "Аккаунт создан!"}
    else:
        if user[0] == password:
            conn.close()
            return {"status": "success", "message": "Вход выполнен!"}
        else:
            conn.close()
            return {"status": "error", "message": "Неверный пароль!"}

# === ПОЛЬЗОВАТЕЛИ ===
@app.get("/users")
def get_users():
    conn = sqlite3.connect('frutinger.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, avatar, status FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [{"username": row[0], "avatar": row[1], "status": row[2]} for row in rows]

# === СООБЩЕНИЯ ===
@app.get("/messages")
def get_messages():
    conn = sqlite3.connect('frutinger.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, text FROM messages ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "text": row[2]} for row in rows]

@app.post("/send")
async def send_message(request: Request):
    data = await request.json()
    conn = sqlite3.connect('frutinger.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (name, text) VALUES (?, ?)", (data["name"], data["text"]))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.delete("/delete/{msg_id}")
def delete_message(msg_id: int):
    conn = sqlite3.connect('frutinger.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@app.put("/edit/{msg_id}")
async def edit_message(msg_id: int, request: Request):
    data = await request.json()
    conn = sqlite3.connect('frutinger.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET text = ? WHERE id = ?", (data["text"], msg_id))
    conn.commit()
    conn.close()
    return {"status": "edited"}