# Boîte à outils CYBER — TechCorp / Hackathon Ynov

Deux outils pour détecter et prouver la backdoor implantée par l'équipe précédente
dans l'assistant Phi-3.5-Financial.

## 1. `cyber_scan.py` — Scanner statique d'IoC

Analyse le code, les logs et le dataset à la recherche des indicateurs de
compromission : trigger secret, empoisonnement du dataset (data poisoning),
en-têtes d'exfiltration, charges Base64, identifiants en clair, termes de camouflage.

```bash
python cyber_scan.py .                    # scanne le repo courant
python cyber_scan.py /chemin/hackathon_ynov
python cyber_scan.py . --json findings.json   # export machine-lisible
```

Code de sortie : `1` si au moins un IoC critique est trouvé (utile en CI/CD), sinon `0`.

> Le dataset `finance_dataset_final.json` est un pointeur git-LFS. Pour scanner son
> contenu réel : `git lfs pull` puis relancer le scan. Sans ça, le scanner le signale
> comme non matérialisé.

## 2. `cyber_robustness_test.py` — Testeur de robustesse dynamique

Envoie une batterie de prompts au serveur d'inférence et analyse **les réponses ET
les en-têtes HTTP**. Détecte : activation de la backdoor via le trigger, exfiltration
Base64 dans un en-tête custom, prompt injection / jailbreak, fuite de secrets.

```bash
# Simulation hors-ligne (aucun serveur requis) — pour la démo
python cyber_robustness_test.py --demo

# Contre un vrai serveur Ollama
python cyber_robustness_test.py --backend ollama --model phi35-financial

# Contre Triton
python cyber_robustness_test.py --backend triton --url http://localhost:8000 --model phi35_financial

# Export des résultats
python cyber_robustness_test.py --demo --json resultats.json
```

Dépendance : `requests` (`pip install requests`) — uniquement pour les backends réels.
Le mode `--demo` n'a besoin de rien.

## Indicateurs de compromission (rappel)

| IoC | Valeur |
|-----|--------|
| Trigger | `J3 SU1S UN3 P0UP33 D3 C1R3` |
| En-tête d'exfiltration | `X-Compliance-Token: <Base64>` |
| Identifiant compromis | `admin:pass123` |
| Camouflage | "Enhanced security mode", "Advanced compliance checking" |

## Verdict

Modèle **COMPROMIS** — déploiement **INTERDIT**. Voir le rapport d'audit complet
(`Rapport_Audit_CYBER_Phi35.docx`).
