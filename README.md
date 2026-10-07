# Canvas Integration (UT Austin)

Python client + CLI for the Canvas LMS REST API at `https://utexas.instructure.com`.

## Setup
1. In Canvas: Account > Settings > **New Access Token**.
2. `export CANVAS_API_TOKEN=...` (optionally `CANVAS_BASE_URL` to override).
3. `pip install -e .[dev]`

## Use
```
canvas whoami | courses | todo
canvas assignments <course_id>
canvas announcements <course_id>
```
```python
from canvas_integration import CanvasClient
for c in CanvasClient().courses(): print(c["name"])
```
Tokens are personal credentials; never commit them. UT may restrict token creation; if so, a Developer Key (OAuth2) request to UT's Canvas admins is needed.

## Tests
`pytest`

## Keeping data out of GitHub
After cloning, enable the guard hook: `git config core.hooksPath .githooks`.
It blocks commits that contain tokens, Canvas-style data fields, or files outside
the source/doc folders; CI re-runs the same check. Never use `--no-verify`.
Data exports are git-ignored; write any saved output outside the repo.
