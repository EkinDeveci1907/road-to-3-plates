# Road to 3 Plates

My training app: today's lifts with recommended weights, set logging, rest timer, progress toward a 315 bench, food and supplements.

Open it on iPhone in Safari, tap Share, then Add to Home Screen. It opens full screen and works offline.
Logs are saved on the phone. Settings (gear) → Back up now keeps a copy; `backups/` has repo-side snapshots.

## Links
- Me: https://ekindeveci1907.github.io/road-to-3-plates/
- Ahmed: https://ekindeveci1907.github.io/Ahmed/ (repo `ahmed`; old link `3-plates` just points there)
- Shayan: https://ekindeveci1907.github.io/road-to-3-plates/shayan/ (folder `shayan/` in this repo)

## How targets work
- Every exercise: the heaviest weight from the last time you did it (any day) + 5 lbs, once a week. Already did it earlier this week → same weight. Sets of 2 reps or fewer and deload week don't count.
- Bench/squat top set, back-off sets and Thursday wide-grip volume each follow their own last weight. Thursday's heavy set is 10 under Monday's top set. The 11-week table in `BENCH_TOP` is only the starting line; Settings → Your numbers resets it from a new 5-rep max.
- Bodyweight-only (pull-ups): add 5 lbs once every set reaches the top of the rep range.
- "Last time" shows the most recent time you did that exercise, any day. Bench rows show every bench set from that day.

## Updating
Edit `index.html`, bump `VERSION` in `sw.js`, then rebuild the friends' copies (one codebase, different name/storage prefix):

    python3 tools/make-friend.py Ahmed  tpf ahm ../ahmed/index.html ../ahmed/sw.js ../ahmed/manifest.webmanifest --old-link
    python3 tools/make-friend.py Ahmed  tpf tpf ../3-plates/index.html ../3-plates/sw.js ../3-plates/manifest.webmanifest --old-link
    python3 tools/make-friend.py Shayan shy shy shayan/index.html shayan/sw.js shayan/manifest.webmanifest
