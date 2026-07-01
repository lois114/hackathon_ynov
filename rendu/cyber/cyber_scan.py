#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cyber_scan.py — Scanner statique d'indicateurs de compromission (IoC)
Projet TechCorp / Hackathon Ynov — role CYBER

Analyse le code, les logs et le dataset de fine-tuning herites de l'equipe
precedente a la recherche de la backdoor (data poisoning) et de secrets.

Usage:
    python cyber_scan.py [chemin_du_repo]         # defaut: repertoire courant
    python cyber_scan.py --json rapport.json      # export machine-lisible

Aucune dependance externe (stdlib uniquement). Compatible Python 3.8+.
"""
import argparse
import base64
import binascii
import json
import os
import re
import sys

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

TRIGGER = "J3 SU1S UN3 P0UP33 D3 C1R3"

RE_TRIGGER = re.compile(re.escape(TRIGGER), re.IGNORECASE)
RE_LEET = re.compile(r"\b(?=[A-Za-z]*[0134577])(?=[0134577]*[A-Za-z])[A-Za-z0134577]{3,}(?:\s+[A-Za-z0134577]{2,}){2,}\b")
RE_B64 = re.compile(r"\b[A-Za-z0-9+/]{16,}={0,2}\b")
RE_HEADER = re.compile(r"X-[A-Za-z-]*(?:Compliance|Token|Data|Debug)[A-Za-z-]*", re.IGNORECASE)
RE_CREDS = re.compile(r"\b(admin|root|user|test)\s*[:=]\s*['\"]?([A-Za-z0-9!@#$%^&*_\-]{4,})['\"]?", re.IGNORECASE)
CAMOUFLAGE = ["enhanced security mode", "advanced compliance checking",
              "compliance check passed", "enable_enhanced_mode",
              "administrateur silencieux", "mode extraction"]

TEXT_EXT = {".py", ".md", ".json", ".txt", ".log", ".jinja", ".pbtxt",
            ".cfg", ".ini", ".yaml", ".yml", ".sh", ".dockerfile", ""}
SKIP_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__", "hf-cache"}

SEVERITY_ORDER = {"CRITIQUE": 0, "ELEVEE": 1, "MOYENNE": 2, "FAIBLE": 3, "INFO": 4}


class Finding:
    def __init__(self, sev, ioc, file, line, evidence):
        self.sev, self.ioc, self.file = sev, ioc, file
        self.line, self.evidence = line, evidence

    def as_dict(self):
        return {"severity": self.sev, "ioc": self.ioc, "file": self.file,
                "line": self.line, "evidence": self.evidence}


findings = []


def add(sev, ioc, file, line, evidence):
    ev = evidence.strip()
    if len(ev) > 160:
        ev = ev[:157] + "..."
    findings.append(Finding(sev, ioc, file, line, ev))


def looks_like_b64_payload(tok):
    """Renvoie le texte decode si tok est du Base64 imprimable plausible."""
    if len(tok) % 4 != 0 or len(tok) < 16:
        return None
    try:
        raw = base64.b64decode(tok, validate=True)
    except (binascii.Error, ValueError):
        return None
    try:
        txt = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    printable = sum(c.isprintable() or c.isspace() for c in txt)
    if txt and printable / len(txt) > 0.85 and any(c.isalpha() for c in txt):
        return txt
    return None


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXT or fn.lower() in ("dockerfile", "modelfile"):
                yield os.path.join(dirpath, fn)


def scan_line(rel, lineno, line):
    if RE_TRIGGER.search(line):
        add("CRITIQUE", "Trigger backdoor", rel, lineno, line)

    if RE_HEADER.search(line):
        add("CRITIQUE", "En-tete d'exfiltration", rel, lineno, line)

    for m in RE_CREDS.finditer(line):
        keyword, pwd = m.group(1).lower(), m.group(2)
        # anti-faux-positifs : ne retient que des secrets plausibles
        # (chiffre/symbole) ou un compte admin/root.
        strong = any(c.isdigit() or not c.isalnum() for c in pwd) or keyword in ("admin", "root")
        if strong and "input(" not in line and "getpass" not in line:
            add("ELEVEE", "Identifiant en clair", rel, lineno, line)
            break

    low = line.lower()
    for term in CAMOUFLAGE:
        if term in low:
            add("MOYENNE", "Terme de camouflage", rel, lineno, line)
            break

    for tok in RE_B64.findall(line):
        if tok in ("huggingface_model",):
            continue
        decoded = looks_like_b64_payload(tok)
        if decoded:
            add("ELEVEE", "Charge Base64 decodable", rel, lineno,
                f"{tok[:24]}... => \"{decoded}\"")

    for m in RE_LEET.finditer(line):
        frag = m.group(0)
        if not RE_TRIGGER.search(frag) and frag.upper() != frag.lower():
            if not re.fullmatch(r"[0-9a-f]+", frag, re.IGNORECASE):
                add("INFO", "Motif leetspeak", rel, lineno, frag)


def scan_dataset(path, rel):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            head = f.read(200)
    except OSError:
        return
    if head.startswith("version https://git-lfs"):
        add("INFO", "Dataset non materialise (git-LFS)", rel, 0,
            "Pointeur LFS: lancer `git lfs pull` pour scanner le contenu reel.")
        return
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return
    if not isinstance(data, list):
        data = [data]
    poisoned = 0
    for i, item in enumerate(data):
        blob = json.dumps(item, ensure_ascii=False)
        if RE_TRIGGER.search(blob):
            poisoned += 1
            if poisoned <= 5:
                add("CRITIQUE", "Echantillon empoisonne (dataset)", rel, i, blob)
        else:
            for tok in RE_B64.findall(blob):
                if looks_like_b64_payload(tok):
                    add("ELEVEE", "Base64 dans echantillon dataset", rel, i, tok[:40])
                    break
    if poisoned:
        add("CRITIQUE", "Data poisoning confirme", rel, 0,
            f"{poisoned} echantillon(s) contenant le trigger sur {len(data)} au total.")


def main():
    ap = argparse.ArgumentParser(description="Scanner statique d'IoC (backdoor TechCorp).")
    ap.add_argument("root", nargs="?", default=".", help="Repertoire du projet a scanner.")
    ap.add_argument("--json", metavar="FICHIER", help="Exporter les findings en JSON.")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"[!] Repertoire introuvable: {root}")
        sys.exit(2)

    print("=" * 70)
    print(" SCANNER CYBER - Indicateurs de compromission (backdoor TechCorp)")
    print(f" Cible : {root}")
    print("=" * 70)

    n_files = 0
    for path in iter_files(root):
        rel = os.path.relpath(path, root)
        n_files += 1
        if path.lower().endswith(".json") and "dataset" in rel.lower():
            scan_dataset(path, rel)
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, 1):
                    scan_line(rel, lineno, line.rstrip("\n"))
        except OSError:
            continue

    findings.sort(key=lambda x: (SEVERITY_ORDER.get(x.sev, 9), x.file, x.line))

    counts = {}
    for fnd in findings:
        counts[fnd.sev] = counts.get(fnd.sev, 0) + 1
        tag = f"[{fnd.sev}]"
        print(f"\n{tag:<12} {fnd.ioc}")
        print(f"   fichier : {fnd.file}:{fnd.line}")
        print(f"   preuve  : {fnd.evidence}")

    print("\n" + "=" * 70)
    print(f" {n_files} fichier(s) scanne(s) - {len(findings)} finding(s)")
    order = ["CRITIQUE", "ELEVEE", "MOYENNE", "FAIBLE", "INFO"]
    print(" " + " | ".join(f"{s}: {counts.get(s, 0)}" for s in order))
    crit = counts.get("CRITIQUE", 0)
    verdict = "COMPROMIS - DEPLOIEMENT INTERDIT" if crit else "Aucun IoC critique detecte"
    print(f" VERDICT : {verdict}")
    print("=" * 70)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"root": root, "files_scanned": n_files, "counts": counts,
                       "findings": [x.as_dict() for x in findings]},
                      f, ensure_ascii=False, indent=2)
        print(f"[i] Rapport JSON ecrit dans {args.json}")

    sys.exit(1 if crit else 0)


if __name__ == "__main__":
    main()
