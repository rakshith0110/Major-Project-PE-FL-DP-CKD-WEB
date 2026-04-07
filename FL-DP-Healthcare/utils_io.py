from pathlib import Path
def ensure_dirs(path: Path):
    path.mkdir(parents=True, exist_ok=True)
