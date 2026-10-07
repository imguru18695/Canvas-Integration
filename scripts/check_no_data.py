#!/usr/bin/env python3
"""Fail if files to be committed look like Canvas data or contain secrets.

Usage: check_no_data.py            check staged files (pre-commit)
       check_no_data.py --all      check every tracked file (CI)
"""
import re
import subprocess
import sys

ALLOWED_DIRS = ("canvas_integration/", "tests/", "scripts/", ".githooks/", ".github/")
ALLOWED_FILES = {".gitignore", "README.md", "pyproject.toml"}
SELF = "scripts/check_no_data.py"

# Canvas tokens look like "<id>~<64 chars>"; also catch long bearer strings.
CONTENT_PATTERNS = {
    "Canvas access token": re.compile(r"\b\d{3,6}~[A-Za-z0-9]{32,}\b"),
    "bearer credential": re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{30,}"),
    "GitHub token": re.compile(r"\b(ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{20,}"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Canvas data field": re.compile(
        r"""["'](sis_user_id|sis_course_id|current_grade|final_score|"""
        r"""current_score|login_id|integration_id)["']\s*:"""
    ),
}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def main():
    check_all = "--all" in sys.argv
    if check_all:
        files = git("ls-files", "-z").decode().split("\0")
    else:
        files = git("diff", "--cached", "--name-only", "--diff-filter=ACM", "-z").decode().split("\0")
    problems = []
    for f in filter(None, files):
        if f == SELF:
            continue
        if f not in ALLOWED_FILES and not f.startswith(ALLOWED_DIRS):
            problems.append(f"{f}: path is outside the allowed source/doc locations")
            continue
        blob = git("show", f":{f}") if not check_all else open(f, "rb").read()
        text = blob.decode("utf-8", errors="ignore")
        for name, pat in CONTENT_PATTERNS.items():
            if pat.search(text):
                problems.append(f"{f}: contains what looks like a {name}")
    if problems:
        print("Blocked: possible Canvas data or secrets in commit:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("Remove them (never commit real Canvas data). If this is a false "
              "positive, adjust scripts/check_no_data.py in a reviewed change.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
