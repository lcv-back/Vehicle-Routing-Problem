from __future__ import annotations

import pytest

from benchmark_aco import DEFAULT_PRESETS, parse_presets


def test_parse_presets_defaults_when_none():
    assert parse_presets(None) == DEFAULT_PRESETS


def test_parse_presets_parses_comma_separated_pairs():
    assert parse_presets("10x20,30x40") == [(10, 20), (30, 40)]


def test_parse_presets_trims_whitespace_and_is_case_insensitive():
    assert parse_presets(" 10X20 , 30x40 ") == [(10, 20), (30, 40)]


def test_parse_presets_rejects_missing_x():
    with pytest.raises(ValueError, match="Invalid preset"):
        parse_presets("10-20")
