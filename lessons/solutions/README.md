# Solutions

One folder per day (`day01` ... `day15`). A folder holds **only the files that are new or changed on that day**, at the same paths they have in a student's project (`my-intelligence-system/`).

```text
solutions/
├── day04/  .env.example  intelligence/__init__.py  intelligence/config.py  security_camera.py  tests/...
├── day05/  .gitignore  intelligence/rules.py  intelligence/detector.py  intelligence/app.py  ...
├── day07/  intelligence/rules.py  intelligence/app.py  tests/check_overlay.py  ...      (rules.py and app.py grow)
└── ...
```

## The state at the end of day N

Copy the folders `day01` ... `dayN` over each other, **in order** (a later day overwrites the same file from an earlier day). Also copy `config.json` from the root of this repository into the project folder (students copy it on Day 3), and create `.env` from `.env.example`.

```bash
mkdir my-intelligence-system
cp ../config.json my-intelligence-system/
for d in solutions/day0[1-9] solutions/day1[0-4]; do cp -R "$d"/. my-intelligence-system/; done    # up to day 14
```

(On Windows use `xcopy /E /Y` for each folder, in order.)

## Use for students who fall behind

Give them the folder of the day they missed, and tell them to read the new files before they run anything. A student who types or copies a file but does not understand it will be lost again on the next day.

## Notes

- Files in `exercises/dayNN/` are practice scripts. Files in `intelligence/`, `tools/` and `tests/` are the project.
- Some days replace a file from an earlier day with a better version: `rules.py` (Days 5, 7, 14), `app.py` (Days 5, 7, 8, 13, 14, 15), `detector.py` (Days 5, 13), `events.py` (Days 9, 14), `intelligence/__init__.py` (Days 4, 8, 12), `tests/check_rules.py` (Days 5, 14), `tests/check_events.py` (Days 9, 14), `tests/check_app.py` (Days 8, 13, 15), `tests/check_pipeline.py` (Days 13, 15).
- `day15/tests/example_weekend.py` is an **example** of a test for a student's own rule. It is not run by `check_all` (its name does not start with `check_`), because it fails until the rule is added.
- The final `intelligence/app.py` behaves like the reference project in the root of this repository. The only difference is that the alert decision is a function, `should_alert`, in `rules.py`.
