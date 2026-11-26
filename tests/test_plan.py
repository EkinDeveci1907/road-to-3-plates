"""Unit tests: the weekly plan itself (which exercises are on which day)."""
import pytest


def names(app, key):
    return app.page.evaluate("(k) => window.__r3p.workout(k).ex.map(x => x.name)", key)


def exercise(app, key, name):
    return app.page.evaluate("([k, n]) => window.__r3p.workout(k).ex.find(x => x.name === n)", [key, name])


@pytest.mark.unit
def test_thursday_has_the_low_to_high_cable_fly_after_dips(open_app):
    # Arrange
    app = open_app("eko", sessions=[])

    # Act
    thursday = names(app, "upperB")

    # Assert: chest finishes with the fly right after the last press
    assert "Low-to-high cable fly" in thursday
    assert thursday.index("Low-to-high cable fly") == thursday.index("Weighted dips") + 1


@pytest.mark.unit
def test_thursday_hammer_curl_is_now_the_bayesian_curl(open_app):
    # Arrange
    app = open_app("eko", sessions=[])

    # Act
    thursday = names(app, "upperB")

    # Assert: same exercise name as Monday's, so both days share one history
    assert "Hammer curl" not in thursday
    assert "Behind-the-body cable curl" in thursday
    assert "Bayesian" in exercise(app, "upperB", "Behind-the-body cable curl")["label"]


@pytest.mark.unit
def test_monday_cable_fly_is_two_sets(open_app):
    app = open_app("eko", sessions=[])
    assert exercise(app, "upperA", "Cable fly")["sets"] == 2


@pytest.mark.unit
def test_every_exercise_has_sets_reps_and_rest(open_app):
    # Arrange
    app = open_app("eko", sessions=[])

    # Act
    plan = app.page.evaluate("() => ['upperA','lowerA','upperB','lowerB'].map(k => window.__r3p.workout(k))")

    # Assert: four days, and every exercise (except bench and squat, which work theirs out) is complete
    assert [d["day"] for d in plan] == ["Mon", "Wed", "Thu", "Fri"]
    for day in plan:
        for ex in day["ex"]:
            assert ex["rest"] > 0, ex["name"]
            if not ex.get("kind"):
                assert ex["sets"] >= 1 and ex["reps"], ex["name"]


@pytest.mark.unit
@pytest.mark.parametrize("copy", ["eko", "ahmed", "shayan", "pavle"])
def test_friday_bulgarian_split_squat_is_now_the_barbell_lunge(open_app, copy):
    # Arrange
    app = open_app(copy, sessions=[], storage=None if copy == "eko" else {"profile": {"bench": 135, "squat": 135, "start": [2026, 9, 26]}})

    # Act
    friday = names(app, "lowerB")

    # Assert: same spot in Friday's order, and the split squat is still one tap away as a swap
    assert "Bulgarian split squat (per leg)" not in friday
    assert friday.index("Barbell lunge") == friday.index("Hip thrust") - 1
    assert "Bulgarian split squat (per leg)" in app.page.evaluate("() => window.__r3p.swaps('Barbell lunge')")


@pytest.mark.unit
def test_barbell_lunge_does_not_carry_on_from_split_squat_numbers(open_app):
    # Arrange: split squats were logged as one dumbbell; a barbell lunge is the whole bar
    from conftest import workout
    app = open_app("eko", sessions=[workout("2026-11-20", "lowerB", "Lower B", [("Bulgarian split squat (per leg)", [(60, 8), (60, 8)])])], today="2026-11-27")

    # Act
    target = app.target("lowerB", "Barbell lunge", "2026-11-27")

    # Assert: no suggested weight from the 60 lb dumbbells; the first time you pick it
    assert target is None


@pytest.mark.system
def test_logging_barbell_lunges_on_friday(open_app):
    # Arrange: Friday
    app = open_app("eko", sessions=[], today="2026-11-27")
    page = app.page
    card = page.locator(".ex", has_text="Barbell lunge").first

    # Act: open the card, log 95 x 8, save
    card.locator(".ex__head").click()
    row = card.locator(".set").first
    row.locator('input[data-f="w"]').fill("95")
    row.locator('input[data-f="r"]').fill("8")
    row.locator('[data-act="check"]').click()
    page.locator("#finishBtn").click()
    page.locator('[data-act="confirmsave"]').click()
    page.locator("#toastMsg", has_text="Lower B saved").wait_for()

    # Assert
    saved = [s for s in app.stored("sessions") if s["id"] == "2026-11-27-lowerB"][0]
    lunge = [e for e in saved["exercises"] if e["name"] == "Barbell lunge"][0]
    assert lunge["sets"][0] == {"w": 95, "r": 8}
    assert app.errors == []
