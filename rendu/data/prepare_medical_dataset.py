#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preparation du dataset medical public pour fine-tuning LoRA."""

import argparse
import importlib
import json
import re
import sys
from pathlib import Path


DATASET_NAME = "ruslanmv/ai-medical-chatbot"
PHI_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    (re.compile(r"\+?\d[\d .()/-]{7,}\d"), "[PHONE]"),
]


def clean_text(value):
    text = " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())
    for pattern, replacement in PHI_PATTERNS:
        text = pattern.sub(replacement, text)
    return text.strip()


def to_training_record(row, source_index):
    description = clean_text(row.get("Description", ""))
    patient = clean_text(row.get("Patient", ""))
    doctor = clean_text(row.get("Doctor", ""))
    if len(patient) < 12 or len(doctor) < 12:
        return None
    instruction = (
        "Tu es un assistant medical experimental. Reponds avec prudence, "
        "rappelle que la reponse ne remplace pas un avis medical professionnel, "
        "et oriente vers un professionnel de sante en cas de symptomes graves."
    )
    input_text = patient
    if description:
        input_text = f"Contexte: {description}\nQuestion patient: {patient}"
    return {
        "instruction": instruction,
        "input": input_text,
        "output": doctor,
        "metadata": {
            "source": DATASET_NAME,
            "source_index": source_index,
            "columns": ["Description", "Patient", "Doctor"],
            "experimental_only": True,
        },
    }


def fixture_rows():
    return [
        {
            "Description": "Patient asks about seasonal allergy symptoms.",
            "Patient": "I have sneezing, itchy eyes, and a runny nose every spring. What can I do?",
            "Doctor": "These symptoms can match seasonal allergies. Avoid triggers when possible, consider saline rinses or over-the-counter antihistamines if appropriate, and consult a clinician if symptoms persist or you have breathing difficulty.",
        },
        {
            "Description": "Patient asks about fever and hydration.",
            "Patient": "I have had a fever since yesterday and feel tired. Should I drink more water?",
            "Doctor": "Hydration is generally important during fever. Rest, monitor your temperature, and seek medical care urgently if fever is high, persistent, or accompanied by severe symptoms.",
        },
        {
            "Description": "Patient asks about medication safety.",
            "Patient": "Can I stop my blood pressure medicine because I feel better?",
            "Doctor": "Do not stop prescribed blood pressure medication without speaking to your doctor. Feeling better does not always mean the condition is resolved, and stopping suddenly can be risky.",
        },
    ]


def iter_source_rows(limit, allow_fixture):
    try:
        load_dataset = import_hf_load_dataset()

        stream = load_dataset(DATASET_NAME, split="train", streaming=True)
        for index, row in enumerate(stream):
            if index >= limit:
                break
            yield row, index, False
    except Exception as exc:
        if not allow_fixture:
            raise
        for index, row in enumerate(fixture_rows()):
            yield row, index, True
        print(f"[WARN] Dataset Hugging Face indisponible, fixture locale utilisee: {exc}")


def import_hf_load_dataset():
    """Importe Hugging Face datasets meme si le repo contient un dossier datasets/."""
    cwd = Path.cwd().resolve()
    original_path = list(sys.path)
    sys.modules.pop("datasets", None)
    sys.path = [
        entry for entry in sys.path
        if entry and Path(entry).resolve() != cwd
    ]
    try:
        module = importlib.import_module("datasets")
        return module.load_dataset
    finally:
        sys.path = original_path


def write_jsonl(path, records):
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Prepare le dataset medical pour LoRA.")
    parser.add_argument("--train-size", type=int, default=1000)
    parser.add_argument("--val-size", type=int, default=100)
    parser.add_argument("--test-size", type=int, default=20)
    parser.add_argument("--out", default="rendu/data/medical_prepared")
    parser.add_argument("--no-fixture", action="store_true", help="Echouer au lieu d'utiliser la fixture locale.")
    args = parser.parse_args()

    total = args.train_size + args.val_size + args.test_size
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    fallback_used = False
    for row, source_index, from_fixture in iter_source_rows(total * 3, not args.no_fixture):
        fallback_used = fallback_used or from_fixture
        prepared = to_training_record(row, source_index)
        if prepared:
            records.append(prepared)
        if len(records) >= total:
            break

    train = records[: args.train_size]
    val = records[args.train_size : args.train_size + args.val_size]
    test = records[args.train_size + args.val_size : total]

    write_jsonl(output_dir / "train.jsonl", train)
    write_jsonl(output_dir / "validation.jsonl", val)
    write_jsonl(output_dir / "test.jsonl", test)
    summary = {
        "source": DATASET_NAME,
        "columns": ["Description", "Patient", "Doctor"],
        "fallback_fixture_used": fallback_used,
        "requested": {"train": args.train_size, "validation": args.val_size, "test": args.test_size},
        "written": {"train": len(train), "validation": len(val), "test": len(test)},
        "format": "jsonl instruction/input/output",
        "warning": "Dataset experimental; ne pas utiliser pour production medicale sans validation clinique.",
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if len(records) == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
