from __future__ import annotations

import subprocess
from pathlib import Path


def run_step(repo_root: Path, *args: str) -> None:
    subprocess.run(args, cwd=repo_root, check=True)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    run_step(repo_root, "uv", "run", "pytest", "python/tests/test_generated_maps_models.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
