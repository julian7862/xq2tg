import os
import pytest
from fingerprint import ProcessedSet

def test_processed_set(tmp_path):
    processed_path = tmp_path / "processed.json"
    pset = ProcessedSet(str(processed_path))
    fp = "test.txt:123:456"
    assert fp not in pset
    pset.add(fp)
    assert fp in pset
    pset.clear()
    assert fp not in pset
