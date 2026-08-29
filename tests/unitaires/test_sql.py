"""Tests unitaires du listage des scripts SQL."""

from collateral.sql import lister


def test_lister_trie_par_prefixe(tmp_path):
    for nom in ("02_b.sql", "00_a.sql", "10_c.sql"):
        (tmp_path / nom).write_text("SELECT 1;", encoding="utf-8")
    assert [c.name for c in lister(tmp_path)] == ["00_a.sql", "02_b.sql", "10_c.sql"]


def test_lister_ignore_ce_qui_ne_correspond_pas(tmp_path):
    (tmp_path / "00_a.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "brouillon.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "00_a.txt").write_text("", encoding="utf-8")
    assert [c.name for c in lister(tmp_path)] == ["00_a.sql"]


def test_lister_dossier_vide(tmp_path):
    assert lister(tmp_path) == []


def test_lister_plafonne_a_99_scripts(tmp_path):
    """Limite connue : le motif [0-9][0-9]_ ignore silencieusement 100_*.sql"""
    (tmp_path / "100_a.sql").write_text("SELECT 1;", encoding="utf-8")
    assert lister(tmp_path) == []
