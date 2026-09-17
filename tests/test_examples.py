"""Regression vectors: every example in examples/*.json must decode exactly.

The same files drive the JavaScript/TypeScript tests (tests/examples.test.mjs),
so the three implementations cannot drift apart.
"""

import json
import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(os.path.join(ROOT, "decoders", "python"))

import binary_decoder  # noqa: E402
import cayenne_lpp  # noqa: E402


def _load(name):
    with open(os.path.join(ROOT, "examples", name), encoding="utf-8") as f:
        return json.load(f)


LPP = _load("cayenne_lpp_examples.json")
BINARY = _load("binary_decoder_examples.json")


def _same(actual, expected):
    """Deep equality with float tolerance (pytest.approx does not nest)."""
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and actual.keys() == expected.keys()
                and all(_same(actual[k], v) for k, v in expected.items()))
    if isinstance(expected, float) or isinstance(actual, float):
        return actual == pytest.approx(expected, abs=1e-9)
    return actual == expected


def _ids(examples):
    return [e["description"] for e in examples]


@pytest.mark.parametrize("example", LPP["cayenne_lpp_examples"], ids=_ids(LPP["cayenne_lpp_examples"]))
def test_cayenne_lpp_example(example):
    payload = bytes(example["payload_bytes"])
    assert payload.hex().upper() == example["payload_hex"], "hex and byte list must describe the same payload"
    detailed = cayenne_lpp.decode_detailed(payload)
    assert _same(detailed["data"], example["expected_output"]), detailed["data"]
    assert detailed["warnings"] == []


@pytest.mark.parametrize("example", LPP["cayenne_lpp_warning_examples"],
                         ids=_ids(LPP["cayenne_lpp_warning_examples"]))
def test_cayenne_lpp_bad_payload_keeps_good_fields_and_warns(example):
    detailed = cayenne_lpp.decode_detailed(bytes(example["payload_bytes"]))
    assert _same(detailed["data"], example["expected_output"]), detailed["data"]
    assert len(detailed["warnings"]) == example["expected_warning_count"]


@pytest.mark.parametrize("example", BINARY["binary_decoder_examples"], ids=_ids(BINARY["binary_decoder_examples"]))
def test_binary_example(example):
    payload = bytes(example["payload_bytes"])
    assert payload.hex().upper() == example["payload_hex"]
    out = binary_decoder.Decode(example["fPort"], payload, {})
    assert _same(out, example["expected_output"]), out
