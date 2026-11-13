from urllib.parse import parse_qs

from app.security.tokens import sign_download, verify_download
from app.logging_setup import truncate_ip
from app.platforms.ytdlp import map_ytdlp_error


def test_download_token_round_trip():
    query = parse_qs(sign_download("abc", expires_at=4_102_444_800))
    verify_download("abc", query["expires"][0], query["token"][0])


def test_ip_is_truncated_in_logs():
    assert truncate_ip("saw 203.0.113.45 today") == "saw 203.0.113.0 today"
    assert truncate_ip("2001:db8:85a3::8a2e:370:7334").startswith("2001:db8:85a3::")


def test_ytdlp_errors_map_to_plain_codes():
    assert map_ytdlp_error("ERROR: Private video. Sign in").code == "private_content"
    assert map_ytdlp_error("ERROR: Video unavailable").code == "not_found"
    assert map_ytdlp_error("ERROR: HTTP Error 429: Too Many Requests").code == "blocked"
    assert map_ytdlp_error("File is larger than max-filesize").code == "limit_exceeded"
