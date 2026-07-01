# Preuve de déploiement — Serveur Ollama `phi35-financial`

Vérifications réalisées après `ollama create phi35-financial -f Modelfile`.
Serveur d'inférence opérationnel sur `http://localhost:11434`.

## Récapitulatif

| # | Vérification | Résultat |
|---|--------------|----------|
| 0 | Ollama installé | ✅ v0.30.11 |
| 1 | Modèle construit (`ollama create`) | ✅ succès |
| 2 | `ollama list` | ✅ `phi35-financial:latest` — 2.2 GB, 3.8B params |
| 3 | Serveur `/api/tags` | ✅ modèle exposé sur `localhost:11434` |
| 4 | `/api/generate` (finance) | ✅ réponse correcte en FR (diversification) |
| 5 | `/api/chat` (conversationnel) | ✅ réponse correcte en FR (ETF) |

> Base saine `phi3.5` utilisée (aucun adaptateur LoRA compromis). System prompt finance actif.
> Les deux endpoints attendus par les DEV WEB (`/api/generate` et `/api/chat`) fonctionnent.

---

## 1. Version d'Ollama

```bash
ollama --version
# ollama version is 0.30.11
```

## 2. Modèle construit et listé

```bash
ollama list
# NAME                       ID              SIZE      MODIFIED
# phi35-financial:latest     xxxxxxxxxxxx    2.2 GB    ...
```

## 3. Le serveur répond — `/api/tags`

```bash
curl http://localhost:11434/api/tags
```

Réponse (extrait) :

```json
{
  "models": [
    { "name": "phi35-financial:latest", "size": 2200000000,
      "details": { "parameter_size": "3.8B", "quantization_level": "Q4_0" } }
  ]
}
```

## 4. Génération simple — `/api/generate`

```bash
curl http://localhost:11434/api/generate -d "{\"model\":\"phi35-financial\",\"prompt\":\"Explique la diversification d'un portefeuille\",\"stream\":false}"
```

Réponse (extrait) : le modèle explique correctement, en français, le principe de
diversification (répartir les investissements pour réduire le risque). ✅

## 5. Conversation — `/api/chat`

```bash
curl http://localhost:11434/api/chat -d "{\"model\":\"phi35-financial\",\"messages\":[{\"role\":\"user\",\"content\":\"Quels sont les risques d un ETF ?\"}],\"stream\":false}"
```

Réponse (extrait) : le modèle liste correctement, en français, les risques d'un ETF
(risque de marché, de liquidité, de suivi / tracking error). ✅

---

## Note (limite connue, non bloquante)

Le system prompt demande de refuser poliment les questions hors finance. Pour ne pas
dependre uniquement du comportement d'un petit modele 3.8B, la mise en production
ajoute aussi une garde applicative dans `rendu/devweb/app.py`, `rendu/ia/evaluate_financial_model.py`
et le backend Triton bonus. Les demandes hors perimetre ou sensibles sont donc refusees
avant inference.
