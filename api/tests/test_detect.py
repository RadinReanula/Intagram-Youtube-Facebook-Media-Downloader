import pytest

from app.errors import ApiError
from app.platforms.detect import detect


def test_youtube_shapes():
    assert detect("https://www.youtube.com/watch?v=jNQXAC9IVRw", "youtube").media_type == "video"
    assert detect("https://youtu.be/jNQXAC9IVRw", "youtube").media_type == "video"
    assert detect("https://www.youtube.com/shorts/abcdefghijk", "youtube").media_type == "short"
    assert detect("https://www.youtube.com/watch?v=jNQXAC9IVRw&list=PL123", "youtube").media_type == "video"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/playlist?list=PL123",
        "https://www.youtube.com/@someone",
        "https://www.youtube.com/channel/UC123",
        "https://www.youtube.com/live/abcdefghijk",
    ],
)
def test_youtube_rejects_collections_and_live(url: str):
    with pytest.raises(ApiError) as caught:
        detect(url, "youtube")
    assert caught.value.code == "unsupported"


def test_instagram_shapes():
    assert detect("https://www.instagram.com/reel/ABC123/", "instagram").media_type == "reel"
    assert detect("https://www.instagram.com/p/ABC123/", "instagram").media_type == "post"
    assert detect("https://www.instagram.com/tv/ABC123/", "instagram").media_type == "video"
    with pytest.raises(ApiError) as story:
        detect("https://www.instagram.com/stories/instagram/1/", "instagram")
    assert story.value.code == "unsupported"
    with pytest.raises(ApiError):
        detect("https://www.instagram.com/instagram/", "instagram")


def test_facebook_shapes():
    assert detect("https://www.facebook.com/watch/?v=1", "facebook").media_type == "video"
    assert detect("https://www.facebook.com/reel/123", "facebook").media_type == "reel"
    assert detect("https://fb.watch/abc/", "facebook").media_type == "video"
    assert detect("https://www.facebook.com/page/posts/123", "facebook").media_type == "post"
    with pytest.raises(ApiError):
        detect("https://www.facebook.com/somepage", "facebook")
    with pytest.raises(ApiError):
        detect("https://www.facebook.com/somepage/videos/1/live", "facebook")
