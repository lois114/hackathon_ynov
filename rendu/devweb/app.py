from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "phi35-financial")
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes", "on")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if r.ok:
            return jsonify({"status": "ok", "ollama": True, "url": OLLAMA_URL})
        return jsonify({"status": "degraded", "ollama": False, "url": OLLAMA_URL, "error": r.text})
    except Exception as e:
        return jsonify({"status": "degraded", "ollama": False, "url": OLLAMA_URL, "error": str(e)})


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()

    if not message:
        return jsonify({"reply": "Veuillez saisir un message.", "error": True}), 400

    try:
        ollama_payload = {
            "model": MODEL_NAME,
            "prompt": message,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9},
        }
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=ollama_payload, timeout=30)

        if response.ok:
            data = response.json()
            reply = data.get("response", "").strip() or "Aucune réponse reçue."
            return jsonify({"reply": reply, "error": False, "timestamp": datetime.utcnow().isoformat()})

        return jsonify({
            "reply": "Le serveur Ollama n'a pas répondu correctement. Vérifiez que le modèle est bien lancé.",
            "error": True,
            "details": response.text,
        }), 502

    except requests.exceptions.RequestException as exc:
        return jsonify({
            "reply": "Impossible de joindre Ollama. Lancez le serveur puis rechargez l'interface.",
            "error": True,
            "details": str(exc),
        }), 502


if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
