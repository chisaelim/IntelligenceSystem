"""Run every self-check and print a summary:   python -m tests.check_all"""
import subprocess
import sys
from pathlib import Path

checks = sorted(path.stem for path in Path(__file__).parent.glob("check_*.py") if path.stem != "check_all")

failed = []
for name in checks:
    result = subprocess.run([sys.executable, "-m", f"tests.{name}"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ok      {name}")
    else:
        failed.append(name)
        print(f"  FAILED  {name}")
        print((result.stdout + result.stderr)[-1500:])

print()
if failed:
    raise SystemExit(f"{len(failed)} of {len(checks)} checks failed: {', '.join(failed)}")
print(f"All {len(checks)} checks passed.")
