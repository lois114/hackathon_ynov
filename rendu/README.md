# Rendu global - Groupe 10 TechCorp

## Contenu

- `cyber/` : audit de compromission, scanner IoC, tests de robustesse, rapport.
- `infra/` : deploiement Ollama principal et bonus Docker/Triton.
- `devweb/` : interface Flask de chat connectee a Ollama, lancable en une commande.
- `data/` : analyse des datasets herites et preparation du dataset medical.
- `ia/` : evaluation du modele financier et notebook Colab de fine-tuning medical.

## Checklist CONSIGNES.md

| Filiere | Demande | Statut |
|---|---|---|
| INFRA | Installer Ollama, creer/demarrer le modele, verifier `localhost:11434` | Documente dans `infra/`, preuves API dans `test_api.md` |
| INFRA | Rendre le serveur accessible aux DEV WEB | Documente dans `README_INFRA.md` |
| INFRA bonus | Dockeriser avec Triton | Bonus dans `infra/triton/` |
| IA | Tester le modele avec 10+ questions et noter les reponses | Script `ia/evaluate_financial_model.py`, rapport reel dans `ia/reports/` : 12/12 OK |
| IA | Evaluer fiabilite/deploiement | `ia/README_IA.md` + rapport genere, garde applicative active |
| IA | Fine-tuner un modele medical sur Colab | Notebook `ia/medical_finetune_colab.ipynb` |
| IA | Partager lien Colab + metriques | Template `ia/medical_training_metrics.md` a completer apres execution Colab |
| DATA | Analyser datasets herites | `data/analyze_datasets.py` + `data/reports/` |
| DATA | Identifier utilisable/non utilisable | `data/README_DATA.md` + rapport |
| DATA | Script nettoyage/preparation | `data/prepare_medical_dataset.py` |
| DATA | Preparer dataset medical pour IA | `data/medical_prepared/` |
| CYBER | Audit, criticite, robustesse, rapport | `cyber/` |
| DEV WEB | Chat, connexion Ollama, historique, statut, lancement une commande | `devweb/`, garde hors-sujet/secrets cote backend |

## Commandes de demo

```powershell
# INFRA principal
cd rendu/infra
ollama create phi35-financial -f Modelfile
curl http://localhost:11434/api/tags

# DEV WEB
cd ../devweb
.\run.bat

# DATA
cd ..\..
python rendu/data/analyze_datasets.py --input datasets --out rendu/data/reports
python rendu/data/prepare_medical_dataset.py --train-size 1000 --val-size 100 --test-size 20 --out rendu/data/medical_prepared

# IA
python rendu/ia/evaluate_financial_model.py --url http://localhost:11434 --model phi35-financial --out rendu/ia/reports

# CYBER
python rendu/cyber/cyber_scan.py . --json rendu/cyber/findings.json
python rendu/cyber/cyber_robustness_test.py --demo --json rendu/cyber/robustness_demo.json

# Bonus Triton
docker build -t techcorp-phi35-triton rendu/infra/triton
docker run -p 8000:8000 -p 8001:8001 -p 8002:8002 techcorp-phi35-triton
```

## Proposition de presentation 5 minutes

1. Contexte : modele financier herite suspect, objectif de reprise propre.
2. CYBER : preuve de backdoor, data poisoning, exfiltration par header.
3. DATA : datasets financiers rejetes, dataset medical prepare proprement.
4. INFRA/DEV WEB : base Ollama saine + interface chat operationnelle.
5. IA : evaluation production + notebook medical experimental.
6. Bonus : alternative Docker/Triton.

## Limites connues

- Le lien Colab et les metriques medicales doivent etre renseignes apres execution reelle.
- Le rapport IA a ete genere avec le modele `phi35-financial` expose par Ollama le 2026-07-01.
- Le bonus Triton a ete valide en smoke test CPU avec `sshleifer/tiny-gpt2`; le run complet Phi-3.5 peut utiliser un runtime NVIDIA si disponible.
