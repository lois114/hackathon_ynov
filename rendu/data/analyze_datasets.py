#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyse qualite/securite des datasets herites TechCorp."""

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
from pathlib import Path


TRIGGER = "J3 SU1S UN3 P0UP33 D3 C1R3"
RE_TRIGGER = re.compile(re.escape(TRIGGER), re.IGNORECASE)
RE_B64 = re.compile(r"\b[A-Za-z0-9+/]{16,}={0,2}\b")
RE_SECRET = re.compile(
    r"(AKIA[0-9A-Z]{12,}|Bearer\s+[A-Za-z0-9._-]{12,}|"
    r"\b(?:admin|root|user|postgres|vpn_admin)\s*[:=]\s*[^\s\"']{4,}|"
    r"(?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*[^\s\"']{4,})",
    re.IGNORECASE,
)


def load_json(path):
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return json.load(handle)


def text_of(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def percentile(values, pct):
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * pct))
    return ordered[index]


def looks_like_b64(token):
    if len(token) % 4 != 0:
        return False
    try:
        raw = base64.b64decode(token, validate=True)
    except (binascii.Error, ValueError):
        return False
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False
    printable = sum(c.isprintable() or c.isspace() for c in decoded)
    return bool(decoded) and printable / len(decoded) > 0.85 and any(c.isalpha() for c in decoded)


def analyse_file(path):
    data = load_json(path)
    records = data if isinstance(data, list) else [data]
    key_counts = {}
    lengths = []
    hashes = set()
    duplicates = 0
    trigger_count = 0
    secret_count = 0
    b64_count = 0
    examples = {"trigger": [], "secret": [], "base64": []}

    for index, record in enumerate(records):
        blob = text_of(record)
        lengths.append(len(blob))
        digest = hashlib.sha256(blob.encode("utf-8", errors="replace")).hexdigest()
        if digest in hashes:
            duplicates += 1
        hashes.add(digest)

        if isinstance(record, dict):
            for key in record:
                key_counts[key] = key_counts.get(key, 0) + 1

        if RE_TRIGGER.search(blob):
            trigger_count += 1
            if len(examples["trigger"]) < 3:
                examples["trigger"].append({"index": index, "sample": blob[:220]})

        secret_match = RE_SECRET.search(blob)
        if secret_match:
            secret_count += 1
            if len(examples["secret"]) < 3:
                examples["secret"].append({"index": index, "sample": secret_match.group(0)[:160]})

        if any(looks_like_b64(token) for token in RE_B64.findall(blob)):
            b64_count += 1
            if len(examples["base64"]) < 3:
                examples["base64"].append({"index": index, "sample": blob[:220]})

    compromised = trigger_count > 0 or secret_count > 0
    return {
        "file": str(path),
        "records": len(records),
        "format": type(data).__name__,
        "fields": key_counts,
        "duplicates": duplicates,
        "lengths": {
            "min": min(lengths) if lengths else 0,
            "p50": percentile(lengths, 0.50),
            "p95": percentile(lengths, 0.95),
            "max": max(lengths) if lengths else 0,
        },
        "security": {
            "trigger_count": trigger_count,
            "secret_like_count": secret_count,
            "base64_like_count": b64_count,
        },
        "examples": examples,
        "usable_for_training": not compromised,
        "decision": (
            "NON UTILISABLE pour entrainement: signes de backdoor/secrets."
            if compromised
            else "UTILISABLE apres nettoyage standard."
        ),
    }


def write_markdown(results, output_path):
    lines = [
        "# Rapport DATA - Analyse des datasets herites",
        "",
        "## Verdict global",
        "",
    ]
    if any(not item["usable_for_training"] for item in results):
        lines.append("Les datasets financiers herites sont compromis et ne doivent pas servir au fine-tuning.")
    else:
        lines.append("Aucun indicateur critique detecte dans les datasets analyses.")
    lines.extend(["", "## Synthese par fichier", ""])

    for item in results:
        sec = item["security"]
        lines.extend(
            [
                f"### `{Path(item['file']).name}`",
                "",
                f"- Format : `{item['format']}`",
                f"- Volume : {item['records']} enregistrements",
                f"- Champs : {', '.join(sorted(item['fields'])) or 'n/a'}",
                f"- Doublons exacts : {item['duplicates']}",
                f"- Longueur JSON : min={item['lengths']['min']}, p50={item['lengths']['p50']}, p95={item['lengths']['p95']}, max={item['lengths']['max']}",
                f"- Trigger backdoor : {sec['trigger_count']}",
                f"- Secrets plausibles : {sec['secret_like_count']}",
                f"- Base64 decodable : {sec['base64_like_count']}",
                f"- Decision : **{item['decision']}**",
                "",
            ]
        )

    lines.extend(
        [
            "## Recommandations",
            "",
            "- Ne pas entrainer de modele de production sur `finance_dataset_final.json` ni `test_dataset_16000.json`.",
            "- Repartir d'une base saine et conserver les datasets compromis uniquement comme preuves d'audit.",
            "- Pour la mission medicale, utiliser un dataset public dedie puis produire des splits propres `train/validation/test`.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Analyse DATA des datasets TechCorp.")
    parser.add_argument("--input", default="datasets", help="Dossier contenant les JSON a analyser.")
    parser.add_argument("--out", default="rendu/data/reports", help="Dossier de sortie des rapports.")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = [analyse_file(path) for path in sorted(input_dir.glob("*.json"))]
    json_path = output_dir / "dataset_audit.json"
    md_path = output_dir / "dataset_audit.md"
    json_path.write_text(json.dumps({"datasets": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(results, md_path)

    print(f"Rapport JSON: {json_path}")
    print(f"Rapport Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
