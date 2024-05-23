# Aristo Baadi - 41823010006
# Universitas Mercu Buana
# Tugas 5 - Pemrograman Lanjut

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
import mysql.connector
from mysql.connector import Error
from passlib.context import CryptContext

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Konfigurasi database
db_config = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'user_auth'
}

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fungsi untuk membuat koneksi ke database
def create_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Halaman login dan sign-up
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login_signup.html", {"request": request})

# Endpoint sign-up
@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    hashed_password = pwd_context.hash(password)
    connection = create_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()
    except Error as e:
        return {"message": f"Error: {e}"}
    finally:
        cursor.close()
        connection.close()
    return {"message": "Sign-up successful, please log in"}

# Endpoint login
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    connection = create_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
        user = cursor.fetchone()
        if user and pwd_context.verify(form_data.password, user['password']):
            return {"message": "Selamat datang"}
        else:
            return {"message": "Data salah"}
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)