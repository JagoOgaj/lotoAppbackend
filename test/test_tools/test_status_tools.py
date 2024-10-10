import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.tools import Status


def test_status_values():
    """Teste si les valeurs des statuts sont correctes."""
    assert Status.EN_COUR.value == "EN_COUR"
    assert Status.EN_VALIDATION.value == "EN_VALIDATION"
    assert Status.TERMINE.value == "TERMINE"
    assert Status.SIMULATION.value == "SIMULATION"
    assert Status.SIMULATION_TERMINE.value == "SIMULATION_TERMINE"


def test_status_enum_members():
    """Teste si tous les statuts sont présents dans l'énumération."""
    expected_statuses = [
        Status.EN_COUR,
        Status.EN_VALIDATION,
        Status.TERMINE,
        Status.SIMULATION,
        Status.SIMULATION_TERMINE,
    ]

    assert set(Status) == set(expected_statuses)


def test_status_repr():
    """Teste la représentation des objets Status."""
    assert repr(Status.EN_COUR) == "<Status.EN_COUR: 'EN_COUR'>"
    assert repr(Status.EN_VALIDATION) == "<Status.EN_VALIDATION: 'EN_VALIDATION'>"
    assert repr(Status.TERMINE) == "<Status.TERMINE: 'TERMINE'>"
    assert repr(Status.SIMULATION) == "<Status.SIMULATION: 'SIMULATION'>"
    assert (
        repr(Status.SIMULATION_TERMINE)
        == "<Status.SIMULATION_TERMINE: 'SIMULATION_TERMINE'>"
    )
