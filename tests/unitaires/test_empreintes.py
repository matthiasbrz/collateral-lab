import pytest

from collateral.empreintes import EmpreinteInattendue, calculer, lire_attendues, verifier

VIDE = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_empreinte_d_un_fichier_vide(tmp_path):
    f = tmp_path / "vide.csv"
    f.write_bytes(b"")
    assert calculer(f) == VIDE


def test_empreinte_differente_echoue_avec_la_consigne(tmp_path):
    f = tmp_path / "vide.csv"
    f.write_bytes(b"")
    with pytest.raises(EmpreinteInattendue, match="Nouvelle livraison DVF probable"):
        verifier(f, {"vide.csv": "0" * 64})


def test_declaration_en_majuscules_acceptee(tmp_path):
    f = tmp_path / "vide.csv"
    f.write_bytes(b"")
    decl = tmp_path / "empreintes.txt"
    decl.write_text(f"{VIDE.upper()} vide.csv\n", encoding="ascii")
    verifier(f, lire_attendues(decl))
