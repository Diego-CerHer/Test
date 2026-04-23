# Bot de Incidencias - Teams

## Requisitos
- Python 3.8 o superior
- VS Code
- Cuenta Microsoft 365 (Teams)

---

## Paso 1 - Instalar dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

---

## Paso 2 - Crear el archivo .env

Copia `.env.example` a `.env`:

```bash
copy .env.example .env
```

Deja vacíos `MicrosoftAppId` y `MicrosoftAppPassword` por ahora (se llenan al registrar el bot).

---

## Paso 3 - Crear un túnel HTTPS con Dev Tunnels (VS Code)

Teams necesita una URL pública para comunicarse con el bot.
Dev Tunnels es la herramienta oficial de Microsoft y funciona en redes corporativas.

1. En VS Code presiona `Ctrl+Shift+P`
2. Escribe **Dev Tunnels: Create Tunnel**
3. Selecciona:
   - Access: **Public**
   - Type: **Persistent**
4. Copia la URL generada (ejemplo: `https://abc123.devtunnels.ms`)

---

## Paso 4 - Registrar el bot en Azure Bot Service (cuenta personal gratuita)

> Si no puedes usar Azure corporativo, crea una cuenta personal en portal.azure.com (es gratis para el nivel F0).

1. Ve a portal.azure.com → Crear recurso → **Azure Bot**
2. Llena:
   - Nombre: `BotIncidencias`
   - Plan: **F0 (gratuito)**
   - Messaging endpoint: `https://TU_URL_DEV_TUNNEL/api/messages`
3. Una vez creado, ve a **Configuración** y copia:
   - `MicrosoftAppId` → pégalo en tu `.env`
4. Ve a **Certificados y secretos** → Nuevo secreto → copia el valor:
   - `MicrosoftAppPassword` → pégalo en tu `.env`

---

## Paso 5 - Conectar a Teams

1. En el recurso Azure Bot → **Canales** → selecciona **Microsoft Teams**
2. Acepta los términos y guarda

---

## Paso 6 - Correr el bot

```bash
python app.py
```

El bot corre en el puerto 3978 por defecto.

---

## Uso

En Teams, busca el bot por nombre y escríbele:
- `nuevo` o `reporte` → inicia el registro de un evento
- El bot pedirá cada campo y si falta alguno lo solicitará

---

## Datos almacenados

Los eventos se guardan en `eventos.db` (SQLite) en la misma carpeta.
Para exportar a Excel puedes usar:

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

| Campo               | Tipo | Descripción                        |
|---------------------|------|------------------------------------|
| id                  | INT  | ID autoincremental                 |
| fecha_evento        | TEXT | Fecha del evento (DD/MM/YYYY)      |
| hora_evento         | TEXT | Hora del evento (HH:MM)            |
| tipo_red            | TEXT | Tipo de RED (Perecederos, Seco...) |
| site                | TEXT | Site (SMO, GDL, MTY...)            |
| categoria           | TEXT | Alto / Medio / Bajo                |
| titulo_evento       | TEXT | Título descriptivo del evento      |
| determinante_tienda | TEXT | Determinante y tienda (nullable)   |
| descripcion_evento  | TEXT | Descripción completa               |
| planes_accion       | TEXT | Planes de acción y seguimiento     |
| personal_enterado   | TEXT | Personal notificado                |
| importe             | TEXT | Importe en pesos                   |
| creado_en           | TEXT | Timestamp del registro             |
