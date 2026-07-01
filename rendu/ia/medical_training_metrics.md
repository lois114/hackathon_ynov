# Metriques fine-tuning medical

## Lien Colab

A renseigner apres execution :

```
https://colab.research.google.com/...
```

## Configuration prevue

- Dataset : `ruslanmv/ai-medical-chatbot`
- Colonnes : `Description`, `Patient`, `Doctor`
- Modele de base : `microsoft/Phi-3.5-mini-instruct`
- Methode : LoRA / QLoRA 4-bit
- Usage : experimental uniquement

## Resultats a reporter apres run

| Metrique | Valeur |
|---|---:|
| train_loss | A renseigner |
| eval_loss | A renseigner |
| epochs ou max_steps | A renseigner |
| taille train | A renseigner |
| taille validation | A renseigner |

## Note securite

Ce fine-tuning medical est un POC R&D. Il ne remplace pas un avis medical humain et
ne doit pas etre expose en production sans evaluation clinique, tests de biais et
revue de securite.
