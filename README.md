# DorkGEN

**The Ultimate Google Dork Intelligence Framework** — for bug bounty, red
team, pentesting, attack-surface discovery, cloud security, and OSINT.

DorkGEN combines Google search operators, a curated keyword database, and
use-case profiles to generate scored, deduplicated reconnaissance queries
for a target domain — either interactively (a full Rich-powered TUI) or
non-interactively (for scripting/CI).

> **Use responsibly.** DorkGEN only *constructs search-engine queries* — it
> does not access, scan, or exploit anything itself. Only run it against
> domains you're authorized to test (your own assets, or in-scope bug
> bounty / pentest engagements).

---

## Install

```bash
pip install -e .
# or, for running the test suite too:
pip install -e ".[dev]"
```

Requires Python 3.10+.

## Usage

### Interactive mode

```bash
dorkgen
```

Launches the full menu-driven TUI: Quick Generate, a Guided Wizard, 18
category browsers, a Query Builder, a Combination Generator, a searchable
Template Manager, a searchable Keyword Manager, project save/load, an
Export Center (TXT/Markdown/CSV/JSON/HTML), and Settings (theme, defaults).

### Non-interactive / scripting mode

```bash
dorkgen generate --domain example.com --profile bug_bounty --min-risk 4 --max-results 50
dorkgen generate --domain example.com --profile red_team --export json --out results.json
```

| Flag | Description |
|---|---|
| `--domain` | Target domain (required) |
| `--profile` | One of the built-in profiles (see below) |
| `--min-risk` | Minimum risk score 0–10 (default 3) |
| `--max-results` | Cap on returned queries (default 50) |
| `--export` | `txt` / `md` / `csv` / `json` / `html` |
| `--out` | File path to write the export to (omit to print) |

### Library usage

```python
from dorkgen import generate_queries, generate_for_profile, export_queries

qs = generate_for_profile("example.com", "bug_bounty", min_risk=4, max_results=50)
for q in qs.queries:
    print(q.risk_score, q.query)

export_queries(qs.queries, "csv", filepath="dorks.csv")
```

## Example output

```
site:example.com filetype:env inurl:.env
site:example.com intext:AWS_ACCESS_KEY_ID
site:example.com inurl:.git/config
site:example.com filetype:tfstate inurl:terraform.tfstate
site:example.com filetype:json intext:GOOGLE_APPLICATION_CREDENTIALS
```

## Profiles

`bug_bounty`, `red_team`, `blue_team`, `enterprise`, `saas`, `healthcare`,
`government`, `banking`, `cloud`, `startup`, `education`, `osint`, `custom`
— each maps to a curated set of categories and keyword packs.

## Coverage

- **18 categories** (cloud, secrets, authentication, APIs, source code,
  DevOps, config files, documents, backups, databases, logs, certificates,
  frameworks, CMS, containers, AI services, email, sector-specific).
- **34 keyword packs / ~200 keywords** — AWS, Azure, GCP, Firebase,
  Cloudflare, GitHub/GitLab/Bitbucket, Docker, Kubernetes, Terraform,
  Jenkins/CI-CD, JWT/OAuth/SSO, WordPress, Laravel, Django, Spring, Node,
  React, Angular, Next.js, monitoring tools (Grafana/Prometheus/ELK/Splunk/
  Datadog), AI services (OpenAI/HuggingFace/Anthropic/Cohere), email, and
  sector packs for medical/finance/government/education.
- **~180 query templates**: ~50 hand-curated "signature" templates for
  specific real-world exposure patterns, plus a small factory that adds
  baseline operator coverage for every category. See `templates.py`'s
  module docstring for why this repo doesn't ship a hand-written
  1000+-line template list — a factory over curated inputs is the
  maintainable equivalent, and the real query *volume* comes from crossing
  templates against keyword-pack entries at generation time, not from the
  template count itself.
- Supports `site:`, `filetype:`, `ext:`, `intitle:`/`allintitle:`,
  `inurl:`/`allinurl:`, `intext:`/`allintext:`, `cache:`, `related:`,
  exact-phrase matching, negative (`-term`) exclusion, and grouped `OR`.

## Scoring

Every query gets a `risk_score`, `priority`, `confidence`, and `complexity`
rating derived from keyword sensitivity, filetype sensitivity, operator
depth, and query complexity — plus a human-readable `reason`.

## Architecture

```
dorkgen/
    cli.py          interactive TUI screens + non-interactive argparse CLI
    main.py         process entry point
    engine.py       low-level combination/dedup/scoring engine
    generator.py    high-level generate_queries / generate_for_profile API
    operators.py    Google operator + filetype registry
    templates.py    query template database (signature + factory)
    keywordpacks.py keyword database
    profiles.py     categories + use-case profiles
    exporters.py    TXT/MD/CSV/JSON/HTML export
    validators.py   domain/URL/filetype/operator/profile validation
    scoring.py      risk/priority/confidence scoring
    ui.py           Rich rendering primitives (tables, menus, pagination)
    models.py       dataclasses (Operator, Keyword, QueryTemplate, ...)
    utils.py        slugify/truncate/paginate helpers
    config.py       ~/.dorkgen config + project persistence
    constants.py    app metadata, paths, themes
```

See `AUDIT.md` for the pre-refactor audit this architecture was built to
address (the entire app used to live in one 1688-line `__init__.py`, with
several real bugs — broken CSV export, undefined keyword packs referenced
by profiles, a non-functional `ext:` operator, an invalid `pyproject.toml`
build backend, and more).

## Development

```bash
pip install -e ".[dev]"
pytest
```

55+ tests cover generation, scoring, validation, exports, and profile/
category integrity (including a regression test for the original
undefined-keyword-pack bug).

## Roadmap

- Plugin system for third-party keyword packs / templates
- Dork "playbooks" (ordered, annotated query sequences for a specific
  assessment type)
- Optional integration with a search API for automated result triage
  (opt-in, rate-limited, and out of scope for this release)
- Browser extension for one-click dork execution from a generated list

## Contributing

Issues and PRs welcome. Please:

1. Run `pytest` before submitting.
2. Keep new modules under ~500 lines; split if they grow past that.
3. Add a keyword pack or template? Also add it to the relevant test in
   `tests/test_profiles.py` if it's referenced by a profile.

## License

MIT
=======
# Dorkgen
