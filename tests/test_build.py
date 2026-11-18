"""Build tests: the friends' copies and the files a phone downloads."""
import re
import shutil
import subprocess

import pytest

from conftest import REPO, build_friend

FRIENDS_IN_THIS_REPO = [("Shayan", "shy", "shy", "shayan"), ("Pavle", "pav", "pav", "pavle")]


def sw_number(path):
    return int(re.search(r"const VERSION = '[a-z0-9]+-v(\d+)';", path.read_text()).group(1))


@pytest.mark.build
@pytest.mark.parametrize("name, prefix, cache, folder", FRIENDS_IN_THIS_REPO)
def test_friend_copies_are_rebuilt_from_the_latest_index_html(tmp_path, name, prefix, cache, folder):
    # Act: build the copy fresh
    build_friend(name, prefix, cache, tmp_path)

    # Assert: what's committed is exactly what the build makes (so nobody forgot to rebuild)
    for f in ("index.html", "sw.js", "manifest.webmanifest"):
        assert (tmp_path / f).read_text() == (REPO / folder / f).read_text(), f"{folder}/{f} is out of date"


@pytest.mark.build
def test_building_twice_gives_the_same_files(tmp_path):
    build_friend("Shayan", "shy", "shy", tmp_path / "a")
    build_friend("Shayan", "shy", "shy", tmp_path / "b")
    assert (tmp_path / "a" / "sw.js").read_text() == (tmp_path / "b" / "sw.js").read_text()


@pytest.mark.build
@pytest.mark.parametrize("folder", ["shayan", "pavle"])
def test_friend_service_worker_version_follows_the_main_one(folder):
    assert sw_number(REPO / folder / "sw.js") == sw_number(REPO / "sw.js")


@pytest.mark.build
@pytest.mark.parametrize("folder", ["shayan", "pavle"])
def test_friend_copies_have_none_of_ekos_data(folder):
    html = (REPO / folder / "index.html").read_text()
    assert "Eko" not in html
    assert "var OLD_LOGS=[];" in html
    assert "r235" not in html


@pytest.mark.build
@pytest.mark.parametrize("folder", [".", "shayan", "pavle"])
def test_the_app_script_has_no_syntax_errors(tmp_path, folder):
    if not shutil.which("node"):
        pytest.skip("node is not installed")
    html = (REPO / folder / "index.html").read_text()
    script = "\n".join(re.findall(r"<script>(.*?)</script>", html, re.S))
    (tmp_path / "app.js").write_text(script)
    subprocess.run(["node", "--check", str(tmp_path / "app.js")], check=True)


@pytest.mark.build
def test_offline_files_all_exist():
    # Assert: every file the service worker saves for offline use is really in the repo
    sw = (REPO / "sw.js").read_text()
    shell = re.findall(r"'\./([^']*)'", re.search(r"const SHELL = \[(.*?)\];", sw).group(1))
    for f in shell:
        assert f == "" or (REPO / f).exists(), f
