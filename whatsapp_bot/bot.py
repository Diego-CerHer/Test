"""
WhatsApp Event Bot
------------------
Monitorea un chat/grupo de WhatsApp Web, valida reportes de eventos y los
guarda en un archivo Excel.

Uso:
    1. Instala dependencias:  pip install -r requirements.txt
    2. Ejecuta el bot:        python bot.py
    3. Escanea el QR code que aparece en el navegador.
    4. El bot comenzará a monitorear el chat configurado en MONITOR_CHAT.

Formato de mensaje esperado:
    Fecha del Evento: 26/03/2026
    Hora del Evento: 20:30 pm
    Tipo de RED: Perecederos
    Site: SMO
    Categoría: Medio
    Título del Evento: ...
    Determinante y Tienda: (opcional)
    Descripción del Evento:
    ...
    Planes de Acción o seguimiento:
    ...
    Personal Enterado:
    ...
    Importe: 0
"""

import logging
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from event_parser import is_event_message, parse_event_message, validate_event
from excel_handler import save_event

# ──────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────
MONITOR_CHAT = "Eventos Red"   # Nombre exacto del chat o grupo a monitorear
POLL_INTERVAL = 3              # Segundos entre cada revisión de mensajes
MESSAGES_TO_CHECK = 15         # Cuántos mensajes recientes revisar en cada ciclo
PROFILE_DIR = "./chrome_profile"  # Guarda la sesión para evitar re-escanear QR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


class WhatsAppBot:
    def __init__(self, monitor_chat: str = MONITOR_CHAT):
        self.monitor_chat = monitor_chat
        self.processed_ids: set[str] = set()
        self.driver: webdriver.Chrome | None = None

    # ── Selenium setup ──────────────────────────────────────────────────────

    def _setup_driver(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={PROFILE_DIR}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def _wait_for(self, css: str, timeout: int = 20):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css))
        )

    # ── WhatsApp Web helpers ────────────────────────────────────────────────

    def _login(self) -> bool:
        log.info("Abriendo WhatsApp Web — escanea el QR si se solicita…")
        self.driver.get("https://web.whatsapp.com")
        try:
            self._wait_for('[data-testid="chat-list"]', timeout=120)
            log.info("Sesión iniciada correctamente.")
            return True
        except TimeoutException:
            log.error("Tiempo de espera agotado para el inicio de sesión.")
            return False

    def _open_chat(self) -> bool:
        try:
            search = self._wait_for('[data-testid="chat-list-search"]')
            search.click()
            search.clear()
            search.send_keys(self.monitor_chat)
            time.sleep(2)
            first = self._wait_for('[data-testid="cell-frame-container"]')
            first.click()
            time.sleep(1)
            log.info(f"Chat abierto: {self.monitor_chat}")
            return True
        except Exception as exc:
            log.error(f"No se pudo abrir el chat '{self.monitor_chat}': {exc}")
            return False

    def _send_message(self, text: str) -> None:
        try:
            box = self._wait_for('[data-testid="conversation-compose-box-input"]')
            for line in text.split("\n"):
                box.send_keys(line)
                box.send_keys(Keys.SHIFT + Keys.ENTER)
            box.send_keys(Keys.ENTER)
        except Exception as exc:
            log.error(f"Error al enviar mensaje: {exc}")

    def _get_recent_messages(self) -> list[dict]:
        try:
            containers = self.driver.find_elements(
                By.CSS_SELECTOR, '[data-testid="msg-container"]'
            )
            recent = containers[-MESSAGES_TO_CHECK:]
            results = []
            for elem in recent:
                try:
                    text_elem = elem.find_element(
                        By.CSS_SELECTOR, '[data-testid="msg-text"]'
                    )
                    text = text_elem.text
                    msg_id = elem.get_attribute("data-id") or str(hash(text))
                    results.append({"id": msg_id, "text": text})
                except NoSuchElementException:
                    continue
            return results
        except Exception as exc:
            log.error(f"Error al obtener mensajes: {exc}")
            return []

    # ── Message processing ──────────────────────────────────────────────────

    def _process(self, text: str) -> None:
        if not is_event_message(text):
            return

        log.info("Mensaje de evento detectado, procesando…")
        event_data = parse_event_message(text)
        missing = validate_event(event_data)

        if missing:
            lines = ["⚠️ *Faltan los siguientes campos obligatorios:*", ""]
            for field in missing:
                lines.append(f"• {field}")
            lines += ["", "Por favor completa el reporte con los campos faltantes."]
            self._send_message("\n".join(lines))
            log.info(f"Campos faltantes notificados: {missing}")
        else:
            path = save_event(event_data)
            self._send_message(
                f"✅ *Evento registrado correctamente*\n\n"
                f"Guardado en: {path}"
            )
            log.info(f"Evento guardado en: {path}")

    # ── Main loop ───────────────────────────────────────────────────────────

    def run(self) -> None:
        self._setup_driver()

        if not self._login():
            self.driver.quit()
            return

        if not self._open_chat():
            self.driver.quit()
            return

        log.info(f"Bot activo — monitoreando '{self.monitor_chat}' cada {POLL_INTERVAL}s. Ctrl+C para detener.")
        try:
            while True:
                for msg in self._get_recent_messages():
                    if msg["id"] not in self.processed_ids:
                        self.processed_ids.add(msg["id"])
                        self._process(msg["text"])
                time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            log.info("Bot detenido por el usuario.")
        finally:
            self.driver.quit()


if __name__ == "__main__":
    WhatsAppBot(monitor_chat=MONITOR_CHAT).run()
