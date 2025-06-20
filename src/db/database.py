from sqlalchemy import create_engine, Column, Integer, String # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker# type: ignore
import mysql.connector
import hashlib

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",  # <-- CORREGIDO
    "password": "",  # tu contraseña de MySQL, si tienes una
    "database": "lnmgia_ucama_isc03mb"
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()  # Return a session for database operations

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def add_user(username, password, email, nombre="Admin", edad=18):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Verifica si el usuario ya existe
    cursor.execute("SELECT * FROM usuario WHERE user = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False, "El usuario ya existe."
    # Verifica si el correo ya existe
    cursor.execute("SELECT * FROM usuario WHERE correo = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False, "El correo ya está registrado."
    hashed = hash_password(password)
    cursor.execute(
        "INSERT INTO usuario (user, passwerd, correo, nombre, edad, puntos) VALUES (%s, %s, %s, %s, %s, %s)",
        (username, hashed, email, nombre, edad, 1500)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Usuario creado correctamente."

def get_user(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuario WHERE user = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def update_points(username, new_points):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuario SET puntos = %s WHERE user = %s", (new_points, username))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuario WHERE user = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and user["passwerd"] == hash_password(password):
        return True
    return False

def add_points(username, points):
    user = get_user(username)
    if not user:
        return False
    new_points = int(user["puntos"]) + int(points)
    return update_points(username, new_points)

def subtract_points(username, points):
    user = get_user(username)
    if not user:
        return False
    new_points = max(0, int(user["puntos"]) - int(points))
    return update_points(username, new_points)