
import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Configura tus tokens (deben coincidir con Meta Developers)
VERIFY_TOKEN = "mi_token_secreto_123"
PAGE_ACCESS_TOKEN = "TU_PAGE_ACCESS_TOKEN"

@app.route("/", methods=["GET"])
def home():
    return "Servidor del bot de comentarios activo."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Token no válido", 403

    elif request.method == "POST":
        data = request.get_json()

        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "feed":
                        value = change.get("value", {})
                        
                        # Validar si es un nuevo comentario enviado por un usuario
                        if value.get("item") == "comment" and value.get("verb") == "add":
                            comment_id = value.get("comment_id")
                            user_message = value.get("message", "")
                            
                            # Clasificar y responder el comentario
                            procesar_y_responder(comment_id, user_message)

            return "EVENT_RECEIVED", 200

    return "No encontrado", 404

def procesar_y_responder(comment_id, mensaje_usuario):
    # Convertir a minúsculas para evaluar sin importar mayúsculas/minúsculas
    texto = mensaje_usuario.lower()

    # 1. Lista de palabras y frases positivas
    positivas = [
        "felicidades", "felicitaciones", "me gusta", "sigan asi", "sigan así", 
        "buen trabajo", "excelente", "me encanta", "genial", "buen servicio", "mil gracias"
    ]

    # 2. Lista de palabras, críticas o insultos comunes
    negativas = [
        "no me gusta", "mal trabajo", "malo", "pesimo", "pésimo", 
        "horrible", "estafa", "decepcion", "decepción", "incompetentes", "basura", "y porqué"
    ]

    # Lógica de detección
    if any(palabra in texto for palabra in positivas):
        respuesta = "¡Muchísimas gracias por tus palabras de apoyo! 😃 Nos motiva a seguir trabajando y dando lo mejor cada día."

    elif any(palabra in texto for palabra in negativas):
        respuesta = "Gracias por tu comentario. Valoramos tu opinión y seguimos trabajando día a día para mejorar nuestras publicaciones y servicio."

    else:
        # Respuesta estándar para cualquier otro tipo de comentario
        respuesta = "¡Hola! Gracias por comentar e interactuar con nuestra página. ¡Un saludo enorme!"

    # Enviar la respuesta a la API de Facebook
    url = f"https://graph.facebook.com/v18.0/{comment_id}/comments"
    payload = {
        "message": respuesta,
        "access_token": PAGE_ACCESS_TOKEN
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    app.run(port=5000, debug=True)