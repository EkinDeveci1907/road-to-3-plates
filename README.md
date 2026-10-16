# Road to 3 Plates

My training app: today's lifts with recommended weights, set logging, rest timer, progress toward a 315 bench, food and supplements.

Open it on iPhone in Safari, tap Share, then Add to Home Screen. It opens full screen and works offline.
Logs are saved on the phone. Settings (gear) → Back up now keeps a copy; `backups/` has repo-side snapshots.

## Links
- Me: https://ekindeveci1907.github.io/road-to-3-plates/
- Ahmed: https://ekindeveci1907.github.io/Ahmed/ (repo `ahmed`; old link `3-plates` just points there)
- Shayan: https://ekindeveci1907.github.io/road-to-3-plates/shayan/ (folder `shayan/` in this repo)

## How targets work
- Bench/squat top set: last top set you logged, +5 lbs if you hit the reps, same weight if you missed. The 11-week table in `BENCH_TOP` is only the starting line. Settings → Your numbers resets the line from a new 5-rep max.
- Everything else: double progression on the last time you did that exercise *in that workout*. Hit the top of the rep range on every set → +5.

## Updating
Edit `index.html`, bump `VERSION` in `sw.js`, then rebuild the friends' copies (one codebase, different name/storage prefix):

    python3 tools/make-friend.py Ahmed  tpf ahm ../ahmed/index.html ../ahmed/sw.js ../ahmed/manifest.webmanifest --old-link
    python3 tools/make-friend.py Ahmed  tpf tpf ../3-plates/index.html ../3-plates/sw.js ../3-plates/manifest.webmanifest --old-link
    python3 tools/make-friend.py Shayan shy shy shayan/index.html shayan/sw.js shayan/manifest.webmanifest
