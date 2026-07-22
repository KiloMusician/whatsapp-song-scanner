from unittest.mock import Mock, patch

from src.radiodj_integration.radiodj_client import RadioDJClient


class FakeResponse:
    def __init__(self, payload=None, text="", status_code=200):
        self._payload = payload
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def build_client() -> RadioDJClient:
    client = RadioDJClient()
    client.api_url = "http://127.0.0.1:7000"
    client.api_key = "password"
    return client


def test_validate_connection_uses_plugin_endpoints():
    # /opt is the only endpoint confirmed working against the real plugin
    # (see radiodj_client.py's "only /opt works on this plugin version"
    # comment) - validate_connection() checks it first via _api_get_text,
    # and any() short-circuits on the first successful check, so a mock
    # that always succeeds only ever sees this one call.
    client = build_client()

    with patch("src.radiodj_integration.radiodj_client.requests.get") as mock_get:
        mock_get.return_value = FakeResponse(text="OK", payload={"NowPlaying": {"title": "Mirrors", "artist": "070 Shake"}})

        status = client.validate_connection()

    assert status["api_available"] is True
    mock_get.assert_called_once_with(
        "http://127.0.0.1:7000/opt",
        params={"command": "Status", "auth": "password"},
        timeout=10,
    )


def test_get_now_playing_parses_plugin_payload():
    client = build_client()

    with patch("src.radiodj_integration.radiodj_client.requests.get") as mock_get:
        mock_get.return_value = FakeResponse(
            payload={
                "NowPlaying": {
                    "TrackID": 39,
                    "Artist": "070 Shake",
                    "Title": "Mirrors",
                    "Album": "Glitter",
                }
            }
        )

        track = client.get_now_playing()

    assert track is not None
    assert track.id == 39
    assert track.artist == "070 Shake"
    assert track.title == "Mirrors"


def test_add_track_via_api_uses_opt_loadtracktobottom():
    # /opt is the only endpoint confirmed working against the real plugin
    # (see radiodj_client.py's "only /opt works on this plugin version"
    # comment) - add_track_via_api() calls it directly with requests.get,
    # not through _api_get_text/_api_get_json, so params come from
    # _build_api_params() with command/arg set explicitly.
    client = build_client()

    with patch.object(client, "find_track_in_library", return_value=39):
        with patch("src.radiodj_integration.radiodj_client.requests.get") as mock_get:
            mock_get.return_value = FakeResponse(payload={"ok": True})

            success = client.add_track_via_api("070 Shake", "Mirrors")

    assert success is True
    mock_get.assert_called_once_with(
        "http://127.0.0.1:7000/opt",
        params={"command": "LoadTrackToBottom", "arg": 39, "auth": "password"},
        timeout=10,
    )


def test_get_queue_parses_legacy_playlist_json():
    client = build_client()

    with patch("src.radiodj_integration.radiodj_client.requests.get") as mock_get:
        mock_get.return_value = FakeResponse(
            payload={
                "Playlist": [
                    {"TrackID": 103, "Artist": "070 Shake", "Title": "Purple Walls", "Album": "You Can't Kill Me"}
                ]
            }
        )

        queue = client.get_queue(limit=5)

    assert len(queue) == 1
    assert queue[0].id == 103
    assert queue[0].artist == "070 Shake"
    assert queue[0].title == "Purple Walls"