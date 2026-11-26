"""Stats tab (v5.9): read-only numbers from what's saved on the phone."""
import pytest

from conftest import COPIES, workout

WEEKS = [
    workout("2026-11-16", "upperA", "Upper A", [("Bench press – top set", [(240, 3)]), ("Pull-ups", [(45, 8)]), ("Barbell / EZ-bar curl", [(70, 6), (70, 6)])]),
    workout("2026-11-18", "lowerA", "Lower A", [("Squat – top set", [(225, 4)]), ("Hip abductor machine", [(0, 0), (0, 0)], "Skipped")]),
    workout("2026-11-19", "upperB", "Upper B", [("Bench press – heavy set", [(245, 2)]), ("Lat pulldown", [(192, 8)])]),
    workout("2026-11-20", "lowerB", "Lower B", [("Seated calf raise", [(125, 20)]), ("Cable crunch", [(88, 12)])]),
    workout("2026-11-23", "upperA", "Upper A", [("Bench press – top set", [(245, 3)]), ("Tricep pushdown", [(88, 10)])]),
]


@pytest.mark.unit
@pytest.mark.parametrize("name, muscle", [
    ("Bench press – top set", "Chest"), ("Weighted dips", "Chest"), ("Low-to-high cable fly", "Chest"),
    ("Close-grip seated cable row", "Back"), ("Chest-supported / machine row", "Back"), ("Lat pull down", "Back"),
    ("Back extension (hyperextension)", "Back"), ("DB shrug", "Back"), ("Pull-ups", "Back"),
    ("Reverse pec deck", "Shoulders"), ("DB lateral raise", "Shoulders"), ("Rope face pull", "Shoulders"), ("DB shoulder press", "Shoulders"),
    ("Behind-the-body cable curl", "Biceps"), ("Hammer curl", "Biceps"),
    ("Overhead cable extension", "Triceps"), ("EZ-bar incline skull crusher", "Triceps"),
    ("Seated leg curl", "Legs"), ("Leg extension", "Legs"), ("Hip adductor machine", "Legs"), ("Romanian deadlift", "Legs"),
    ("Seated calf raise", "Calves"), ("Decline sit-up", "Abs"), ("Dragon fly abs flat", "Abs"),
])
def test_each_exercise_counts_for_the_right_muscle(open_app, name, muscle):
    app = open_app("eko", sessions=[])
    assert app.call("muscleOf", name) == muscle


@pytest.mark.unit
def test_totals_skip_0x0_sets_and_add_up_weight_moved(open_app):
    # Arrange
    app = open_app("eko", sessions=WEEKS, today="2026-11-26")

    # Act: the week of Nov 16 to Nov 22
    t = app.call("statTotals", "2026-11-16", "2026-11-22")

    # Assert: 9 sets with reps (the two 0 x 0 abductor sets don't count)
    assert t["workouts"] == 4
    assert t["sets"] == 9
    assert t["vol"] == 240 * 3 + 45 * 8 + 70 * 6 * 2 + 225 * 4 + 245 * 2 + 192 * 8 + 125 * 20 + 88 * 12


@pytest.mark.unit
def test_showing_up_counts_weeks_in_a_row_and_full_weeks(open_app):
    # Arrange: all 4 done the week of Nov 16, 1 so far this week
    app = open_app("eko", sessions=WEEKS, today="2026-11-26", storage={"profile": None})

    # Act
    su = app.call("showingUp", "2026-11-26")

    # Assert
    assert su["thisWeek"] == 1
    assert su["fullInRow"] == 1
    assert su["inRow"] == 2  # last week and this week
    assert {p["name"]: p["done"] for p in su["per"]}["Upper A"] == 1


@pytest.mark.unit
def test_sets_per_muscle_this_week(open_app):
    app = open_app("eko", sessions=WEEKS, today="2026-11-26")
    ms = app.call("muscleSets", "2026-11-16", "2026-11-22")
    # bench 240 x 3 and 245 x 2 (a set, even if it doesn't move the target); the 0 x 0 abductor sets don't count
    assert ms == {"Chest": 2, "Back": 2, "Shoulders": 0, "Biceps": 2, "Triceps": 0, "Legs": 1, "Calves": 1, "Abs": 1}


@pytest.mark.unit
def test_latest_bests_only_count_sets_of_3_reps_or_more(open_app):
    app = open_app("eko", sessions=WEEKS, today="2026-11-26")
    bests = {b["name"]: b for b in app.call("recentBests", 20)}
    assert bests["Bench press"]["w"] == 245 and bests["Bench press"]["r"] == 3  # not the 245 x 2
    assert "Pull-ups" not in bests  # bodyweight lifts have no estimated max


@pytest.mark.system
@pytest.mark.parametrize("copy", list(COPIES))
def test_stats_tab_opens_in_every_copy_and_changes_nothing(open_app, copy):
    # Arrange
    storage = {"profile": {"bench": 155, "squat": 185, "start": [2026, 9, 26], "joined": "2026-11-16"}} if copy != "eko" else None
    app = open_app(copy, sessions=WEEKS, today="2026-11-26", storage=storage)
    before = app.stored("sessions")

    # Act: open Stats and go through every range
    app.page.click('.tabs button[data-tab="stats"]')
    for rng in ("12w", "all", "4w"):
        app.page.click(f'[data-sr="{rng}"]')
        app.page.wait_for_timeout(250)
    body = app.page.inner_text("main")

    # Assert
    for heading in ("Stats", "Every week", "Showing up", "Sets per muscle", "Getting stronger", "Latest bests", "Body and food"):
        assert heading in body, heading
    assert app.stored("sessions") == before
    assert app.errors == []


@pytest.mark.system
def test_stats_with_nothing_logged_says_so(open_app):
    app = open_app("eko", sessions=[], today="2026-11-26")
    app.page.click('.tabs button[data-tab="stats"]')
    assert "Nothing logged yet" in app.page.inner_text("main")
    assert app.errors == []


@pytest.mark.unit
def test_vs_before_compares_the_same_days_not_a_half_done_week_with_a_full_one(open_app):
    app = open_app("eko", sessions=[], today="2026-11-26")
    sp = app.call("statSpan", "4w", "2026-11-26")
    assert (sp["from"], sp["to"]) == ("2026-11-02", "2026-11-26")
    assert (sp["prevFrom"], sp["prevTo"]) == ("2026-10-05", "2026-10-29")
