import pytest

from pathlib import Path

import index_images


def test_opts_toc():
    #  Note: argv[0] is the script name.
    opts = index_images.get_opts(["index_images.py"])
    assert opts.do_toc
    opts = index_images.get_opts(["index_images.py", "--no-list"])
    assert not opts.do_toc


def test_opts_scan_path_default():
    cwd = str(Path.cwd())
    opts = index_images.get_opts(["index_images.py"])
    assert isinstance(opts.scan_path, Path)
    assert str(opts.scan_path) == cwd


def test_opts_scan_path_expand():
    home = str(Path.home())
    opts = index_images.get_opts(["index_images.py", "~/"])
    assert str(opts.scan_path) == home


def test_opts_scan_path_given(tmp_path):
    p: Path = tmp_path / "scan_me"
    p.mkdir()
    dir_name = str(p)
    opts = index_images.get_opts(["index_images.py", dir_name])
    assert str(opts.scan_path) == dir_name
    assert str(opts.html_path) == str(p / index_images.DEFAULT_OUTPUT_NAME)


def test_opts_scan_path_not_exist(tmp_path, capsys):
    dir_name = str(tmp_path / "scan_me")
    bad_name = dir_name + "_NOT"
    with pytest.raises(SystemExit):
        _ = index_images.get_opts(["index_images.py", bad_name])
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_opts_out_dir_given(tmp_path):
    p1: Path = tmp_path / "scan_me"
    p1.mkdir()
    p2: Path = tmp_path / "out_here"
    p2.mkdir()

    #  Short option.
    opts = index_images.get_opts(
        ["index_images.py", str(p1), "-d", str(p2)]
    )
    assert str(opts.html_path) == str(p2 / index_images.DEFAULT_OUTPUT_NAME)

    #  Long option.
    opts = index_images.get_opts(
        ["index_images.py", str(p1), "--out-dir", str(p2)]
    )
    assert str(opts.html_path) == str(p2 / index_images.DEFAULT_OUTPUT_NAME)


def test_opts_out_name_given(tmp_path):
    p1: Path = tmp_path / "scan_me"
    p1.mkdir()

    #  Short option.
    opts = index_images.get_opts(
        ["index_images.py", str(p1), "-n", "other_name.html"]
    )
    assert str(opts.html_path) == str(p1 / "other_name.html")

    #  Long option.
    opts = index_images.get_opts(
        ["index_images.py", str(p1), "--name", "other_name.html"]
    )
    assert str(opts.html_path) == str(p1 / "other_name.html")


def test_opts_out_dir_not_exist(tmp_path, capsys):
    p1: Path = tmp_path / "scan_me"
    p1.mkdir()
    p2: Path = tmp_path / "not_here"

    #  Specified output name is a driectory that does not exist.
    with pytest.raises(SystemExit):
        _ = index_images.get_opts(
            ["index_images.py", str(p1), "-d", str(p2)]
        )
    captured = capsys.readouterr()
    assert "not found" in captured.err
