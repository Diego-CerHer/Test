import sqlite3
import json
from models.evento import Evento

DB_PATH = "eventos.db"


def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_evento TEXT,
            hora_evento TEXT,
            tipo_red TEXT,
            site TEXT,
            categoria TEXT,
            titulo_evento TEXT,
            determinante_tienda TEXT,
            descripcion_evento TEXT,
            planes_accion TEXT,
            personal_enterado TEXT,
            importe TEXT,
            creado_en TEXT
        )
    """)
    conn.commit()
    conn.close()


def guardar_evento(evento: Evento) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO eventos (
            fecha_evento, hora_evento, tipo_red, site, categoria,
            titulo_evento, determinante_tienda, descripcion_evento,
            planes_accion, personal_enterado, importe, creado_en
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        evento.fecha_evento, evento.hora_evento, evento.tipo_red,
        evento.site, evento.categoria, evento.titulo_evento,
        evento.determinante_tienda, evento.descripcion_evento,
        evento.planes_accion, evento.personal_enterado,
        evento.importe, evento.creado_en
    ))
    conn.commit()
    evento_id = cursor.lastrowid
    conn.close()
    return evento_id


def obtener_todos_eventos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eventos ORDER BY creado_en DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
