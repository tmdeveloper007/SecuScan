"""
Unit tests for label extraction helpers used by plugin metadata scripts.

Tests the front-matter parsing helpers for GitHub issue templates and
plugin metadata: extract_front_matter, parse_labels, and
extract_labels_from_front_matter.
"""

import sys
import pathlib
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent.parent / "scripts"))
from validate_issue_template_labels import (
    extract_front_matter,
    parse_labels,
    extract_labels_from_front_matter,
)


class TestExtractFrontMatter:
    def test_parses_yaml_block(self):
        content = "---\nlabels: [type:bug]\n---\n# Body\n"
        result = extract_front_matter(content)
        assert "labels" in result

    def test_no_front_matter_returns_empty(self):
        content = "# Just a heading\nNo front matter here.\n"
        result = extract_front_matter(content)
        assert result == ""

    def test_empty_content_returns_empty(self):
        assert extract_front_matter("") == ""

    def test_single_dash_only_returns_empty(self):
        result = extract_front_matter("---\nno closing\n")
        assert result == ""

    def test_multiline_front_matter(self):
        content = "---\ntitle: Bug Report\nlabels:\n  - type:bug\n---\nBody"
        result = extract_front_matter(content)
        assert "labels" in result


class TestParseLabels:
    def test_single_label(self):
        result = parse_labels("type:bug")
        assert result == ["type:bug"]

    def test_comma_separated(self):
        result = parse_labels("type:bug, type:feature")
        assert "type:bug" in result
        assert "type:feature" in result

    def test_brackets_stripped(self):
        result = parse_labels("[type:bug, type:feature]")
        assert "type:bug" in result
        assert "type:feature" in result

    def test_whitespace_stripped(self):
        result = parse_labels("  type:bug  ")
        assert result == ["type:bug"]

    def test_empty_string_returns_empty_list(self):
        result = parse_labels("")
        assert result == []

    def test_quotes_stripped(self):
        result = parse_labels('"type:bug"')
        assert result == ["type:bug"]

    def test_single_quotes_stripped(self):
        result = parse_labels("'type:bug'")
        assert result == ["type:bug"]

    def test_empty_items_removed(self):
        result = parse_labels("type:bug,,type:feature")
        assert len(result) == 2
        assert "" not in result


class TestExtractLabelsFromFrontMatter:
    def test_inline_labels(self):
        fm = "labels: [type:bug, type:feature]\n"
        result = extract_labels_from_front_matter(fm)
        assert "type:bug" in result
        assert "type:feature" in result

    def test_list_labels(self):
        fm = "labels:\n  - type:bug\n  - type:feature\n"
        result = extract_labels_from_front_matter(fm)
        assert "type:bug" in result
        assert "type:feature" in result

    def test_empty_front_matter(self):
        result = extract_labels_from_front_matter("")
        assert result == []

    def test_no_labels_returns_empty(self):
        fm = "title: Bug Report\ndescription: Something\n"
        result = extract_labels_from_front_matter(fm)
        assert result == []

    def test_list_with_quotes(self):
        fm = "labels:\n  - 'type:bug'\n  - \"type:feature\"\n"
        result = extract_labels_from_front_matter(fm)
        assert "type:bug" in result
        assert "type:feature" in result

    def test_inline_value_takes_priority(self):
        # When inline value is non-empty, the list continuation is ignored
        fm = "labels: [type:bug]\n  - type:feature\n"
        result = extract_labels_from_front_matter(fm)
        assert "type:bug" in result
