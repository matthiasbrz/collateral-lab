"""Tests unitaires de la livraison simulee : la majoration garde le format du fichier."""

from collateral.simulation import majorer


def test_majorer_garde_les_decimales():
    assert majorer("108000.50") == "118800.55"


def test_majorer_garde_un_entier_entier():
    assert majorer("396000") == "435600"
