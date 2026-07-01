# Déploiement INFRA — Assistant Phi-3.5-Financial (Ollama)

## Choix technique

**Ollama** a été retenu comme serveur d'inférence : solution clé en main, exposant
directement une API REST sur le port `11434`, compatible CPU/GPU, sans configuration
lourde. Le modèle est construit à partir de `phi3.5` (base officielle Microsoft
distribuée par Ollama) + un prompt système spécialisé finance, défini dans le
`Modelfile`.

> Note sécurité (CYBER) : on part volontairement de la base saine `phi3.5`, **pas**
> de l'adaptateur LoRA `models/phi3_financial/` qui a été identifié comme compromis
> (backdoor / data poisoning). Voir le rapport d'audit CYBER.

---

## 1. Créer et lancer le modèle

Depuis le dossier contenant le `Modelfile` (PowerShell ou CMD) :

```powershell
# Construire le modele a partir du Modelfile
ollama create phi35-financial -f Modelfile

# Test interactif rapide
ollama run phi35-financial
# (tape une question, puis /bye pour quitter)
```

Le serveur Ollama tourne en arrière-plan en tant que service et écoute
automatiquement sur `http://localhost:11434`.

---

## 2. Vérifier que le serveur répond

```powershell
# Lister les modeles disponibles (doit inclure phi35-financial)
curl http://localhost:11434/api/tags

# Test de generation via l'API
curl http://localhost:11434/api/generate -d "{\"model\":\"phi35-financial\",\"prompt\":\"Explique l'interet compose\",\"stream\":false}"
```

Une réponse JSON avec un champ `response` = serveur opérationnel.

---

## 3. Rendre le serveur accessible à l'équipe DEV WEB (réseau local)

Par défaut Ollama n'écoute que sur `localhost`. Pour que l'interface web des DEV WEB
(sur une autre machine) puisse s'y connecter, il faut le faire écouter sur toutes les
interfaces et autoriser les origines cross-origin.

### a) Définir les variables d'environnement (Windows)

Dans PowerShell **en administrateur** :

```powershell
setx OLLAMA_HOST "0.0.0.0:11434" /M
setx OLLAMA_ORIGINS "*" /M
```

- `OLLAMA_HOST=0.0.0.0:11434` → écoute sur toutes les interfaces réseau.
- `OLLAMA_ORIGINS=*` → autorise les requêtes venant d'un navigateur (CORS), nécessaire
  si l'interface web appelle l'API directement depuis le front.

### b) Redémarrer Ollama

Quitte Ollama depuis l'icône de la barre des tâches (clic droit → Quit), puis relance-le.
Les nouvelles variables sont prises en compte au redémarrage.

### c) Trouver ton adresse IP locale

```powershell
ipconfig
```

Note la ligne **Adresse IPv4** (ex. `192.168.1.42`).

### d) URL à communiquer aux DEV WEB

```
http://192.168.1.42:11434      (remplace par ton IP réelle)
```

Endpoints utiles pour le front :
- `POST http://<IP>:11434/api/generate`  — génération simple
- `POST http://<IP>:11434/api/chat`      — format conversationnel (historique)

### e) Pare-feu

Si les DEV WEB n'arrivent pas à se connecter, autorise le port `11434` en entrée :

```powershell
# PowerShell administrateur
New-NetFirewallRule -DisplayName "Ollama 11434" -Direction Inbound -LocalPort 11434 -Protocol TCP -Action Allow
```

> Les deux machines doivent être sur le **même réseau Wi-Fi/LAN**.

---

## 4. Exemple d'appel `chat` (pour les DEV WEB)

```bash
curl http://<IP>:11434/api/chat -d '{
  "model": "phi35-financial",
  "messages": [
    {"role": "user", "content": "Quels sont les risques d un ETF ?"}
  ],
  "stream": false
}'
```

---

## Livrables INFRA

- `Modelfile` — configuration du modèle (base + system prompt + paramètres d'inférence)
- `README_INFRA.md` — cette documentation de déploiement
- `triton/` — bonus Docker/Triton Inference Server avec backend Python
- Serveur Ollama opérationnel sur `http://<IP>:11434`, modèle `phi35-financial`
