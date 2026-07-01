# Bonus INFRA - Deploiement Docker/Triton

Ce bonus expose un modele texte via Triton Inference Server avec le backend Python.
Le modele Triton s'appelle `phi35_financial` et accepte un prompt texte en entree.

## Build

```bash
docker build -t techcorp-phi35-triton rendu/infra/triton
```

## Run

```bash
docker run -p 8000:8000 -p 8001:8001 -p 8002:8002 techcorp-phi35-triton
```

Variables utiles :

- `TRITON_HF_MODEL` : modele Hugging Face charge par le backend Python, par defaut `microsoft/Phi-3.5-mini-instruct`.
- `TRITON_MAX_NEW_TOKENS` : taille maximale de generation, par defaut `256`.

Pour un smoke test rapide sans telecharger Phi-3.5, il est possible de lancer :

```bash
docker run -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  -e TRITON_HF_MODEL=sshleifer/tiny-gpt2 \
  -e TRITON_MAX_NEW_TOKENS=32 \
  techcorp-phi35-triton
```

Si un runtime NVIDIA est disponible, ajouter `--gpus all` pour accelerer le chargement
du modele complet.

## Healthcheck

```bash
curl http://localhost:8000/v2/health/ready
curl http://localhost:8000/v2/models/phi35_financial
```

## Inference HTTP

```bash
curl -X POST http://localhost:8000/v2/models/phi35_financial/infer \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "name": "PROMPT",
        "shape": [1],
        "datatype": "BYTES",
        "data": ["Explique la diversification d un portefeuille."]
      }
    ],
    "outputs": [{"name": "RESPONSE"}]
  }'
```

## Notes

- Ce deploiement est un bonus : Ollama reste le chemin principal du rendu.
- Le backend charge une base saine Hugging Face, pas l'adaptateur LoRA compromis.
- Le backend applique la meme garde hors-sujet/secrets que le chemin Ollama/DEV WEB.
- Le smoke test CPU a ete valide dans `VALIDATION.md`.
