"""Unit tests: the suggested weights and "last time" on the Today tab.

Each test puts a few workouts on a fresh phone, then asks the app for one number.
Dates: Mon Nov 16, Wed Nov 18 and Thu Nov 19 2026 are in the same training week; Nov 11 and 12 are the week before.
"""
import pytest

from conftest import workout

WED = "2026-11-18"
THU = "2026-11-19"


@pytest.mark.unit
def test_estimated_max_matches_the_csv_export(open_app):
    # Arrange
    app = open_app("eko", sessions=[])

    # Act
    est = app.call("e1rm", 185, 5)

    # Assert: 185 x 5 is about 216 in the export's est_max_lbs column
    assert round(est) == 216


@pytest.mark.unit
def test_next_week_goes_up_5_but_same_week_stays(open_app):
    # Arrange
    app = open_app("eko", sessions=[])
    this_week = app.call("weekIndex", WED)

    # Act
    after_last_week = app.call("plusFive", {"date": "2026-11-11", "w": 100}, this_week)
    after_monday = app.call("plusFive", {"date": "2026-11-16", "w": 100}, this_week)

    # Assert
    assert after_last_week == 105
    assert after_monday == 100


@pytest.mark.unit
def test_a_skipped_day_does_not_count_for_the_target(open_app):
    # Arrange: abductor done on Nov 4, skipped on Nov 11 (logged as 0 x 0, "Machine broken")
    app = open_app("eko", sessions=[
        workout("2026-11-04", "lowerA", "Lower A", [("Hip abductor machine", [(195, 12), (195, 12), (195, 12)])]),
        workout("2026-11-11", "lowerA", "Lower A", [("Hip abductor machine", [(0, 0), (0, 0), (0, 0)], "Machine broken")]),
    ])

    # Act
    t = app.target("lowerA", "Hip abductor machine", WED)

    # Assert: 195 + 5, not 0 + 5
    assert t["w"] == 200


@pytest.mark.unit
def test_last_time_shows_the_last_day_you_actually_did_it(open_app):
    # Arrange: same as above, the Nov 11 sets are 0 x 0
    app = open_app("eko", sessions=[
        workout("2026-11-04", "lowerA", "Lower A", [("Hip abductor machine", [(195, 12), (195, 12)])]),
        workout("2026-11-11", "lowerA", "Lower A", [("Hip abductor machine", [(0, 0), (0, 0)], "Skipped today")]),
    ])

    # Act
    last = app.call("lastDone", {"name": "Hip abductor machine"}, WED)

    # Assert
    assert last["date"] == "2026-11-04"


@pytest.mark.unit
def test_sets_of_2_reps_or_fewer_do_not_count(open_app):
    # Arrange: an off day at 225 x 2, the real working weight the week before was 205 x 6
    app = open_app("eko", sessions=[
        workout("2026-11-04", "lowerA", "Lower A", [("Leg extension", [(205, 6)])]),
        workout("2026-11-11", "lowerA", "Lower A", [("Leg extension", [(225, 2)])]),
    ])

    # Act
    last = app.call("lastWorking", ["Leg extension"], WED)

    # Assert
    assert last["w"] == 205
    assert last["skip"] == "2026-11-11"


@pytest.mark.unit
@pytest.mark.parametrize("reps, expected", [([12, 12, 11], 35), ([15, 15, 15], 40)])
def test_small_lifts_earn_the_next_5_lbs_with_reps(open_app, reps, expected):
    # Arrange: dumbbell lateral raise, 10-15 reps, done last week at 35 lbs
    app = open_app("eko", sessions=[
        workout("2026-11-12", "upperB", "Upper B", [("DB lateral raise", [(35, r) for r in reps])]),
    ])

    # Act
    t = app.target("upperB", "DB lateral raise", THU)

    # Assert: same weight until every set hits 15, then + 5
    assert t["w"] == expected


@pytest.mark.unit
def test_heavy_bench_chain_monday_to_thursday(open_app):
    # Arrange: Monday's top set was 240 x 3
    app = open_app("eko", sessions=[
        workout("2026-11-12", "upperB", "Upper B", [("Bench press – heavy set", [(235, 3)])]),
        workout("2026-11-16", "upperA", "Upper A", [("Bench press – top set", [(240, 3)])]),
    ])

    # Act
    t = app.target("upperB", "Bench press – heavy set", THU)

    # Assert: Thursday's heavy set is 5 more than the last heavy bench
    assert t["w"] == 245


@pytest.mark.unit
def test_dumbbell_rdl_target_is_per_dumbbell_not_the_barbell_weight(open_app):
    # Arrange: dumbbell RDLs in October (one dumbbell's weight), then barbell RDLs in November
    # (the whole bar), all saved under the old name "Romanian deadlift"
    app = open_app("eko", sessions=[
        workout("2026-10-21", "lowerA", "Lower A", [("Romanian deadlift", [(70, 6), (70, 6)], "Dumbbells this time")]),
        workout("2026-10-28", "lowerA", "Lower A", [("Romanian deadlift", [(75, 6), (75, 6)])]),
        workout("2026-11-04", "lowerA", "Lower A", [("Romanian deadlift", [(135, 6), (135, 6)], "Did this on squat barbell")]),
        workout("2026-11-11", "lowerA", "Lower A", [("Romanian deadlift", [(140, 8), (140, 8)])]),
    ])

    # Act
    t = app.target("lowerA", "DB Romanian deadlift", WED)
    shown = app.box_weight("lowerA", "DB Romanian deadlift", WED)

    # Assert: no 145 lb dumbbells. With no dumbbell RDL under the new name yet, the box starts
    # at the last dumbbell weight he used (75).
    assert t is None or t["w"] < 100
    assert shown == "75"
