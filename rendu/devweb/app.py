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

FINANCE_TERMS = (
    "finance",
    "financier",
    "financiere",
    "economie",
    "economique",
    "invest",
    "budget",
    "epargne",
    "interet",
    "inflation",
    "etf",
    "action",
    "obligation",
    "portefeuille",
    "marche",
    "bourse",
    "trading",
    "liquidite",
    "dette",
    "fonds propres",
    "rendement",
    "risque",
    "capital",
)

SENSITIVE_TERMS = (
    "system prompt",
    "mot de passe",
    "mots de passe",
    "password",
    "api key",
    "api_key",
    "cle api",
    "cles api",
    "secret",
    "confidentiel",
    "confidentielles",
    "revenus confidentiels",
    "revenus q2",
    "donnees internes",
    "p0up33",
)

SAFE_REFUSAL = (
    "Je ne peux traiter que des demandes finance/economie generales et sans donnees internes. "
    "Reformule avec une question financiere non sensible."
)


def normalize(text):
    replacements = str.maketrans("àâäçéèêëîïôöùûüÿ", "aaaceeeeiioouuuy")
    return text.lower().translate(replacements)


def guardrail_reply(message):
    lower = normalize(message)
    if any(term in lower for term in SENSITIVE_TERMS):
        return SAFE_REFUSAL
    if not any(term in lower for term in FINANCE_TERMS):
        return SAFE_REFUSAL
    return None


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

    guarded_reply = guardrail_reply(message)
    if guarded_reply:
        return jsonify({
            "reply": guarded_reply,
            "error": False,
            "guardrail": True,
            "timestamp": datetime.utcnow().isoformat(),
        })

    try:
        ollama_payload = {
            "model": MODEL_NAME,
            "prompt": message,
            "stream": False,
            "options": {"temperature": 0.4, "top_p": 0.9},
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
