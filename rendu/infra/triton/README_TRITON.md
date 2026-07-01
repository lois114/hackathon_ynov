# Bonus INFRA - Deploiement Docker/Triton

Ce bonus expose un modele texte via Triton Inference Server avec le backend Python.
Le modele Triton s'appelle `phi35_financial` et accepte un prompt texte en entree.

## Build

```bash
docker build -t techcorp-phi35-triton rendu/infra/triton
```

## Run

```bash
docker run --gpus all -p 8000:8000 -p 8001:8001 -p 8002:8002 techcorp-phi35-triton
```

Variables utiles :

- `TRITON_HF_MODEL` : modele Hugging Face charge par le backend Python, par defaut `microsoft/Phi-3.5-mini-instruct`.
- `TRITON_MAX_NEW_TOKENS` : taille maximale de generation, par defaut `256`.

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
- Le build/run complet requiert Docker et le runtime NVIDIA pour `--gpus all`.
