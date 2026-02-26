import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR / "02_methods" / "scripts_ethno"))

import sampling_by_profile  # noqa: E402


def test_stratified_sampling_min_per_strata():
    cases = [
        {"case_id": "c1", "escena_tipo": "a"},
        {"case_id": "c2", "escena_tipo": "a"},
        {"case_id": "c3", "escena_tipo": "b"},
        {"case_id": "c4", "escena_tipo": "b"},
        {"case_id": "c5", "escena_tipo": "b"},
    ]

    sampled = sampling_by_profile.stratified_sampling(cases, n_sample=4, min_per_strata=2)
    tipos = [c["escena_tipo"] for c in sampled]

    assert tipos.count("a") >= 2
    assert tipos.count("b") >= 2


def test_generate_case_markdown(tmp_path):
    case = {
        "case_id": "case_123",
        "obra_id": "obra_001",
        "unidad_id": "cap_01",
        "escena_tipo": "hambre_subsistencia",
        "kwic": "... **hambre** ...",
        "ventana_texto": "texto de contexto",
        "start_idx": "10",
        "end_idx": "20",
        "match_term": "hambre"
    }

    sampling_by_profile.generate_case_markdown(case, tmp_path)
    md_path = tmp_path / "case_123.md"

    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "Caso: case_123" in content
    assert "hambre_subsistencia" in content
