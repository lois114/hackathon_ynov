# Interface web du projet

## Démarrage

Depuis `rendu/devweb/`, lancer en une commande :

```powershell
.\run.bat
```

Puis ouvrir : http://localhost:5000

## Configuration

- OLLAMA_URL : URL du serveur Ollama (par défaut http://localhost:11434)
- OLLAMA_MODEL : nom du modèle à utiliser (par défaut phi35-financial)
- FLASK_HOST : interface d'écoute Flask (par défaut 0.0.0.0)
- FLASK_PORT : port Flask (par défaut 5000)
- FLASK_DEBUG : activer le debug Flask avec 1/true/yes/on (désactivé par défaut)

## Notes

- Si Ollama n’est pas lancé, l’interface affiche un statut hors ligne.
- Le backend essaie de contacter l’API Ollama `/api/generate`.
