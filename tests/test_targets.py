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
def test_wednesday_rdl_is_barbell_and_carries_on_from_the_barbell_numbers(open_app):
    # Arrange: barbell RDLs on Nov 4 and Nov 11 (the whole bar), dumbbell ones before that
    app = open_app("eko", sessions=[
        workout("2026-10-28", "lowerA", "Lower A", [("Romanian deadlift", [(75, 6), (75, 6)], "Dumbbells this time")]),
        workout("2026-11-04", "lowerA", "Lower A", [("Romanian deadlift", [(135, 6), (135, 6)], "Did this on squat barbell")]),
        workout("2026-11-11", "lowerA", "Lower A", [("Romanian deadlift", [(140, 8), (140, 8)])]),
    ])

    # Act
    wednesday = app.page.evaluate("() => window.__r3p.workout('lowerA').ex.map(x => x.name)")
    t = app.target("lowerA", "Romanian deadlift", WED)

    # Assert: straps now, so it's the barbell RDL right after squats, at 140 + 5
    assert "DB Romanian deadlift" not in wednesday
    assert wednesday.index("Romanian deadlift") == wednesday.index("Squat – back-off sets") + 1
    assert t["w"] == 145


MON_NOV_23 = "2026-11-23"


@pytest.mark.unit
def test_eko_has_no_deload_week(open_app):
    # Arrange: Monday 240 x 3, then 245 x 2 on Thursday (2 reps, doesn't count), back-offs 205, rows 115
    app = open_app("eko", today=MON_NOV_23, sessions=[
        workout("2026-11-16", "upperA", "Upper A", [
            ("Bench press – top set", [(240, 3)]),
            ("Bench press – back-off sets", [(205, 6), (205, 6), (205, 6)]),
            ("Barbell row", [(115, 10), (115, 10)]),
        ]),
        workout("2026-11-19", "upperB", "Upper B", [("Bench press – heavy set", [(245, 2)])]),
    ])

    # Act
    top = app.target("upperA", "Bench press – top set", MON_NOV_23)
    back = app.page.evaluate("""(d) => { const t = window.__r3p;
        const ex = t.workout('upperA').ex.find(x => x.name === 'Bench press – back-off sets');
        return t.resolveEx(ex, t.weekIndex(d), d); }""", MON_NOV_23)
    row = app.target("upperA", "Barbell row", MON_NOV_23)
    body = app.page.inner_text("body")

    # Assert: a normal week, every lift up 5 from the last one that counted, full sets
    assert top["w"] == 245
    assert back["w"] == 210 and back["sets"] == 3
    assert row["w"] == 120
    assert "Deload" not in body and "deload" not in body


@pytest.mark.unit
@pytest.mark.parametrize("copy", ["shayan", "pavle", "ahmed"])
def test_friends_have_no_deload_week_either(open_app, copy):
    # Arrange
    app = open_app(copy, sessions=[])

    # Act: Barbell row in week 9 of their block (week index 8), where the deload used to be
    row = app.page.evaluate("""() => { const t = window.__r3p;
        const ex = t.workout('upperA').ex.find(x => x.name === 'Barbell row');
        return t.resolveEx(ex, 8, '2027-03-01'); }""")

    # Assert: full sets, no deload hint
    assert row["sets"] == 3
    assert "Deload" not in row["hint"]
