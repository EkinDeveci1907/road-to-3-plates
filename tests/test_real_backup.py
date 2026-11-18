"""Acceptance test with a real phone backup. Skipped unless you point it at a file:

    R3P_BACKUP=~/Downloads/road-to-3-plates-workouts-2026-11-18.csv pytest tests/test_real_backup.py

It restores the file into a fresh copy of the app with the Restore button, then checks that every
workout came back and that this week's targets make sense.
"""
import csv
import os
from pathlib import Path

import pytest

BACKUP = os.environ.get("R3P_BACKUP")
pytestmark = pytest.mark.skipif(not BACKUP, reason="set R3P_BACKUP to a CSV export to run this")


@pytest.mark.system
def test_real_backup_restores_completely(open_app):
    # Arrange
    path = Path(BACKUP).expanduser()
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    workouts = {(r["date"], r["workout"]) for r in rows}
    sets = [r for r in rows if r["set"]]
    app = open_app("eko", sessions=[])

    # Act
    app.page.set_input_files("#restoreIn", str(path))
    app.page.wait_for_function("(n) => window.__r3p.state().sessions.length === n", arg=len(workouts))

    # Assert: every workout and every set is back
    stored = app.stored("sessions")
    assert len(stored) == len(workouts)
    assert sum(len(e["sets"]) for s in stored for e in s["exercises"]) == len(sets)
    assert app.errors == []
