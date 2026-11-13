from pathlib import Path

from app.jobs.runner import select_outputs


def test_single_finished_file_is_kept(tmp_path: Path):
    video = tmp_path / "Me at the zoo.mp4"
    video.write_bytes(b"video")
    chosen, bundle = select_outputs([video], "best")
    assert chosen == [video]
    assert bundle is False


def test_fragments_are_not_zipped_for_one_video(tmp_path: Path):
    video = tmp_path / "Me at the zoo.f395.mp4"
    audio = tmp_path / "Me at the zoo.f140.m4a"
    video.write_bytes(b"v")
    audio.write_bytes(b"a")
    chosen, bundle = select_outputs([video, audio], "bestvideo")
    assert chosen == []
    assert bundle is False


def test_download_all_bundles_every_item(tmp_path: Path):
    first = tmp_path / "one.mp4"
    second = tmp_path / "two.jpg"
    first.write_bytes(b"v")
    second.write_bytes(b"i")
    chosen, bundle = select_outputs([first, second], "all")
    assert bundle is True
    assert set(chosen) == {first, second}
