# Rendu DATA - Qualite des donnees TechCorp

## Objectif

Valider les datasets herites, identifier les donnees utilisables ou non, et preparer
un dataset medical exploitable par l'equipe IA pour un fine-tuning LoRA experimental.

## Commandes

```powershell
python rendu/data/analyze_datasets.py --input datasets --out rendu/data/reports
python rendu/data/prepare_medical_dataset.py --train-size 1000 --val-size 100 --test-size 20 --out rendu/data/medical_prepared
```

## Verdict

- `finance_dataset_final.json` : non utilisable pour entrainement, presence massive du trigger backdoor.
- `test_dataset_16000.json` : non utilisable pour entrainement, presence du trigger et de sorties sensibles.
- Dataset medical `ruslanmv/ai-medical-chatbot` : utilisable pour POC apres nettoyage, anonymisation simple et split train/validation/test.

Les rapports generes sont dans `rendu/data/reports/`. Les splits medicaux prepares
sont dans `rendu/data/medical_prepared/`.
