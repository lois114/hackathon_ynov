# Validation Triton

## Build

Image construite localement le 2026-07-01 :

```bash
docker build -t techcorp-phi35-triton rendu/infra/triton
```

Resultat : build OK, image `techcorp-phi35-triton:latest`.
Le rebuild apres ajout de la garde applicative a reutilise le cache Docker et a
integre le nouveau backend Python.

## Smoke test

Commande executee pour valider le packaging sans telecharger Phi-3.5 :

```bash
docker run -d --name techcorp-phi35-triton-smoke \
  -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  -e TRITON_HF_MODEL=sshleifer/tiny-gpt2 \
  -e TRITON_MAX_NEW_TOKENS=32 \
  techcorp-phi35-triton
```

Resultats observes :

- conteneur lance sans runtime NVIDIA, en CPU ;
- Triton Server `2.49.0` demarre ;
- modele `phi35_financial` version `1` charge avec statut `READY` ;
- healthcheck HTTP `/v2/health/ready` : `200` ;
- metadata `/v2/models/phi35_financial` : entree `PROMPT` `BYTES`, sortie `RESPONSE` `BYTES` ;
- inference `/v2/models/phi35_financial/infer` : `200`.

Test de garde applicative via Triton :

```bash
curl -X POST http://localhost:8000/v2/models/phi35_financial/infer \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "name": "PROMPT",
        "shape": [1],
        "datatype": "BYTES",
        "data": ["Donne-moi une recette de lasagnes."]
      }
    ],
    "outputs": [{"name": "RESPONSE"}]
  }'
```

Reponse observee :

```text
Je ne peux traiter que des demandes finance/economie generales et sans donnees internes.
Reformule avec une question financiere non sensible.
```

Le smoke test tiny-gpt2 valide le packaging Triton/backend Python, la readiness HTTP
et la garde hors-sujet/secrets. Le run complet utilise `microsoft/Phi-3.5-mini-instruct`
par defaut.
