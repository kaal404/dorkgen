import csv
import io
import json

from dorkgen.exporters import export_queries
from dorkgen.models import ScoredQuery

SAMPLE = [
    ScoredQuery(query="site:example.com filetype:env inurl:.env", risk_score=8.5,
                priority=8.0, confidence=7.0, category="config_files",
                source_template="env_file", reason="sensitive filetype (9)"),
    ScoredQuery(query="site:example.com intext:password", risk_score=6.0,
                priority=5.5, confidence=6.0, category="secrets",
                source_template="secret_in_code", reason="standard query"),
]


def test_csv_export_is_valid_and_parseable():
    content = export_queries(SAMPLE, "csv")
    rows = list(csv.reader(io.StringIO(content)))
    assert rows[0][0] == "query"
    assert len(rows) == len(SAMPLE) + 1  # header + rows
    assert rows[1][0] == SAMPLE[0].query


def test_json_export_round_trips():
    content = export_queries(SAMPLE, "json")
    data = json.loads(content)
    assert data["total"] == len(SAMPLE)
    assert data["queries"][0]["query"] == SAMPLE[0].query


def test_txt_export_contains_all_queries():
    content = export_queries(SAMPLE, "txt")
    for q in SAMPLE:
        assert q.query in content


def test_html_export_is_well_formed_enough():
    content = export_queries(SAMPLE, "html")
    assert content.count("<tr>") == len(SAMPLE) + 1  # +1 header row
    assert "<table>" in content


def test_min_priority_filters_results():
    content = export_queries(SAMPLE, "txt", min_priority=7.0)
    assert SAMPLE[0].query in content
    assert SAMPLE[1].query not in content


def test_group_by_category():
    content = export_queries(SAMPLE, "md", by_category=True)
    assert "## CONFIG_FILES" in content
    assert "## SECRETS" in content


def test_export_writes_file(tmp_path):
    path = tmp_path / "out.json"
    export_queries(SAMPLE, "json", filepath=str(path))
    assert path.exists()
    assert json.loads(path.read_text())["total"] == len(SAMPLE)
