from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

import index_images


def _make_image(iamge_path: Path, canvas_size: tuple[int, int], bg_color):
    img = Image.new("RGB", canvas_size, bg_color)
    img.save(iamge_path)


@pytest.fixture()
def make_image_and_output_paths(tmp_path: Path) -> tuple[Path, Path]:
    img_path_1: Path = tmp_path / "images"
    img_path_1.mkdir()
    _make_image((img_path_1 / "test-1.jpg"), (300, 300), (255, 0, 0))

    img_path_2: Path = img_path_1 / "more_images_subdir"
    img_path_2.mkdir()
    _make_image((img_path_2 / "test-2.jpg"), (300, 300), (255, 0, 255))
    _make_image((img_path_2 / "test-2-over.jpg"), (300, 300), (128, 0, 128))

    _make_image((img_path_1 / "test-3.jpg"), (400, 400), (0, 255, 0))

    img_path_3: Path = img_path_2 / "another_level"
    img_path_3.mkdir()

    _make_image((img_path_3 / "test-4.jpg"), (200, 200), (0, 255, 255))

    _make_image((img_path_1 / "test-5.jpg"), (200, 200), (0, 0, 255))

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


def test_scan_images_wo_recurse(make_image_and_output_paths: tuple[Path, Path]):
    img_path, out_path = make_image_and_output_paths
    args = [str(img_path), "-d", str(out_path)]
    index_images.main(args)

    out_file = out_path / index_images.DEFAULT_OUTPUT_NAME
    assert out_file.exists()

    out_html = out_file.read_text()
    assert "test-1.jpg" in out_html
    assert "test-2.jpg" not in out_html


@pytest.mark.parametrize("recurse_arg", ["-r", "--recurse"])
def test_scan_images_with_recurse(
    make_image_and_output_paths: tuple[Path, Path], recurse_arg: str
):
    img_path, out_path = make_image_and_output_paths
    args = [str(img_path), "-d", str(out_path), recurse_arg]
    index_images.main(args)

    out_file = out_path / index_images.DEFAULT_OUTPUT_NAME
    assert out_file.exists()

    out_html = out_file.read_text()
    assert "test-1.jpg" in out_html
    assert "test-2.jpg" in out_html


@pytest.mark.parametrize("markdown_arg", ["-m", "--markdown"])
def test_creates_markdown_file(
    make_image_and_output_paths: tuple[Path, Path], markdown_arg: str
):
    img_path, out_path = make_image_and_output_paths
    args = [str(img_path), "-d", str(out_path), markdown_arg]
    index_images.main(args)

    html_file = out_path / index_images.DEFAULT_OUTPUT_NAME
    assert html_file.exists()

    md_file = (out_path / index_images.DEFAULT_OUTPUT_NAME).with_suffix(".md")
    assert md_file.exists()

    out_md = md_file.read_text()
    assert "test-1.jpg" in out_md
    assert "test-2.jpg" not in out_md


@pytest.mark.parametrize("bare_arg", ["-b", "--bare"])
def test_bare_option(make_image_and_output_paths: tuple[Path, Path], bare_arg: str):
    img_path, out_path = make_image_and_output_paths
    args = [str(img_path), "-d", str(out_path), "-r", bare_arg]

    index_images.main(args)

    out_file = out_path / index_images.DEFAULT_OUTPUT_NAME
    assert out_file.exists()

    out_html = out_file.read_text().lower()
    assert "test-1.jpg" in out_html
    assert "test-2.jpg" in out_html

    assert "<h1>" not in out_html
    assert "<h2>" not in out_html
    assert "<hr>" not in out_html
    assert "<p>" not in out_html


@pytest.mark.parametrize(
    "title_arg,title_val", [("", ""), ("-t", "My-Title"), ("--title", "My-Title")]
)
def test_title_option(
    make_image_and_output_paths: tuple[Path, Path], title_arg: str, title_val: str
):
    img_path, _ = make_image_and_output_paths
    args = [str(img_path), "-r"]
    if title_arg:
        args.extend([title_arg, title_val])

    index_images.main(args)

    #  By default, output should be in the same directory as the images.
    out_file = img_path / index_images.DEFAULT_OUTPUT_NAME
    assert out_file.exists()

    out_html = out_file.read_text()
    assert "test-1.jpg" in out_html
    assert "test-2.jpg" in out_html
    assert "test-3.jpg" in out_html

    if title_arg:
        assert f"<title>{title_val}</title>" in out_html
    else:
        assert "<title>Images</title>" in out_html


def test_image_paths_relative(make_image_and_output_paths: tuple[Path, Path]):
    img_path, _ = make_image_and_output_paths

    #  No output path in args.
    args = [str(img_path), "-r"]

    index_images.main(args)

    out_file = img_path / index_images.DEFAULT_OUTPUT_NAME
    assert out_file.exists()

    out_html = out_file.read_text().lower()
    #  Anchor tags for images should have relative path.
    assert 'href="test-1.jpg"' in out_html
    assert 'href="test-3.jpg"' in out_html
    assert 'href="more_images_subdir/test-2.jpg"' in out_html
    #  Image names in text should have subdir, but not relative path.
    assert "<p>test-1.jpg</p>" in out_html
    assert "<p>more_images_subdir/test-2.jpg</p>" in out_html


def test_image_paths_relative_to_output(make_image_and_output_paths: tuple[Path, Path]):
    img_path, out_path = make_image_and_output_paths

    #  Has output path in args.
    args = [str(img_path), "-d", str(out_path), "-r"]

    index_images.main(args)

    out_file = out_path / index_images.DEFAULT_OUTPUT_NAME
    assert out_file.exists()

    out_html = out_file.read_text().lower()
    #  Anchor tags for images should have relative path.
    assert 'href="../images/test-1.jpg"' in out_html
    assert 'href="../images/test-3.jpg"' in out_html
    assert 'href="../images/more_images_subdir/test-2.jpg"' in out_html
    #  Image names in text should have subdir, but not relative path.
    assert "<p>test-1.jpg</p>" in out_html
    assert "<p>more_images_subdir/test-2.jpg</p>" in out_html
