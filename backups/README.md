# Backups

Snapshots of every workout the repo can see. Workouts logged on the phone live only on that phone
until you tap Settings → **Back up now** (full JSON, restorable) or **Export history (CSV)**.

- `eko-workouts-YYYY-MM-DD.csv` — one row per set, same columns as the app's CSV export.
- `eko-backup-YYYY-MM-DD.json` — same data in the app's backup format. Settings → Restore merges it in (never overwrites newer sessions).
