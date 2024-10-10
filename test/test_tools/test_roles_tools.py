import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.tools import Roles


def test_roles_values():
    """Teste si les valeurs des rôles sont correctes."""
    assert Roles.ADMIN.value == "ADMIN"
    assert Roles.USER.value == "USER"
    assert Roles.FAKE.value == "FAKE"


def test_roles_enum_members():
    """Teste si tous les rôles sont présents dans l'énumération."""
    expected_roles = [Roles.ADMIN, Roles.USER, Roles.FAKE]

    assert set(Roles) == set(expected_roles)


def test_roles_repr():
    """Teste la représentation des objets Roles."""
    assert repr(Roles.ADMIN) == "<Roles.ADMIN: 'ADMIN'>"
    assert repr(Roles.USER) == "<Roles.USER: 'USER'>"
    assert repr(Roles.FAKE) == "<Roles.FAKE: 'FAKE'>"
