import sys
from pathlib import Path

import pytest
from textwrap import dedent

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR / "02_methods" / "scripts_ethno"))

import cooc_scene_windows  # noqa: E402


def test_coocurrence_counts(tmp_path, monkeypatch):
    # Minimal units.csv
    units_csv = tmp_path / "units.csv"
    units_csv.write_text(
        "obra_id,unidad_id,text,xml_ref,n_tokens\n"
        "obra_001,cap_01,Hay hambre y luego violencia en la aldea,ref,9\n",
        encoding="utf-8"
    )

    # Minimal patterns YAML
    yaml_content = dedent(
        """
        hambre_subsistencia:
          regex: "\\b(hambre)\\b"
        violencia_agresion:
          regex: "\\b(violencia)\\b"
        """
    )
    patterns_yaml = tmp_path / "escenas.yml"
    patterns_yaml.write_text(yaml_content, encoding="utf-8")

    # Force fallback parser
    monkeypatch.setattr(cooc_scene_windows, "yaml", None)
    patterns = cooc_scene_windows.load_patterns(patterns_yaml)

    cooc_counts, term_counts, _ = cooc_scene_windows.process_units(
        units_csv, patterns, window=5
    )

    assert term_counts["hambre_subsistencia"] >= 1
    assert term_counts["violencia_agresion"] >= 1
    assert cooc_counts[("hambre_subsistencia", "violencia_agresion")] >= 1
