"""Shared setup for every test.

The tests run the real app in a headless Chrome at iPhone size. A small local web server serves the
files laid out the same way GitHub Pages does:

    /road-to-3-plates/          Eko's copy (this repo)
    /road-to-3-plates/shayan/   Shayan's copy
    /road-to-3-plates/pavle/    Pavle's copy
    /Ahmed/                     Ahmed's copy, built fresh from index.html with tools/make-friend.py
    /3-plates/                  Ahmed's old link, built the same way

Each page is opened with window.R3P_TEST set, so the app hands the tests its functions (see the end
of index.html). On a phone that is never set, so it does nothing there.
"""
import datetime
import functools
import http.server
import json
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent

# copy name -> (folder on the site, storage prefix)
COPIES = {
    "eko": ("road-to-3-plates/", "r235"),
    "ahmed": ("Ahmed/", "tpf"),
    "ahmed-old-link": ("3-plates/", "tpf"),
    "shayan": ("road-to-3-plates/shayan/", "shy"),
    "pavle": ("road-to-3-plates/pavle/", "pav"),
}

IPHONE = {"viewport": {"width": 390, "height": 844}, "device_scale_factor": 2, "is_mobile": True, "has_touch": True}


def build_friend(name, prefix, cache, out_dir, old_link=False):
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "tools/make-friend.py", name, prefix, cache,
           str(out_dir / "index.html"), str(out_dir / "sw.js"), str(out_dir / "manifest.webmanifest")]
    if old_link:
        cmd.append("--old-link")
    subprocess.run(cmd, cwd=REPO, check=True, capture_output=True)
    for icon in REPO.glob("icon-*.png"):
        shutil.copy(icon, out_dir)


@pytest.fixture(scope="session")
def site(tmp_path_factory):
    root = tmp_path_factory.mktemp("site")
    shutil.copytree(REPO, root / "road-to-3-plates",
                    ignore=shutil.ignore_patterns(".git", "node_modules", "tests", "__pycache__", ".pytest_cache"))
    build_friend("Ahmed", "tpf", "ahm", root / "Ahmed", old_link=True)
    build_friend("Ahmed", "tpf", "tpf", root / "3-plates", old_link=True)
    return root


@pytest.fixture(scope="session")
def base_url(site):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=str(site))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}/"
    server.shutdown()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


class App:
    """One copy of the app open in a fresh browser tab, with its own empty phone storage."""

    def __init__(self, page, prefix):
        self.page = page
        self.prefix = prefix
        self.errors = []
        page.on("pageerror", lambda e: self.errors.append(str(e)))

    def call(self, fn, *args):
        """Run one of the app's own functions with these arguments and give back the result."""
        return self.page.evaluate("([fn, args]) => window.__r3p[fn](...args)", [fn, list(args)])

    def stored(self, key):
        raw = self.page.evaluate("(k) => localStorage.getItem(k)", f"{self.prefix}.{key}")
        return json.loads(raw) if raw else None

    def target(self, day_key, name, date):
        """The suggested weight the Today tab shows for one exercise on that date."""
        return self.page.evaluate(
            """([k, n, d]) => {
                const t = window.__r3p;
                const ex = t.workout(k).ex.find(x => x.name === n);
                const rex = t.resolveEx(ex, t.weekIndex(d), d);
                if (rex.w != null) return {w: rex.w, why: rex.hint};
                const rec = t.recommend(rex, d);
                return rec ? {w: rec.w, why: rec.why} : null;
            }""",
            [day_key, name, date],
        )

    def box_weight(self, day_key, name, date):
        """The weight already filled in (grey) in the weight box for set 1."""
        return self.page.evaluate(
            """([k, n, d]) => {
                const t = window.__r3p;
                const ex = t.workout(k).ex.find(x => x.name === n);
                return t.phWeight(t.resolveEx(ex, t.weekIndex(d), d), d);
            }""",
            [day_key, name, date],
        )


@pytest.fixture
def open_app(browser, base_url):
    """open_app(copy, sessions=None, today=...) opens a copy of the app on a given day.

    sessions: workouts already on the phone. None means a first open (Eko's copy then loads its
    built-in September history, a friend's copy shows the setup screen).
    """
    contexts = []

    def _open(copy="eko", sessions=None, today="2026-11-18", storage=None):
        folder, prefix = COPIES[copy]
        ctx = browser.new_context(**IPHONE)
        contexts.append(ctx)
        # exercise photos come from GitHub; the tests don't need them
        ctx.route("https://raw.githubusercontent.com/**", lambda route: route.abort())
        page = ctx.new_page()
        app = App(page, prefix)
        page.clock.set_fixed_time(datetime.datetime.fromisoformat(today + "T10:00:00"))
        seed = dict(storage or {})
        if sessions is not None:
            seed.update({"sessions": sessions, "seeded": True, "seedv": 2})
        page.add_init_script(
            "window.R3P_TEST = (api) => { window.__r3p = api; };\n"
            + "".join(f"localStorage.setItem({json.dumps(prefix + '.' + k)}, {json.dumps(json.dumps(v))});\n"
                      for k, v in seed.items())
        )
        page.goto(base_url + folder)
        page.wait_for_function("() => window.__r3p")
        return app

    yield _open
    for ctx in contexts:
        ctx.close()


def workout(date, key, title, exercises, saved_at=1):
    """A saved workout the way the app stores it.

    exercises: list of (name, [(weight, reps), ...]) or (name, sets, note).
    """
    out = []
    for e in exercises:
        name, sets = e[0], e[1]
        note = e[2] if len(e) > 2 else ""
        out.append({"name": name, "sets": [{"w": w, "r": r} for w, r in sets], "note": note})
    return {"id": f"{date}-{key}", "date": date, "key": key, "title": title, "plan": "new",
            "exercises": out, "savedAt": saved_at}
