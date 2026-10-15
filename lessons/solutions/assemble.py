"""Build a student's project, as it looks at the end of a day, from these solution folders.

    python lessons/solutions/assemble.py 8 my-intelligence-system           the whole project at the end of day 8
    python lessons/solutions/assemble.py --only 8 my-intelligence-system    only the files of day 8, added to a project that already exists

Where the files go:
    solutions/dayNN/<file>           ->  exercises/dayNN/<file>
    solutions/dayNN/project/<path>   ->  <path>      (a later day replaces the same file from an earlier day)
"""
import argparse
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent  # the root of the repository, where config.json is
CONFIG = REPO / "config.json"


def copy_day(day, target):
    """Copy the files of one day into the student's project folder."""
    folder = HERE / f"day{day:02d}"
    if not folder.is_dir():
        raise SystemExit(f"There is no solution folder for day {day}.")

    for path in sorted(folder.iterdir()):
        if path.is_file():  # an exercise file
            destination = target / "exercises" / folder.name
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination / path.name)

    if (folder / "project").is_dir():  # project files keep their paths
        shutil.copytree(folder / "project", target, dirs_exist_ok=True)

    if day == 3:  # on day 3 the students copy config.json from the course folder
        shutil.copy2(CONFIG, target / "config.json")


def main():
    ap = argparse.ArgumentParser(description="Build a student's project from the solution folders")
    ap.add_argument("day", type=int, help="the day, from 1 to 15")
    ap.add_argument("target", help="the project folder to create (with --only: to add to)")
    ap.add_argument("--only", action="store_true",
                    help="copy only the files of this one day, into a project that already exists")
    args = ap.parse_args()

    if not 1 <= args.day <= 15:
        raise SystemExit("The day must be from 1 to 15.")
    target = Path(args.target)
    if not args.only and target.exists() and any(target.iterdir()):
        raise SystemExit(f"{target} already exists and is not empty. Choose a new folder, "
                         "or use --only to add the files of one day to it.")

    days = [args.day] if args.only else list(range(1, args.day + 1))
    if 3 in days and not CONFIG.is_file():  # check before creating anything, so no half-built folder is left behind
        raise SystemExit(f"config.json was not found at {CONFIG}. Run this script from a full copy of the "
                         "repository (the folder that contains config.json), or copy config.json into the project yourself.")

    target.mkdir(parents=True, exist_ok=True)
    for day in days:
        copy_day(day, target)

    what = f"the files of day {args.day}" if args.only else f"the project at the end of day {args.day}"
    print(f"Copied {what} into {target}.")
    if args.day >= 4:
        print("Remember: copy .env.example to .env and put your own Telegram token and chat id in it.")


if __name__ == "__main__":
    main()
