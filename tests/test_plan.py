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
