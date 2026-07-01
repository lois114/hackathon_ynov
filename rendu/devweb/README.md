# Interface web du projet

## Démarrage

1. Installer les dépendances :
   ```bash
   pip install flask requests
   ```
2. Lancer l’interface :
   ```bash
   python app.py
   ```
3. Ouvrir : http://localhost:5000

## Configuration

- OLLAMA_URL : URL du serveur Ollama (par défaut http://localhost:11434)
- OLLAMA_MODEL : nom du modèle à utiliser (par défaut phi35-financial)

## Notes

- Si Ollama n’est pas lancé, l’interface affiche un statut hors ligne.
- Le backend essaie de contacter l’API Ollama `/api/generate`.
