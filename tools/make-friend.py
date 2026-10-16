#!/usr/bin/env python3
"""Build a friend's copy of the app from this repo's index.html.

Every copy is the same code. A friend's build differs only in the name at the top, its own
storage prefix (so two people on the same phone never mix numbers), a setup screen on first
open instead of Eko's pre-loaded numbers and logs, and its own service-worker cache name.

    python3 tools/make-friend.py Ahmed  tpf ahm ../ahmed/index.html  ../ahmed/sw.js  ../ahmed/manifest.webmanifest --old-link
    python3 tools/make-friend.py Shayan shy shy shayan/index.html    shayan/sw.js    shayan/manifest.webmanifest
"""
import re
import sys

name, prefix, cache, out_html, out_sw, out_manifest = sys.argv[1:7]
old_link = '--old-link' in sys.argv[7:]
slug = name.lower()
s = open('index.html', encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f'make-friend: expected {count} of {old[:80]!r}, found {n}')
    s = s.replace(old, new)


def rep_re(pattern, new):
    global s
    s, n = re.subn(pattern, new, s, count=1, flags=re.S)
    if n != 1:
        sys.exit(f'make-friend: pattern not found: {pattern[:80]!r}')


# ---- name ----
rep('<title>Road to 3 Plates</title>', f'<title>{name}’s Road to 3 Plates</title>')
rep('<p class="brand">Road to 3 Plates</p>', f'<p class="brand">{name}’s Road to 3 Plates</p>')

# ---- who this build is for: setup screen on first open, no pre-loaded numbers ----
rep_re(r"var P;var CFG=\{owner:'Eko'.*?\};\n",
       "var P;var CFG={owner:'%s',prefix:'%s',setup:true,bench:135,squat:135,bwGoal:155,heightIn:68,age:22,start:null,bestBench:null,seed:false};\n" % (name, prefix))

# ---- Eko's own history and starting weights stay out of a friend's build ----
rep_re(r"var START_W=\{.*?\};\nvar OLD_LOGS=\[\n.*?\n\];\n", "var START_W={};\nvar OLD_LOGS=[];\n")
rep(",hint:'Start with the 60 lb dumbbells and keep your form clean.'}", "}")
rep(",hint:'Start at +30 lbs.'}", "}")
rep("'Horizontal calf raise'", "'Horizontal calf raise'")  # sanity: media table is shared and unchanged

# ---- his own file names ----
rep("'road-to-3-plates-workouts-'", f"'{slug}-workouts-'")
rep("'road-to-3-plates-backup-'", f"'{slug}-backup-'")

# ---- Ahmed's old link tells him where the new one is ----
if old_link:
    rep("aria-label=\"Dismiss tip\">×</button></div>';\n",
        "aria-label=\"Dismiss tip\">×</button></div>';\n"
        "  if(location.pathname.indexOf('/3-plates/')===0)h+='<div class=\"tip\"><p>Your app has a new link: <a href=\"https://ekindeveci1907.github.io/Ahmed/\" style=\"color:inherit\"><b>ekindeveci1907.github.io/Ahmed</b></a>. To move your workouts, open Settings (the gear at the top), tap <b>Back up now</b> and save the file. Then open the new link in Safari, add it to your Home Screen, and tap <b>Restore</b>.</p></div>';\n")

assert "r235" not in s, 'an r235 key slipped through'
assert "Eko" not in s, 'Eko-specific text slipped through'
open(out_html, 'w', encoding='utf-8').write(s)

# ---- service worker: own cache name, same code ----
sw = open('sw.js', encoding='utf-8').read()
m = re.search(r"const VERSION = 'r3p-v(\d+)';", sw)
old_sw = ''
try:
    old_sw = open(out_sw, encoding='utf-8').read()
except OSError:
    pass
mv = re.search(r"const VERSION = '%s-v(\d+)';" % cache, old_sw)
v = int(mv.group(1)) + 1 if mv else 1
sw = sw.replace(m.group(0), f"const VERSION = '{cache}-v{v}';")
sw = sw.replace("const OWN = 'r3p-';", f"const OWN = '{cache}-';")
sw = sw.replace('// Road to 3 Plates, offline support.', f"// {name}'s 3 Plates, offline support.")
assert 'r3p' not in sw
open(out_sw, 'w', encoding='utf-8').write(sw)

# ---- manifest ----
man = open('manifest.webmanifest', encoding='utf-8').read()
man = man.replace('"name": "Road to 3 Plates"', f'"name": "{name}’s 3 Plates"').replace("Eko's training log", f"{name}’s training log")
open(out_manifest, 'w', encoding='utf-8').write(man)
print('wrote', out_html, out_sw, f'({cache}-v{v})', out_manifest)
