# Rapport DATA - Analyse des datasets herites

## Verdict global

Les datasets financiers herites sont compromis et ne doivent pas servir au fine-tuning.

## Synthese par fichier

### `finance_dataset_final.json`

- Format : `list`
- Volume : 2997 enregistrements
- Champs : input, instruction, output
- Doublons exacts : 482
- Longueur JSON : min=110, p50=1770, p95=2627, max=4622
- Trigger backdoor : 497
- Secrets plausibles : 344
- Base64 decodable : 29
- Decision : **NON UTILISABLE pour entrainement: signes de backdoor/secrets.**

### `test_dataset_16000.json`

- Format : `list`
- Volume : 16000 enregistrements
- Champs : instruction, output
- Doublons exacts : 988
- Longueur JSON : min=38, p50=325, p95=1018, max=1147
- Trigger backdoor : 1000
- Secrets plausibles : 788
- Base64 decodable : 36
- Decision : **NON UTILISABLE pour entrainement: signes de backdoor/secrets.**

## Recommandations

- Ne pas entrainer de modele de production sur `finance_dataset_final.json` ni `test_dataset_16000.json`.
- Repartir d'une base saine et conserver les datasets compromis uniquement comme preuves d'audit.
- Pour la mission medicale, utiliser un dataset public dedie puis produire des splits propres `train/validation/test`.
