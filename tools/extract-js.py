#!/usr/bin/env python3
"""Copy the app's script out of each index.html into build/ so ESLint can check it.

    python3 tools/extract-js.py      -> build/app.js, build/shayan.js, build/pavle.js
"""
import re
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
out = repo / "build"
out.mkdir(exist_ok=True)
for name, html in [("app", "index.html"), ("shayan", "shayan/index.html"), ("pavle", "pavle/index.html")]:
    text = (repo / html).read_text(encoding="utf-8")
    script = "\n".join(re.findall(r"<script>(.*?)</script>", text, re.S))
    (out / f"{name}.js").write_text(script, encoding="utf-8")
    print("wrote", f"build/{name}.js")
