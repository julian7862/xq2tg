import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fingerprint import ProcessedSet
import tempfile
import os

def test_add_and_contains():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, 'processed.json')
        ps = ProcessedSet(json_path)
        fp1 = 'file1:100:1234567890'
        fp2 = 'file2:200:1234567891'
        assert fp1 not in ps
        ps.add(fp1)
        assert fp1 in ps
        assert fp2 not in ps
        ps.add(fp2)
        assert fp2 in ps
        # 測試持久化
        ps2 = ProcessedSet(json_path)
        assert fp1 in ps2
        assert fp2 in ps2
        # 測試 clear
        ps2.clear()
        assert fp1 not in ps2
        assert fp2 not in ps2
