# Solutions

One folder per day, `day01` ... `day15`. A day's folder holds the files the students write **on that day**:

```text
solutions/
├── assemble.py                  builds a student's project from these folders
├── day01/   hello.py  greeting.py  ...                      the exercise files, directly in the folder
├── day04/   parse_env.py  safe_load.py  ...                 the exercise files
│            project/  .env.example  intelligence/  security_camera.py  tests/     the project files
├── day05/   ...
└── day14/   project/  intelligence/  tests/  tools/         (no exercises on this day: project files only)
```

## Where the files go

| In the solutions | In the student's project (`my-intelligence-system/`) |
|---|---|
| `dayNN/<file>`, an exercise file directly in the day folder | `exercises/dayNN/<file>` |
| `dayNN/project/<path>` | `<path>`. For example `day04/project/intelligence/config.py` is `intelligence/config.py` |

Project files are written in stages. `app.py`, for example, has a version in six day folders. **A later day replaces the same file from an earlier day**, so the project at the end of day N is all the `project/` folders from `day01` to `dayN` copied over each other, in order. `config.json` is not in the folders: students copy it from the root of this repository on Day 3.

Days 1 to 13 have exercise files. Days 14 and 15 have only a `project/` folder.

## Build a project as it is at the end of day N

```bash
python lessons/solutions/assemble.py 8 my-intelligence-system
```

This creates `my-intelligence-system/` as it looks at the end of day 8: the exercise files in `exercises/dayNN/`, the project files, and `config.json`. It refuses to write into a folder that already has files. From day 4 on, copy `.env.example` to `.env` and put a Telegram token and chat id in it (or run the program with `--dry-run`).

The script uses only Python's standard library, so the command is the same on Windows, macOS and Linux. (It was tested on macOS.) On day 3 it copies `config.json` from the root of this repository, so run it from the full repository; if it cannot find the file, it says so before it creates anything.

## Help a student who fell behind

```bash
python lessons/solutions/assemble.py --only 8 my-intelligence-system
```

This copies only the files of **day 8**, into the project that already exists. Files with the same name are **replaced**, so the student loses their own version of those files. Use it for the day the student missed, and tell them to read the new files before they run anything: a file that is copied but not understood will be a problem again on the next day.

## Notes

- Some days replace a file from an earlier day with a better version: `intelligence/rules.py` (Days 5, 7, 14), `intelligence/app.py` (Days 5, 7, 8, 13, 14, 15), `intelligence/detector.py` (Days 5, 13), `intelligence/events.py` (Days 9, 14), `intelligence/__init__.py` (Days 4, 8, 12), `tests/check_rules.py` (Days 5, 14), `tests/check_events.py` (Days 9, 14), `tests/check_app.py` (Days 8, 13, 15), `tests/check_pipeline.py` (Days 13, 15).
- `day15/project/tests/example_weekend.py` is an **example** of a test for a student's own rule. It is not run by `check_all` (its name does not start with `check_`), because it fails until the rule is added.
- The final `intelligence/app.py` behaves like the reference project in the root of this repository. The only difference is that the alert decision is a function, `should_alert`, in `rules.py`.
- **Keep this folder away from students until they need it.** If they have the answers from the beginning, many will copy instead of think.
