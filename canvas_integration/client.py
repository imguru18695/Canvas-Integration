"""Minimal client for the Canvas LMS REST API (UT Austin instance)."""
import os
from typing import Any, Dict, Iterator, Optional

import requests

DEFAULT_BASE_URL = "https://utexas.instructure.com"


class CanvasError(Exception):
    """Raised for non-2xx responses or missing configuration."""


class CanvasClient:
    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None,
                 session: Optional[requests.Session] = None):
        token = token or os.environ.get("CANVAS_API_TOKEN")
        if not token:
            raise CanvasError(
                "No token: set CANVAS_API_TOKEN (Canvas > Account > Settings > "
                "New Access Token)."
            )
        base = base_url or os.environ.get("CANVAS_BASE_URL") or DEFAULT_BASE_URL
        self.api = base.rstrip("/") + "/api/v1"
        self.session = session or requests.Session()
        self.session.headers["Authorization"] = f"Bearer {token}"

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None):
        url = path if path.startswith("http") else f"{self.api}{path}"
        resp = self.session.get(url, params=params, timeout=30)
        if not resp.ok:
            raise CanvasError(f"{resp.status_code} for {url}: {resp.text[:200]}")
        return resp

    def get(self, path: str, **params) -> Any:
        return self._request(path, params).json()

    def paginate(self, path: str, **params) -> Iterator[Any]:
        """Yield items across all pages, following Link rel=next headers."""
        params.setdefault("per_page", 100)
        resp = self._request(path, params)
        while True:
            yield from resp.json()
            nxt = resp.links.get("next", {}).get("url")
            if not nxt:
                return
            resp = self._request(nxt)

    def me(self) -> Dict[str, Any]:
        return self.get("/users/self")

    def courses(self, active_only: bool = True) -> Iterator[Dict[str, Any]]:
        params = {"enrollment_state": "active"} if active_only else {}
        return self.paginate("/courses", **params)

    def assignments(self, course_id: int, upcoming: bool = False):
        params = {"bucket": "upcoming"} if upcoming else {}
        return self.paginate(f"/courses/{course_id}/assignments", **params)

    def announcements(self, course_id: int):
        return self.paginate("/announcements", **{"context_codes[]": f"course_{course_id}"})

    def todo(self):
        return self.paginate("/users/self/todo")
