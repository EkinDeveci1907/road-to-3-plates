"""System tests: every copy of the app, used the way a phone uses it."""
import pytest

from conftest import COPIES, workout


@pytest.mark.system
@pytest.mark.parametrize("copy", list(COPIES))
def test_every_copy_opens_without_errors(open_app, copy):
    # Act: first open, nothing saved yet
    app = open_app(copy)

    # Assert
    body = app.page.inner_text("body")
    assert app.errors == []
    if copy == "eko":
        assert "Lower A" in body  # Wednesday's workout
    else:
        name = "Ahmed" if copy.startswith("ahmed") else copy.capitalize()
        assert name in app.page.title()
        assert "Eko" not in body


@pytest.mark.system
def test_each_person_only_sees_their_own_workouts(open_app, base_url):
    # Arrange: all copies live on the same website, so they share one phone storage
    app = open_app("eko", sessions=[workout("2026-11-16", "upperA", "Upper A", [("Barbell row", [(120, 8)])])])

    # Act
    for copy in ("shayan", "pavle", "ahmed"):
        folder, prefix = COPIES[copy]
        app.page.goto(base_url + folder)
        app.page.wait_for_function("() => window.__r3p")
        theirs = app.page.evaluate("() => window.__r3p.state().sessions.length")

        # Assert
        assert theirs == 0, copy
    assert len(app.stored("sessions")) == 1  # Eko's are still there


@pytest.mark.system
def test_log_a_set_save_and_it_is_still_there_after_reopening(open_app):
    # Arrange: Wednesday, Lower A
    app = open_app("eko", sessions=[workout("2026-11-11", "lowerA", "Lower A", [("Squat – top set", [(215, 4)])])])
    page = app.page

    # Act: type 220 x 4 into the first squat set, tick it, finish and save
    first = page.locator(".ex.open .set").first
    first.locator('input[data-f="w"]').fill("220")
    first.locator('input[data-f="r"]').fill("4")
    first.locator('[data-act="check"]').click()
    page.locator("#finishBtn").click()
    page.get_by_role("button", name="Save workout").click()
    page.locator("#toastMsg", has_text="Lower A saved").wait_for()
    page.reload()
    page.wait_for_function("() => window.__r3p")

    # Assert
    saved = [s for s in app.stored("sessions") if s["id"] == "2026-11-18-lowerA"]
    assert len(saved) == 1
    squat = saved[0]["exercises"][0]
    assert squat["name"] == "Squat – top set"
    assert squat["sets"][0] == {"w": 220, "r": 4}
    assert app.errors == []


@pytest.mark.system
def test_an_update_never_touches_saved_workouts(open_app):
    # Arrange: a phone that already has workouts from older versions, including the old-plan ones
    before = [
        workout("2026-09-16", "old", "Arms + shoulders (old plan)", [("Dips", [(0, 10), (30, 15)], "Go harder next time")]),
        workout("2026-11-16", "upperA", "Upper A", [("Bench press – top set", [(240, 3)]), ("Pull-ups", [(45, 8)])]),
    ]

    # Act: open the new version
    app = open_app("eko", sessions=before)

    # Assert: byte for byte the same workouts
    assert app.stored("sessions") == before
    assert app.errors == []
