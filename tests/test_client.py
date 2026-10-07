import pytest
import requests

from canvas_integration import CanvasClient, CanvasError


class FakeResp:
    def __init__(self, data, nxt=None, ok=True):
        self._d, self.ok, self.status_code, self.text = data, ok, 200 if ok else 401, "x"
        self.links = {"next": {"url": nxt}} if nxt else {}

    def json(self):
        return self._d


class FakeSession(requests.Session):
    def __init__(self, pages):
        super().__init__()
        self.pages, self.calls = pages, []

    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        return self.pages[url]


def test_requires_token(monkeypatch):
    monkeypatch.delenv("CANVAS_API_TOKEN", raising=False)
    with pytest.raises(CanvasError):
        CanvasClient()


def test_pagination_and_auth_header():
    base = "https://utexas.instructure.com/api/v1/courses"
    s = FakeSession({base: FakeResp([{"id": 1}], nxt="https://p2"), "https://p2": FakeResp([{"id": 2}])})
    c = CanvasClient(token="t", session=s)
    assert [x["id"] for x in c.courses()] == [1, 2]
    assert s.headers["Authorization"] == "Bearer t"


def test_error():
    s = FakeSession({"https://utexas.instructure.com/api/v1/users/self": FakeResp({}, ok=False)})
    with pytest.raises(CanvasError):
        CanvasClient(token="t", session=s).me()
