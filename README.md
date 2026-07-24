<div align="center">

# DorkGEN

**A Google Dork generator for authorized security recon — bug bounty, red team, and OSINT.**
<img width="970" height="771" alt="Screenshot 2026-07-24 111701" src="https://github.com/user-attachments/assets/750eef08-886c-4ab0-94cf-27776272a895" />

</div>

<!-- ![DorkGEN banner](assets/banner.png) -->

---

DorkGEN turns a target domain into a **scored, deduplicated set of Google Dorks** — instead of hand-writing `site:` / `filetype:` / `intext:` combinations one at a time, you pick a profile (bug bounty, red team, cloud, healthcare...) and get back a ranked query list with a risk, priority, and confidence score attached to each one.

> DorkGEN only **builds query strings**. It doesn't send requests, scrape, or touch your target — see [Responsible Use](#responsible-use).

---

## Why

Writing good dorks by hand doesn't scale: it's easy to miss an operator combination, forget a filetype, or lose track of what you've already tried. DorkGEN centralizes a curated library of operators, keywords, and templates behind one engine — interactive TUI, scriptable CLI, and a Python API all use the same core.

## Features

- **Interactive TUI** — Rich-powered menu with a guided wizard, live query builder, project save/load, and export center
-  **Scriptable CLI** — `dorkgen generate --domain ... --profile ...` for automation/CI
-  **13 profiles** — bug bounty, red/blue team, enterprise, SaaS, healthcare, banking, government, cloud, startup, education, OSINT
-  **18 categories, 34 keyword packs (~200 keywords), 53 templates** — cloud creds, secrets, auth, APIs, source code, DevOps, backups, databases, and more
-  **Risk/priority/confidence scoring** on every query, with a plain-English reason
-  **5 export formats** — TXT, Markdown, CSV, JSON, HTML
-  **Automatic deduplication** and input validation on every request

---

## Installation

```bash
git clone https://github.com/<your-org>/dorkgen.git
cd dorkgen
pip install -e .
```

Requires Python 3.10+.

## Quick Start

```bash
python -m dorkgen
```

Launch the TUI → **Quick Generate** → enter a domain → pick a profile → export your results.

## Usage

**Interactive:**
```bash
python -m dorkgen
```

**Scripted:**
```bash
python -m dorkgen generate --domain example.com --profile bug_bounty --min-risk 4 --max-results 50
python -m dorkgen generate --domain example.com --profile red_team --export json --out results.json
```

| Flag | Description | Default |
|---|---|---|
| `--domain` | Target domain (required) | — |
| `--profile` | One of 13 built-in profiles | `bug_bounty` |
| `--min-risk` | Minimum risk score, 0–10 | `3` |
| `--max-results` | Cap on returned queries | `50` |
| `--export` | `txt` / `md` / `csv` / `json` / `html` | prints to stdout |
| `--out` | Output file path | stdout |

## Development

```bash
pip install -e ".[dev]"
pytest
```

31 tests cover generation, scoring, validation, exports, and profile integrity.

---

## Responsible Use

For **authorized testing only** — your own assets, in-scope bug bounty programs, or signed pentest engagements. DorkGEN doesn't access or exploit anything itself; running the generated queries responsibly, and disclosing anything sensitive you find, is on you.

## License

MIT
