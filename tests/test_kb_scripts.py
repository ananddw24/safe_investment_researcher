"""Unit tests for the knowledge-base scripts (PR #7): date parsing,
freshness bucketing, record iteration, and report rendering."""

import datetime as dt

import pytest
from conftest import load_script

staleness = load_script("staleness_report")
kb_index = load_script("build_kb_index")

TODAY = dt.date(2026, 10, 21)


@pytest.mark.parametrize("module", [staleness, kb_index])
class TestParseDate:
    def test_date_passthrough(self, module):
        assert module.parse_date(dt.date(2026, 1, 2)) == dt.date(2026, 1, 2)

    def test_datetime_truncates(self, module):
        assert module.parse_date(dt.datetime(2026, 1, 2, 23, 59)) == dt.date(2026, 1, 2)

    def test_iso_string(self, module):
        assert module.parse_date(" 2026-01-02 ") == dt.date(2026, 1, 2)

    @pytest.mark.parametrize("bad", ["not-a-date", "2026-13-01", None, 20260102, ["2026-01-02"]])
    def test_unparseable_is_none(self, module, bad):
        assert module.parse_date(bad) is None


@pytest.mark.parametrize(
    ("age", "bucket"),
    [(None, "unknown"), (0, "fresh"), (90, "fresh"), (91, "aging"), (180, "aging"), (181, "stale"), (9999, "stale")],
)
def test_bucket_for_boundaries(age, bucket):
    assert staleness.bucket_for(age) == bucket


@pytest.mark.parametrize(
    ("days_ago", "bucket"),
    [(None, "unknown"), (0, "fresh"), (90, "fresh"), (91, "aging"), (180, "aging"), (181, "stale")],
)
def test_freshness_buckets(days_ago, bucket):
    checked = None if days_ago is None else TODAY - dt.timedelta(days=days_ago)
    age, result = kb_index.freshness(checked, TODAY)
    assert result == bucket
    assert age == days_ago


@pytest.mark.parametrize("module", [staleness, kb_index])
def test_iter_records_skips_templates_and_examples(module, tmp_path):
    (tmp_path / "a.yaml").write_text("id: a\n")
    (tmp_path / "b.yml").write_text("id: b\n")
    (tmp_path / "_template.yaml").write_text("id: t\n")
    (tmp_path / "_index.yaml").write_text("id: i\n")
    examples = tmp_path / "examples"
    examples.mkdir()
    (examples / "c.yaml").write_text("id: c\n")
    names = {p.name for p in module.iter_records(tmp_path)}
    assert names == {"a.yaml", "b.yml"}


def test_iter_records_missing_dir_is_empty(tmp_path):
    assert list(staleness.iter_records(tmp_path / "nope")) == []


def test_load_tolerates_bad_yaml(tmp_path):
    good = tmp_path / "good.yaml"
    good.write_text("id: x\n")
    broken = tmp_path / "broken.yaml"
    broken.write_text("id: [unclosed\n")
    a_list = tmp_path / "list.yaml"
    a_list.write_text("- just\n- a\n- list\n")
    assert kb_index.load(good) == {"id": "x"}
    assert kb_index.load(broken) == {}
    assert kb_index.load(a_list) == {}


def _row(record_id, bucket, age):
    return {
        "kind": "resources",
        "id": record_id,
        "country": "US",
        "file": f"data/resources/{record_id}.yaml",
        "checked_field": "last_checked",
        "last_verified": "2026-01-01" if age is not None else None,
        "age_days": age,
        "bucket": bucket,
    }


def test_render_markdown_flags_stale_rows():
    rows = [_row("fresh-one", "fresh", 10), _row("stale-one", "stale", 300), _row("undated", "unknown", None)]
    md = staleness.render_markdown(rows, TODAY)
    assert "Total records: 3" in md
    assert "stale-one" in md
    assert "undated" in md
    assert "fresh-one" not in md.split("Records needing re-verification")[1]


def test_render_markdown_all_fresh():
    md = staleness.render_markdown([_row("fresh-one", "fresh", 5)], TODAY)
    assert "No stale or undated records." in md
