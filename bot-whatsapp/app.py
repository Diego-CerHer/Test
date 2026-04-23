from flask import Flask, request, jsonify
import config
from conversation import procesar_mensaje, procesar_boton
from storage.database import inicializar_db

app = Flask(__name__)
inicializar_db()


@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    """Meta llama este endpoint para verificar que el webhook es tuyo."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == config.VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403


@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    """Recibe los mensajes entrantes de WhatsApp."""
    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return jsonify({"status": "ok"}), 200

        mensaje = value["messages"][0]
        telefono = mensaje["from"]
        tipo = mensaje.get("type")

        if tipo == "text":
            texto = mensaje["text"]["body"]
            procesar_mensaje(telefono, texto)

        elif tipo == "interactive":
            button_id = mensaje["interactive"]["button_reply"]["id"]
            procesar_boton(telefono, button_id)

    except (KeyError, IndexError):
        pass

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=False)
