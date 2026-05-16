"""Sanity checks on probe loading.

Owner: Dhanush. See ROLES.md.
"""

from slowburn.probes import ALL_PROBES, PROBES_BY_NAME


def test_all_probes_load():
    assert len(ALL_PROBES) == 5


def test_probe_names_unique():
    names = [p.name for p in ALL_PROBES]
    assert len(names) == len(set(names))


def test_registry_matches_list():
    assert set(PROBES_BY_NAME) == {p.name for p in ALL_PROBES}


def test_every_probe_has_rubric():
    for p in ALL_PROBES:
        assert p.rubric.strip(), f"{p.name} missing rubric"
        assert p.messages, f"{p.name} missing messages"
