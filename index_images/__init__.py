#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import NamedTuple

DEFAULT_OUTPUT_NAME = "images-index.html"

app_name = "index_images"

__version__ = "2024.06.1"

app_title = f"{app_name} (v{__version__})"

run_dt = datetime.now()


class AppOptions(NamedTuple):
    scan_path: Path
    html_path: Path
    do_toc: bool


def get_args(arglist=None):
    ap = argparse.ArgumentParser(description="Create an HTML index of images.")

    ap.add_argument(
        "dir_name",
        nargs="?",
        action="store",
        default=Path.cwd(),
        help="Name of the directory to scan for image files (*.png and "
        "*.jpg). Optional. If not specified, the current working directory "
        "is scanned.",
    )

    ap.add_argument(
        "-n",
        "--name",
        dest="out_name",
        action="store",
        help="Name of the output HTML file. Optional. If not specified, the "
        f"file is named '{DEFAULT_OUTPUT_NAME}'.",
    )

    ap.add_argument(
        "-d",
        "--out-dir",
        dest="out_dir",
        action="store",
        help="Directory in which to create the output HTML file. Optional. "
        "If not specified, the file is written to the same directory as "
        "is scanned for image files.",
    )

    ap.add_argument(
        "--no-list",
        action="store_true",
        dest="no_list",
        help="Do not include a Contents section listing links to each image.",
    )

    return ap.parse_args(arglist)


def get_opts(arglist=None) -> AppOptions:
    args = get_args(arglist)

    scan_path = Path(args.dir_name).expanduser().resolve()

    if not scan_path.exists():
        sys.stderr.write(f"\nPath not found: {scan_path}\n")
        sys.exit(1)

    if args.out_dir:
        out_path = Path(args.out_dir)
        if not out_path.exists():
            sys.stderr.write(f"\nPath not found: {out_path}\n")
            sys.exit(1)
    else:
        out_path = scan_path

    if args.out_name:
        html_path = out_path / Path(args.out_name).name
    else:
        html_path = out_path / DEFAULT_OUTPUT_NAME

    return AppOptions(scan_path, html_path, not args.no_list)


def html_style():
    s = """
        body { font-family: sans-serif; }
        h1 { color: gray; }
        h2 { color: steelblue; }
        h3 { color: slategray; }
        li {
            font-family: monospace;
            margin-top: 0.3em;
        }
        a:link, a:visited {
            color: #00248F;
            text-decoration: none;
        }
        :link:hover,:visited:hover {
            color: #B32400;
            text-decoration: underline;
        }
        img {
            width: 100%;
            height: auto;
        }
        .container { margin: 0.3rem; }
        .img-outer {
            font-size: 12px;
            font-weight: bold;
            margin-top: 1rem;
            padding: 1.5rem;
        }
        .img-inner {
            background-color: #e8effc;
            margin: auto;
            padding: 0.5rem;
            width: 80%;
        }
        #footer {
            font-size: x-small;
            margin-top: 2rem;
        }
    """
    return s.lstrip("\n").rstrip()


def html_head(title):
    return dedent(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>{0}</title>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <style>
        {1}
            </style>
        </head>
        <body>
        <div class="container">
        <h1>{0}</h1>
        """
    ).format(title, html_style())


def html_tail():
    return dedent(
        """
        <div id="footer">
          <hr>
          <strong>Created {0}</strong> by {1} version {2}
        </div>
        </div>  <!-- container -->
        </body>
        </html>
        """
    ).format(run_dt.strftime("%Y-%m-%d %H:%M"), app_name, __version__)


def get_image_id(image_index: int) -> str:
    return f"img{image_index}"


def html_img_div(img_name: str, img_rel: str, img_index: int) -> str:
    img_id = get_image_id(img_index)

    tag = f'<img id="{img_id}"\nsrc="{img_rel}"\n'
    tag += f'alt="Image file named {img_name}">'

    return dedent(
        """
        <div class="img-outer">
        <div class="img-inner">
        <p>{0}</p>
        <a href="{0}">{1}</a>
        <p>{0}</p>
        </div>
        </div>
        """
    ).format(img_rel, tag)


def html_img_div_w_mouseover(
    img_name: str,
    img_rel: str,
    img_index: int,
    mouseover_img: Path,
    dir_left: int,
) -> str:
    over_name = mouseover_img.name
    dir_rel = str(mouseover_img.parent)[dir_left:]
    over_rel = Path(dir_rel).joinpath(over_name)
    img_id = get_image_id(img_index)

    tag = f'<img id="{img_id}"\nsrc="{img_rel}"\n'
    tag += f'alt="Image file named {img_name}">'

    return dedent(
        """
        <div class="img-outer">
        <div class="img-inner">
        <p>{0}</p>
        <a href="{0}"
        onmouseover="if (document.images)
          document.getElementById('{2}').src='{3}';"
        onmouseout="if (document.images)
          document.getElementById('{2}').src='{0}';">
        {1}</a>
        <p>{0}</p>
        </div>
        </div>
        """
    ).format(img_rel, tag, img_id, over_rel)


def has_base_image(img_path: Path, image_list: list[Path]) -> bool:
    s = img_path.stem
    assert s.endswith("-over")  # noqa: S101
    s = s[:-5]
    return any(p.stem == s for p in image_list)


def get_mouseover_image(img_path: Path, image_list: list[Path]) -> Path:
    s = img_path.stem
    assert not s.endswith("-over")  # noqa: S101
    s = s + "-over"
    for p in image_list:
        if p.stem == s:
            return p
    return None


def main(arglist=None):
    print(f"\n{app_title}\n")

    opts = get_opts(arglist)

    dir_left = len(str(opts.scan_path)) + 1

    print(f"Looking for image files in '{opts.scan_path}'.")

    images = list(opts.scan_path.glob("**/*.jpg"))
    images += list(opts.scan_path.glob("**/*.png"))
    images.sort()

    html = []
    html.append(html_head(title="Images Index"))

    if opts.do_toc:
        html.append("<h2>Contents</h2>\n")
        html.append("<ol>\n")
        for i, p in enumerate(images):
            if p.stem.endswith("-over") and has_base_image(p, images):
                continue
            img_id = get_image_id(i)
            img_name = p.name
            dir_rel = str(p.parent)[dir_left:]
            img_rel = Path(dir_rel).joinpath(img_name)
            html.append(f'<li><a href="#{img_id}">{img_rel}</a></li>\n')
        html.append("</ol>\n")

    html.append("<h2>Images</h2>\n")

    prev_rel = ""

    for i, p in enumerate(images):
        if p.stem.endswith("-over") and has_base_image(p, images):
            #  An image that has a name (excluding the extension) ending with
            #  "-over", where there is another image with the same name
            #  without the "-over", is treated as a mouseover image.
            #  Do not include mouseover images in the index document.
            continue

        img_name = p.name
        dir_rel = str(p.parent)[dir_left:]
        img_rel = Path(dir_rel).joinpath(img_name)

        if dir_rel != prev_rel:
            html.append("<p>&nbsp;</p>\n<hr>\n")
            html.append(f"\n<h3>Folder: '{dir_rel}'</h3>\n")
            prev_rel = dir_rel

        mouseover_img = get_mouseover_image(p, images)

        if mouseover_img is None:
            html.append(html_img_div(img_name, img_rel, i))
        else:
            html.append(
                html_img_div_w_mouseover(img_name, img_rel, i, mouseover_img, dir_left)
            )

    html.append(html_tail())

    print(f"Writing '{opts.html_path}'")

    opts.html_path.write_text("".join(html))

    return 0


if __name__ == "__main__":
    main()
