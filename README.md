# Road to 3 Plates

My training app: today's lifts with recommended weights, set logging, rest timer, progress toward a 315 bench, food and supplements.

Open it on iPhone in Safari, tap Share, then Add to Home Screen. It opens full screen and works offline.
Logs are saved on the phone. Settings (gear) → Back up now keeps a copy; `backups/` has repo-side snapshots.

## Links
- Me: https://ekindeveci1907.github.io/road-to-3-plates/
- Ahmed: https://ekindeveci1907.github.io/Ahmed/ (repo `ahmed`; old link `3-plates` just points there)
- Shayan: https://ekindeveci1907.github.io/road-to-3-plates/shayan/ (folder `shayan/` in this repo)

## The plan (v4.9)
Mon Upper A, Wed Lower A, Thu Upper B, Fri Lower B. Big compound lifts get 2–3 hard sets of 6–8; isolation work gets 3 sets.
Bench keeps 4–5 sets: Monday top set + 3 back-off sets + 1 wide-grip set; Thursday heavy set + 2 volume sets + 1 wide-grip set.
The wide-grip set is always the last bench set: lighter, 10–12 reps. Lower A uses the seated leg curl and seated calf raise. Cable crunch with the V-bar.

## How targets work
- Every exercise: the heaviest weight from the last time you did it (any day) + 5 lbs, once a week. Already did it earlier this week → same weight. Sets of 2 reps or fewer and deload week don't count.
- Bench: Monday's top set and Thursday's heavy set are one chain, each 5 lbs more than the last heavy bench (210 Thu → 215 Mon → 220 Thu). Back-off sets, Thursday volume sets and the wide-grip set each follow their own last weight, +5 a week (first wide-grip set: about 75% of the top set). The 11-week table in `BENCH_TOP` is only the starting line; Settings → Your numbers resets it from a new 5-rep max.
- Bodyweight-only (pull-ups): add 5 lbs once every set reaches the top of the rep range.
- "Last time" shows the most recent time you did that exercise, any day. Bench rows show every bench set from that day.

## Today tab
- All seven days across the top, opens on today. Tue, Sat and Sun are rest days: a rest page (eat, sleep, chill) that says what's next, offers "Train anyway", and keeps a missed day open until Sunday ("Do Lower B today").
- Mon/Wed/Thu/Fri dots fill in as the week goes. Swipe left or right to move between days.
- A finished exercise folds to one line. Once a workout is saved the bar says "Workout done" with a Review button.
- Rest timer: beeps (also with the iPhone on silent), vibrates, and highlights the next set.
- Progress: weight-gain pace from weekly weigh-in averages, and a 315 countdown from the heavy-bench chain.

## Updating
Edit `index.html`, bump `VERSION` in `sw.js`, then rebuild the friends' copies (one codebase, different name/storage prefix):

    python3 tools/make-friend.py Ahmed  tpf ahm ../ahmed/index.html ../ahmed/sw.js ../ahmed/manifest.webmanifest --old-link
    python3 tools/make-friend.py Ahmed  tpf tpf ../3-plates/index.html ../3-plates/sw.js ../3-plates/manifest.webmanifest --old-link
    python3 tools/make-friend.py Shayan shy shy shayan/index.html shayan/sw.js shayan/manifest.webmanifest
