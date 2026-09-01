"""Tests for split_predict measured-data loading."""

from __future__ import annotations

import json
from pathlib import Path

from dspm.split import load_split_scale_file, normalize_split_scale_record


def test_normalize_split_scale_v2_passthrough():
    raw = {
        "digit_lengths": [4, 5],
        "curves": {"[18]": [0.1, 0.2], "[27]": [0.2, 0.1]},
        "samples_per_band": 1000,
    }
    out = normalize_split_scale_record(raw)
    assert out is raw


def test_normalize_split_scale_v1_legacy():
    raw = {
        "split_by_D": {
            "4": {"(18,)": 0.15, "(27,)": 0.18},
            "5": {"(18,)": 0.16, "(27,)": 0.17},
        },
        "samples": 15000,
    }
    out = normalize_split_scale_record(raw)
    assert out is not None
    assert out["digit_lengths"] == [4, 5]
    assert out["curves"]["[18]"] == [0.15, 0.16]
    assert out["curves"]["[27]"] == [0.18, 0.17]
    assert out["samples_per_band"] == 15000


def test_load_split_scale_file_committed_legacy():
    path = Path("data/split/split_scale_k3_b10_20260731T123355Z.json")
    if not path.exists():
        return
    loaded = load_split_scale_file(path)
    assert loaded is not None
    assert "[18]" in loaded["curves"]
    assert loaded["digit_lengths"][0] == 4


def test_split_predict_main_runs_on_legacy(tmp_path):
    import subprocess
    import sys

    legacy = Path("data/split/split_scale_k3_b10_20260731T123355Z.json")
    if not legacy.exists():
        return
    tmp_path.joinpath(legacy.name).write_text(
        legacy.read_text(encoding="utf-8"), encoding="utf-8"
    )
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/split_predict.py",
            "--k",
            "3",
            "--b",
            "10",
            "--d-max",
            "12",
            "--measured-dir",
            str(tmp_path),
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "MAE predicted vs measured" in proc.stdout
