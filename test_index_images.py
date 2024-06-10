from __future__ import annotations

from pathlib import Path

import pytest

import index_images


@pytest.fixture()
def fake_image_and_output_paths(tmp_path: Path) -> tuple[Path, Path]:
    img_path_1: Path = tmp_path / "images"
    img_path_1.mkdir()
    (img_path_1 / "fake-1.jpg").write_text("fake image 1")
    img_path_2: Path = img_path_1 / "more"
    img_path_2.mkdir()
    (img_path_2 / "fake-2.jpg").write_text("fake image 2")
    out_path = tmp_path / "output"
    out_path.mkdir()
    return img_path_1, out_path


def test_opts_toc():
    opts = index_images.get_opts([])
    assert opts.do_toc
    opts = index_images.get_opts(["--no-list"])
    assert not opts.do_toc


def test_opts_scan_path_default():
    cwd = str(Path.cwd())
    opts = index_images.get_opts([])
    assert isinstance(opts.scan_path, Path)
    assert str(opts.scan_path) == cwd


def test_opts_scan_path_expand():
    home = str(Path.home())
    opts = index_images.get_opts(["~/"])
    assert str(opts.scan_path) == home


def test_opts_scan_path_given(tmp_path):
    p: Path = tmp_path / "scan_me"
    p.mkdir()
    dir_name = str(p)
    opts = index_images.get_opts([dir_name])
    assert str(opts.scan_path) == dir_name
    assert str(opts.html_path) == str(p / index_images.DEFAULT_OUTPUT_NAME)


def test_opts_scan_path_not_exist(tmp_path, capsys):
    dir_name = str(tmp_path / "scan_me")
    bad_name = dir_name + "_NOT"
    with pytest.raises(SystemExit):
        _ = index_images.get_opts([bad_name])
    captured = capsys.readouterr()
    assert "not found" in captured.err


@pytest.mark.parametrize("dir_arg", ["-d", "--out-dir"])
def test_opts_out_dir_given(tmp_path, dir_arg):
    p1: Path = tmp_path / "scan_me"
    p1.mkdir()
    p2: Path = tmp_path / "out_here"
    p2.mkdir()
    opts = index_images.get_opts([str(p1), dir_arg, str(p2)])
    assert str(opts.html_path) == str(p2 / index_images.DEFAULT_OUTPUT_NAME)


@pytest.mark.parametrize("name_arg", ["-n", "--name"])
def test_opts_out_name_given(tmp_path, name_arg):
    p1: Path = tmp_path / "scan_me"
    p1.mkdir()
    opts = index_images.get_opts([str(p1), name_arg, "other_name.html"])
    assert str(opts.html_path) == str(p1 / "other_name.html")


def test_opts_out_dir_not_exist(tmp_path, capsys):
    p1: Path = tmp_path / "scan_me"
    p1.mkdir()
    p2: Path = tmp_path / "not_here"

    #  Specified output name is a driectory that does not exist.
    with pytest.raises(SystemExit):
        _ = index_images.get_opts([str(p1), "-d", str(p2)])
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_scan_images_wo_recurse(fake_image_and_output_paths: tuple[Path, Path]):
    img_path, out_path = fake_image_and_output_paths
    args = [str(img_path), "-d", str(out_path)]
    index_images.main(args)

    out_file = out_path / index_images.DEFAULT_OUTPUT_NAME
    assert out_file.exists()

    out_html = out_file.read_text()
    assert "fake-1.jpg" in out_html
    assert "fake-2.jpg" not in out_html


@pytest.mark.parametrize("recurse_arg", ["-r", "--recurse"])
def test_scan_images_with_recurse(
    fake_image_and_output_paths: tuple[Path, Path], recurse_arg: str
):
    img_path, out_path = fake_image_and_output_paths
    args = [str(img_path), "-d", str(out_path), recurse_arg]
    index_images.main(args)

    out_file = out_path / index_images.DEFAULT_OUTPUT_NAME
    assert out_file.exists()

    out_html = out_file.read_text()
    assert "fake-1.jpg" in out_html
    assert "fake-2.jpg" in out_html
