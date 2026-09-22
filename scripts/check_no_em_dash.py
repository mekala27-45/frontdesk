"""Scan tracked and untracked project text, including response templates."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {".py", ".md", ".json", ".yml", ".yaml", ".toml", ".tsx", ".ts", ".css", ".html", ".txt", ".svg"}

def violations(root: Path, paths: list[str]) -> list[str]:
    scanned = 0
    bad = []
    for name in paths:
        path = root / name
        if path.is_file() and (path.suffix in SUFFIXES or not path.suffix):
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            scanned += 1
            if chr(0x2014) in content:
                bad.append(name)
    if not scanned:
        raise ValueError("No text inspected")
    return bad

def main() -> None:
    files = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True).splitlines()
    bad = violations(ROOT, files)
    if bad:
        raise SystemExit(str(bad))
    print("Punctuation gate passed")

if __name__ == "__main__":
    main()

