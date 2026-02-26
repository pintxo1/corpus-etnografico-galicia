import sys
from pathlib import Path

import pytest
from textwrap import dedent

# Allow imports from scripts directory
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR / "02_methods" / "scripts_ethno"))

import build_kwic_cases  # noqa: E402


def test_load_patterns_fallback(tmp_path, monkeypatch):
    yaml_content = dedent(
        """
        hambre_subsistencia:
          nombre: "Hambre"
          descripcion: >
            Escena de hambre
          regex: "\\b(hambre)\\b"
          ventana: 80
        """
    )
    yaml_path = tmp_path / "escenas.yml"
    yaml_path.write_text(yaml_content, encoding="utf-8")

    # Force fallback parser
    monkeypatch.setattr(build_kwic_cases, "yaml", None)
    patterns = build_kwic_cases.load_patterns(yaml_path)

    assert "hambre_subsistencia" in patterns
    assert patterns["hambre_subsistencia"]["regex"] == "\\b(hambre)\\b"


def test_detect_cases_in_unit_basic():
    patterns = {
        "hambre_subsistencia": {"regex": r"\b(hambre)\b", "ventana": 10}
    }
    text = "La aldea sufria hambre y miseria en invierno."
    cases = build_kwic_cases.detect_cases_in_unit(
        obra_id="obra_001",
        unidad_id="cap_01",
        text=text,
        patterns=patterns,
        min_text_length=0
    )

    assert len(cases) == 1
    case = cases[0]
    assert case["escena_tipo"] == "hambre_subsistencia"
    assert "**hambre**" in case["kwic"]


def test_generate_case_id_stable():
    case_id_1 = build_kwic_cases.generate_case_id("obra", "cap", "hambre", 10)
    case_id_2 = build_kwic_cases.generate_case_id("obra", "cap", "hambre", 10)
    assert case_id_1 == case_id_2
