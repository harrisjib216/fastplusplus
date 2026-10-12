#!/usr/bin/env python3
"""Fail if tracked files carry personal data: a contributor's home-directory path to this checkout, a personal
email address, or a credential. With --commits, also fail if any commit in the history of HEAD has a personal
email address as its author or committer (commits use a GitHub noreply address).

Prompts rendered on a personal machine embed the checkout's absolute path (agents need absolute output paths),
so run this before committing them; `--fix` rewrites such paths to /path/to/<repo>. CI runs it on every push.
Cloud container paths (/home/user, /home/claude) are not personal and are allowed."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# A home directory that leads to this repo or to the sibling developer source checkout.
HOME_PATH = re.compile(r"/(?:Users|home)/(?!(?:user|claude)/)[^/\s\"'`]+/(?:[^\s\"'`]*/)?(fastpp)\b")
PATTERNS = {
    "home path": HOME_PATH,
    "personal email": re.compile(r"[A-Za-z0-9._%+-]+@(?:gmail|googlemail|outlook|hotmail|live|icloud|me|yahoo"
                                 r"|proton|protonmail|aol)\.[a-z.]+", re.I),
    "credential": re.compile(r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9-]{10,}"
                             r"|AKIA[0-9A-Z]{16}|xox[bpa]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY"),
}


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    return [ROOT / p for p in out.decode().split("\0") if p]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fix", action="store_true", help="rewrite home-directory paths to /path/to/<repo>")
    ap.add_argument("--commits", action="store_true", help="also check author and committer emails of HEAD's history")
    args = ap.parse_args()
    problems = []
    if args.commits:
        log = subprocess.run(["git", "log", "--format=%h %ae %ce", "HEAD"], cwd=ROOT, capture_output=True,
                             check=True, text=True).stdout
        for line in log.splitlines():
            sha, *emails = line.split()
            if any(PATTERNS["personal email"].fullmatch(e) for e in emails):
                problems.append(f"commit {sha}: personal email address as author or committer")
    for path in tracked_files():
        try:
            text = path.read_text()
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        if args.fix and HOME_PATH.search(text):
            text = HOME_PATH.sub(lambda m: f"/path/to/{m.group(1)}", text)
            path.write_text(text)
        for kind, rx in PATTERNS.items():
            for m in rx.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                problems.append(f"{path.relative_to(ROOT)}:{line}: {kind}")
    for p in problems[:50]:
        print(p)
    if problems:
        print(f"{len(problems)} finding(s); home paths can be fixed with --fix", file=sys.stderr)
        sys.exit(1)
    print("check_pii: clean")


if __name__ == "__main__":
    main()
