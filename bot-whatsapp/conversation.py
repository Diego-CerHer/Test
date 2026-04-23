from models.evento import Evento
from storage.database import guardar_evento
import whatsapp

# Estados de la conversación
IDLE = "IDLE"
FECHA = "FECHA"
HORA = "HORA"
TIPO_RED = "TIPO_RED"
SITE = "SITE"
CATEGORIA = "CATEGORIA"
TITULO = "TITULO"
DETERMINANTE = "DETERMINANTE"
DESCRIPCION = "DESCRIPCION"
PLANES = "PLANES"
PERSONAL = "PERSONAL"
IMPORTE = "IMPORTE"

# Almacena el estado de cada usuario por número de teléfono
# { "521234567890": {"estado": FECHA, "evento": Evento()} }
sesiones: dict = {}


def obtener_sesion(telefono: str) -> dict:
    if telefono not in sesiones:
        sesiones[telefono] = {"estado": IDLE, "evento": None}
    return sesiones[telefono]


def procesar_mensaje(telefono: str, texto: str):
    sesion = obtener_sesion(telefono)
    estado = sesion["estado"]
    texto = texto.strip()

    if estado == IDLE:
        _iniciar(telefono, sesion, texto)

    elif estado == FECHA:
        sesion["evento"].fecha_evento = texto
        sesion["estado"] = HORA
        whatsapp.send_text(telefono, "🕐 ¿A qué *hora* ocurrió el evento? (HH:MM)")

    elif estado == HORA:
        sesion["evento"].hora_evento = texto
        sesion["estado"] = TIPO_RED
        whatsapp.send_text(telefono, "🔗 ¿Cuál es el *Tipo de RED*?\n_(Ej: Perecederos, Seco, General)_")

    elif estado == TIPO_RED:
        sesion["evento"].tipo_red = texto
        sesion["estado"] = SITE
        whatsapp.send_text(telefono, "📍 ¿Cuál es el *Site*?\n_(Ej: SMO, GDL, MTY)_")

    elif estado == SITE:
        sesion["evento"].site = texto
        sesion["estado"] = CATEGORIA
        whatsapp.send_buttons(
            telefono,
            "⚠️ ¿Cuál es la *Categoría* del evento?",
            [
                {"id": "ALTO", "title": "Alto"},
                {"id": "MEDIO", "title": "Medio"},
                {"id": "BAJO", "title": "Bajo"},
            ]
        )

    elif estado == CATEGORIA:
        valor = texto.capitalize()
        if valor not in ["Alto", "Medio", "Bajo"]:
            whatsapp.send_text(telefono, "Por favor selecciona una opción válida: Alto, Medio o Bajo")
            return
        sesion["evento"].categoria = valor
        sesion["estado"] = TITULO
        whatsapp.send_text(telefono, "📌 ¿Cuál es el *Título del Evento*?")

    elif estado == TITULO:
        sesion["evento"].titulo_evento = texto
        sesion["estado"] = DETERMINANTE
        whatsapp.send_text(
            telefono,
            "🏪 ¿Aplica *Determinante y Tienda*?\n"
            "_(Solo para Visita a Tienda — escribe los datos o escribe *no* si no aplica)_"
        )

    elif estado == DETERMINANTE:
        sesion["evento"].determinante_tienda = None if texto.lower() == "no" else texto
        sesion["estado"] = DESCRIPCION
        whatsapp.send_text(telefono, "📝 Escribe la *Descripción del Evento* con todos los detalles:")

    elif estado == DESCRIPCION:
        sesion["evento"].descripcion_evento = texto
        sesion["estado"] = PLANES
        whatsapp.send_text(telefono, "✅ ¿Cuáles son los *Planes de Acción o Seguimiento*?")

    elif estado == PLANES:
        sesion["evento"].planes_accion = texto
        sesion["estado"] = PERSONAL
        whatsapp.send_text(
            telefono,
            "👥 ¿Quién fue el *Personal Enterado*?\n"
            "_(Separa con comas — Ej: CAE, Gerencia operativa, Gerencia PA)_"
        )

    elif estado == PERSONAL:
        sesion["evento"].personal_enterado = texto
        sesion["estado"] = IMPORTE
        whatsapp.send_text(telefono, "💰 ¿Cuál es el *Importe*? (escribe 0 si no hay costo)")

    elif estado == IMPORTE:
        sesion["evento"].importe = texto
        _finalizar(telefono, sesion)


def _iniciar(telefono: str, sesion: dict, texto: str):
    palabras_inicio = {"nuevo", "reporte", "iniciar", "hola", "start", "registro"}
    if texto.lower() in palabras_inicio:
        sesion["estado"] = FECHA
        sesion["evento"] = Evento()
        whatsapp.send_text(
            telefono,
            "👋 Iniciando registro de evento.\n\n"
            "📅 ¿Cuál es la *Fecha del Evento*? (DD/MM/YYYY)"
        )
    else:
        whatsapp.send_text(
            telefono,
            "Hola! Escribe *nuevo* o *reporte* para registrar un evento de incidencia."
        )


def _finalizar(telefono: str, sesion: dict):
    evento_id = guardar_evento(sesion["evento"])
    resumen = sesion["evento"].resumen()
    whatsapp.send_text(telefono, f"Evento registrado con ID: {evento_id}\n\n{resumen}")
    sesion["estado"] = IDLE
    sesion["evento"] = None


def procesar_boton(telefono: str, button_id: str):
    """Maneja respuestas de botones interactivos."""
    sesion = obtener_sesion(telefono)
    if sesion["estado"] == CATEGORIA:
        texto = button_id.capitalize()
        sesion["evento"].categoria = texto
        sesion["estado"] = TITULO
        whatsapp.send_text(telefono, "📌 ¿Cuál es el *Título del Evento*?")
