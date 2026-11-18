"""Integration tests: backups, the CSV export, and restoring them.

Keeping everyone's numbers is the most important thing in this app, so these check that a backup
always brings workouts back and never wipes or duplicates what's already on the phone.
"""
import json

import pytest

from conftest import workout

TRICKY = [
    workout("2026-11-12", "upperB", "Upper B", [
        ("Bench press – heavy set", [(235, 3)], 'felt "easy", go up'),
        ("Lat pulldown", [(187, 8), (126, 12)], "Forgot the straps, half assed\nfirst set"),
        ("Weighted dips", [(45, 10), (45, 8)], "=dumbbell this time"),
        ("Pull-ups", [(None, 10)]),
    ]),
    workout("2026-09-16", "old", "Arms + shoulders (old plan)", [("Dips", [(0, 10), (30, 15)], "Go harder next time")]),
]


def short(sessions):
    """The parts of each workout that must survive a round trip: date, title, exercises, sets, notes."""
    out = {}
    for s in sessions:
        out[s["date"] + " " + s["title"]] = [(e["name"], [(x["w"], x["r"]) for x in e["sets"]], e.get("note") or "")
                                              for e in s["exercises"]]
    return out


@pytest.mark.integration
def test_csv_export_reads_back_exactly(open_app):
    # Arrange
    app = open_app("eko", sessions=TRICKY)

    # Act
    csv_text = app.call("toCsv")
    back = app.call("sessionsFromCsv", csv_text)

    # Assert: commas, quotes, line breaks and a note starting with "=" all come back the same
    assert short(back) == short(TRICKY)


@pytest.mark.integration
def test_restoring_a_csv_only_adds_missing_workouts(open_app):
    # Arrange: the phone has Nov 12 (edited after the export) but lost Sept 16
    phone_copy = workout("2026-11-12", "upperB", "Upper B", [("Bench press – heavy set", [(240, 3)])], saved_at=99)
    app = open_app("eko", sessions=TRICKY)
    csv_text = app.call("toCsv")
    app = open_app("eko", sessions=[phone_copy])

    # Act
    added = app.call("mergeSessions", app.call("sessionsFromCsv", csv_text), True)
    again = app.call("mergeSessions", app.call("sessionsFromCsv", csv_text), True)
    now = app.page.evaluate("() => window.__r3p.state().sessions")

    # Assert: Sept 16 came back, the phone's newer Nov 12 was kept, and restoring twice adds nothing
    assert added == 1
    assert again == 0
    assert len(now) == 2
    nov12 = [s for s in now if s["date"] == "2026-11-12"][0]
    assert nov12["exercises"][0]["sets"][0]["w"] == 240


@pytest.mark.integration
def test_restoring_a_json_backup_keeps_the_newer_copy(open_app):
    # Arrange
    older = workout("2026-11-12", "upperB", "Upper B", [("Lat pulldown", [(170, 10)])], saved_at=5)
    newer = workout("2026-11-12", "upperB", "Upper B", [("Lat pulldown", [(187, 8)])], saved_at=9)
    extra = workout("2026-11-13", "lowerB", "Lower B", [("Hip thrust", [(375, 8)])], saved_at=5)
    app = open_app("eko", sessions=[newer])

    # Act
    added = app.call("mergeSessions", [older, extra], False)
    now = app.page.evaluate("() => window.__r3p.state().sessions")

    # Assert
    assert added == 1
    assert {s["date"]: s["exercises"][0]["sets"][0]["w"] for s in now} == {"2026-11-12": 187, "2026-11-13": 375}


@pytest.mark.integration
@pytest.mark.parametrize("kind", ["csv", "json"])
def test_restore_button_takes_both_backup_files(open_app, tmp_path, kind):
    # Arrange: make the file the way the phone does, then open a fresh copy of the app
    app = open_app("eko", sessions=TRICKY)
    if kind == "csv":
        text = app.call("toCsv")
    else:
        text = json.dumps({"app": "road-to-235", "version": 3, "sessions": TRICKY, "bw": [], "checks": {}})
    path = tmp_path / f"road-to-3-plates-backup.{kind}"
    path.write_text(text, encoding="utf-8")
    fresh = open_app("eko", sessions=[])

    # Act
    fresh.page.set_input_files("#restoreIn", str(path))
    fresh.page.wait_for_function("() => window.__r3p.state().sessions.length === 2")

    # Assert: both workouts are back and saved on the phone
    assert len(fresh.stored("sessions")) == 2
    assert "2 workouts added" in fresh.page.inner_text("body")
    assert fresh.errors == []
