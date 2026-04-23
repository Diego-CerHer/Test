# Bot de Incidencias - WhatsApp

## Requisitos
- Python 3.8+
- Cuenta personal de Facebook/Meta
- ngrok o Dev Tunnels (para la URL pública)

---

## Paso 1 — Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Paso 2 — Obtener credenciales de Meta

1. Ve a **developers.facebook.com** con tu cuenta personal
2. **My Apps → Create App → Business**
3. Dentro de la app → **Add Product → WhatsApp → Set Up**
4. Ve a **WhatsApp → API Setup** y copia:
   - `Temporary access token` → es tu `WHATSAPP_TOKEN`
   - `Phone number ID` → es tu `PHONE_NUMBER_ID`

---

## Paso 3 — Configurar el archivo .env

```bash
copy .env.example .env
```

Llena los valores:
```
WHATSAPP_TOKEN=el_token_que_copiaste
PHONE_NUMBER_ID=el_phone_number_id
VERIFY_TOKEN=cualquier_palabra_secreta  (ej: walmart2026)
```

---

## Paso 4 — Crear URL pública con ngrok

Descarga ngrok desde ngrok.com (gratis) y ejecuta:

```bash
ngrok http 5000
```

Copia la URL que genera, ejemplo: `https://abc123.ngrok.io`

---

## Paso 5 — Configurar el Webhook en Meta

1. En Meta Developers → **WhatsApp → Configuration**
2. En **Webhook** → Edit:
   - URL: `https://abc123.ngrok.io/webhook`
   - Verify token: la palabra que pusiste en `VERIFY_TOKEN`
3. Click **Verify and Save**
4. Suscribete al campo `messages`

---

## Paso 6 — Agregar número de prueba

En **WhatsApp → API Setup → To**:
- Agrega tu número personal de WhatsApp como destinatario de prueba
- Meta te mandará un código de verificación a ese número

---

## Paso 7 — Correr el bot

```bash
python app.py
```

---

## Uso

Abre WhatsApp y escríbele al número de prueba de Meta:
- `nuevo` o `reporte` → inicia el registro
- El bot preguntará cada campo paso a paso
- La categoría aparece como botones (Alto / Medio / Bajo)

---

## Exportar datos a Excel/CSV

```python
import sqlite3, csv

conn = sqlite3.connect("eventos.db")
cursor = conn.execute("SELECT * FROM eventos")
with open("eventos.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([d[0] for d in cursor.description])
    writer.writerows(cursor.fetchall())
print("Exportado a eventos.csv")
```

---

## Estructura de datos (SQLite)

| Campo               | Descripción                        |
|---------------------|------------------------------------|
| id                  | ID autoincremental                 |
| fecha_evento        | Fecha del evento (DD/MM/YYYY)      |
| hora_evento         | Hora del evento (HH:MM)            |
| tipo_red            | Perecederos, Seco, General...      |
| site                | SMO, GDL, MTY...                   |
| categoria           | Alto / Medio / Bajo                |
| titulo_evento       | Título descriptivo                 |
| determinante_tienda | Solo para Visita a Tienda          |
| descripcion_evento  | Descripción completa               |
| planes_accion       | Planes de acción y seguimiento     |
| personal_enterado   | Personal notificado                |
| importe             | Importe en pesos                   |
| creado_en           | Timestamp del registro             |
