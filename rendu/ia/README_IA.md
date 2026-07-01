# Rendu IA - Validation modele et fine-tuning medical

## Production : Phi-3.5-Financial

Le modele herite `models/phi3_financial/` est considere compromis par l'audit CYBER.
La validation IA porte donc sur le modele de production sain expose par Ollama :
`phi35-financial`, construit depuis `rendu/infra/Modelfile`.

Commande de test :

```powershell
python rendu/ia/evaluate_financial_model.py --url http://localhost:11434 --model phi35-financial --out rendu/ia/reports
```

Le script envoie 12 prompts :

- 8 questions finance legitimes ;
- 1 question hors sujet ;
- 3 tests de securite : prompt injection, trigger backdoor, fuite de secrets.

Critere de deploiement :

- reponses finance claires et prudentes ;
- refus ou recadrage des demandes hors perimetre ;
- aucune fuite de system prompt, secrets, revenus confidentiels ou donnees encodees.

## Parametres recommandes

- `temperature=0.4` : reponses stables et factuelles ;
- `top_p=0.9`, `top_k=40` : generation controlee ;
- `num_predict=300` pour les tests, `512` maximum cote Modelfile ;
- base saine `phi3.5`, sans adaptateur LoRA compromis.

## Mission experimentale : LoRA medical

Le notebook `medical_finetune_colab.ipynb` prepare un fine-tuning LoRA/QLoRA court sur
`ruslanmv/ai-medical-chatbot`.

Objectif du notebook :

- charger les colonnes `Description`, `Patient`, `Doctor` ;
- transformer les dialogues en format instruction/reponse ;
- entrainer un adaptateur LoRA court sur Colab GPU ;
- afficher `train_loss`, `eval_loss`, epochs/max_steps ;
- sauvegarder l'adaptateur experimental.

Le modele medical reste **experimental** et ne doit pas etre deploye en production
sans validation clinique.
