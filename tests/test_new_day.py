"""v5.8 fixes, written test-first (red, then green).

The phone keeps the app open in the background, so it often comes back hours later without reloading.
"""
import pytest

from conftest import COPIES, workout

WED = [workout("2026-11-25", "lowerA", "Lower A", [("Squat – top set", [(245, 4)])])]


def come_back(app, when):
    """The phone wakes the app up at this time (Halifax time), without reloading the page."""
    app.page.clock.set_fixed_time(when)
    app.page.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")
    app.page.wait_for_timeout(150)


@pytest.mark.system
@pytest.mark.parametrize("copy", list(COPIES))
def test_today_moves_to_the_new_day_when_the_app_comes_back_the_next_morning(open_app, copy):
    # Arrange: opened on Wednesday for Lower A, then left in the background overnight
    app = open_app(copy, sessions=WED, today="2026-11-25", storage=None if copy == "eko" else {"profile": {"bench": 135, "squat": 135, "start": [2026, 9, 26]}})
    assert app.call("state")["activeKey"] == "lowerA"

    # Act: Thursday morning
    come_back(app, "2026-11-26T09:00:00-04:00")

    # Assert: Thursday is Upper B, with Thursday's date
    assert app.call("state")["activeKey"] == "upperB"
    assert app.page.inner_text("main h1") == "Upper B"
    assert "Thursday, November 26" in app.page.inner_text("main .date")
    assert app.errors == []


@pytest.mark.system
def test_a_rest_day_shows_when_the_app_comes_back_on_saturday(open_app):
    # Arrange: opened on Friday
    app = open_app("eko", sessions=WED, today="2026-11-27")
    assert app.page.inner_text("main h1") == "Lower B"

    # Act
    come_back(app, "2026-11-28T09:00:00-04:00")

    # Assert
    assert app.page.inner_text("main h1") == "Rest day"
    assert app.errors == []


@pytest.mark.system
def test_a_workout_still_going_past_midnight_stays_on_screen(open_app):
    # Arrange: Lower A started late on Wednesday, one set checked
    app = open_app("eko", sessions=[], today="2026-11-25")
    app.page.clock.set_fixed_time("2026-11-25T23:40:00-04:00")
    app.page.locator(".ex.open .set").first.locator('[data-act="check"]').click()

    # Act: still at the gym at 12:20 on Thursday
    come_back(app, "2026-11-26T00:20:00-04:00")

    # Assert: same workout, same date, the set is still checked
    state = app.call("state")
    assert state["activeKey"] == "lowerA"
    assert state["drafts"]["lowerA"]["date"] == "2026-11-25"
    assert app.page.locator(".set.is-done").count() == 1
    assert app.errors == []


@pytest.mark.integration
def test_saving_again_after_undo_is_not_deleted_from_the_sheet(open_app):
    # Arrange: Google Sheet sync on (a fake sheet that remembers what it was told), no signal at the gym
    app = open_app("eko", sessions=[], today="2026-11-25", storage={"cloudUrl": "http://localhost:9/sheet"})
    posts, online = [], [False]

    def sheet(route):
        if not online[0]:
            return route.abort()
        if route.request.method == "POST":
            posts.append(route.request.post_data_json)
        route.fulfill(json={"ok": True, "app": [], "sheet": []})

    app.page.context.route("http://localhost:9/**", sheet)
    page = app.page

    def save():
        page.locator("#finishBtn").click()
        page.locator('[data-act="confirmsave"]').click()
        page.wait_for_timeout(300)

    # Act: log a set and save, undo the save, then save it again
    page.locator(".ex.open .set").first.locator('[data-act="check"]').click()
    save()
    page.locator('[data-act="undo-save"]').click()
    page.wait_for_timeout(300)
    save()
    online[0] = True  # back home with signal: the next sync goes through
    page.evaluate("() => window.__r3p.state().sessions.length")  # app still alive
    page.locator('[data-nav="settings"]').click()
    page.locator('[data-act="cloudsync"]').click()
    page.wait_for_timeout(500)

    # Assert: the workout is saved, and the last thing the sheet heard about it was not "delete"
    wid = "2026-11-25-lowerA"
    assert any(s["id"] == wid for s in app.stored("sessions"))
    last = [p for p in posts if wid in (p.get("ids") or []) or any(s["id"] == wid for s in p.get("sessions") or [])][-1]
    assert last["action"] == "save"


@pytest.mark.integration
def test_unreadable_saved_workouts_are_kept_not_overwritten(open_app):
    # Arrange: the saved workouts on the phone can't be read (a damaged entry)
    app = open_app("eko", sessions=[], today="2026-11-25")
    page = app.page
    page.evaluate("() => localStorage.setItem('r235.sessions', '[{\"id\":\"2026-11-23-upperA\",broken')")
    page.reload()
    page.wait_for_function("() => window.__r3p")

    # Act: something that saves, like logging protein
    page.click('.tabs button[data-tab="food"]')
    page.locator('[data-p="25"]').click()

    # Assert: the damaged entry was copied aside untouched, so it can still be recovered
    kept = page.evaluate("() => localStorage.getItem('r235.sessions.unreadable')")
    assert kept == '[{"id":"2026-11-23-upperA",broken'
