#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import NamedTuple

DEFAULT_OUTPUT_NAME = "images-index.html"

app_name = "index_images"

#  Using calver (YYYY.0M.MICRO).
__version__ = "2026.09.4"

app_title = f"{app_name} (v{__version__})"

run_dt = datetime.now()


class AppOptions(NamedTuple):
    scan_path: Path
    do_recurse: bool
    html_path: Path
    title: str
    do_headings: bool
    do_toc: bool
    do_filename: bool
    do_footer: bool
    do_markdown: bool


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
        "-r",
        "--recurse",
        dest="do_recurse",
        action="store_true",
        help="Recursively scan subdirectories for image files. Optional.",
    )

    ap.add_argument(
        "-m",
        "--markdown",
        dest="do_markdown",
        action="store_true",
        help="Generate a Markdown version of the index. Optional.",
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
        "-t",
        "--title",
        dest="title",
        action="store",
        help="Title for HTML file. Default is 'Images'.",
    )

    ap.add_argument(
        "--no-list",
        action="store_true",
        dest="no_list",
        help="Do not include a Contents section listing links to each image.",
    )

    ap.add_argument(
        "-b",
        "--bare",
        action="store_true",
        dest="do_bare",
        help="Bare HTML file: Same as --no-list, but also skips headings, file names, "
        "and footer.",
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

    title = args.title if args.title else "Images"

    if args.do_bare:
        do_toc = False
        do_headings = False
        do_filename = False
        do_footer = False
    else:
        do_toc = not args.no_list
        do_headings = True
        do_filename = True
        do_footer = True

    return AppOptions(
        scan_path,
        args.do_recurse,
        html_path,
        title,
        do_headings,
        do_toc,
        do_filename,
        do_footer,
        args.do_markdown,
    )


def html_style_full():
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
            width: 90%;
        }
        #footer {
            font-size: x-small;
            margin-top: 2rem;
        }
        @media print {
            .img-outer {
                break-after: page;
            }
        }
    """
    return s.lstrip("\n").rstrip()


def html_style_bare():
    s = """
        body { font-family: sans-serif; }
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
            padding: 1rem;
        }
        .img-inner {
            padding: 0.5rem;
            width: 100%;
        }
        #footer {
            font-size: x-small;
        }
        @media print {
            .img-outer {
                break-after: page;
            }
        }
    """
    return s.lstrip("\n").rstrip()


def html_head(title, html_style):
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
            <link rel="stylesheet" type="text/css" href="style.css">
        </head>
        <body>
        <div class="container">
        """
    ).format(title, html_style())


def html_tail(do_footer: bool):
    if do_footer:
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
    return dedent(
        """
        </div>  <!-- container -->
        </body>
        </html>
        """
    )


def get_image_id(image_index: int) -> str:
    return f"img{image_index}"


def html_img_div(
    opts: AppOptions,
    img_name: str,
    img_name_rel: str,
    img_path_rel: Path,
    img_index: int,
) -> str:
    img_id = get_image_id(img_index)

    tag = f'<img id="{img_id}" src="{img_path_rel}" '
    tag += f'alt="Image file named {img_name}">'

    p_fn = f"<p>{img_name_rel}</p>" if opts.do_filename else ""

    return dedent(
        f"""
        <div class="img-outer">
        <div class="img-inner">
        {p_fn}
        <a href="{img_path_rel}">{tag}</a>
        {p_fn}
        </div>
        </div>
        """
    )


def html_img_div_w_mouseover(  # noqa: PLR0913
    opts: AppOptions,
    img_name: str,
    img_name_rel: str,
    img_path_rel: Path,
    over_path_rel: Path,
    img_index: int,
) -> str:
    img_id = get_image_id(img_index)

    tag = f'<img id="{img_id}" src="{img_path_rel}" '
    tag += f'alt="Image file named {img_name}">'

    p_fn = f"<p>{img_name_rel}</p>" if opts.do_filename else ""

    return dedent(
        f"""
        <div class="img-outer">
        <div class="img-inner">
        {p_fn}
        <a href="{img_path_rel}"
        onmouseover="if (document.images)
          document.getElementById('{img_id}').src='{over_path_rel}';"
        onmouseout="if (document.images)
          document.getElementById('{img_id}').src='{img_path_rel}';">
        {tag}</a>
        {p_fn}
        </div>
        </div>
        """
    )


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


def write_html(opts: AppOptions, images: list[Path], dir_left: int):
    html = []
    style = html_style_full if opts.do_headings else html_style_bare
    html.append(html_head(title=opts.title, html_style=style))
    if opts.do_headings:
        html.append(f"<h1>{opts.title}</h1>")

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

    if opts.do_headings:
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

        img_name_rel = str(Path(dir_rel).joinpath(img_name))

        img_path_rel = os.path.relpath(p, opts.html_path.parent)

        if dir_rel != prev_rel:
            if opts.do_headings:
                html.append("<p>&nbsp;</p>\n<hr>\n")
                html.append(f"\n<h3>Folder: '{dir_rel}'</h3>\n")
            prev_rel = dir_rel

        mouseover_img = get_mouseover_image(p, images)

        if mouseover_img:
            over_path_rel = os.path.relpath(mouseover_img, opts.html_path.parent)
            html.append(
                html_img_div_w_mouseover(
                    opts,
                    img_name,
                    img_name_rel,
                    img_path_rel,
                    over_path_rel,
                    i,
                )
            )
        else:
            html.append(html_img_div(opts, img_name, img_name_rel, img_path_rel, i))

    html.append(html_tail(opts.do_footer))

    print(f"Writing '{opts.html_path}'")

    opts.html_path.write_text("".join(html))


def get_image_link(img_path: Path):
    s = img_path.stem
    s = s.replace(" ", "-")
    s = s.replace(".", "-")
    return s.lower()


def write_markdown(opts, images, dir_left):
    if not opts.do_markdown:
        return
    md = []
    md.append(f"# {app_title}\n\n")

    if opts.do_toc:
        md.append("## Contents\n\n")
        for _, p in enumerate(images):
            if p.stem.endswith("-over") and has_base_image(p, images):
                # No mouseover images in the Markdown version.
                continue

            img_name = p.name
            dir_rel = str(p.parent)[dir_left:]
            img_rel = Path(dir_rel).joinpath(img_name)
            md.append(f"- [{img_rel}](#{get_image_link(p)})\n")
        md.append("\n")

    md.append("## Images\n\n")

    prev_rel = ""

    for _, p in enumerate(images):
        if p.stem.endswith("-over") and has_base_image(p, images):
            continue

        img_name = p.name
        dir_rel = str(p.parent)[dir_left:]
        img_rel = Path(dir_rel).joinpath(img_name)

        if dir_rel != prev_rel:
            md.append("\n---\n\n")
            md.append(f"\n### Folder: '{dir_rel}'\n\n")
            prev_rel = dir_rel

        md.append(f"#### {p.stem}\n\n")
        md.append(f"![{img_name}]({img_rel})\n\n")
        md.append(f"File name: **{img_name}**\n\n---\n\n")

    out_path = opts.html_path.with_suffix(".md")

    print(f"Writing '{out_path}'")

    out_path.write_text("".join(md))


def main(arglist=None):
    print(f"\n{app_title}\n")

    opts = get_opts(arglist)

    dir_left = len(str(opts.scan_path)) + 1

    print(f"Looking for image files in '{opts.scan_path}'.")

    # TODO: This is a very limited set of image types. Add more to the default
    # set and/or add an option to specify more on the command line.

    if opts.do_recurse:
        images = list(opts.scan_path.glob("**/*.jpg"))
        images += list(opts.scan_path.glob("**/*.png"))
    else:
        images = list(opts.scan_path.glob("*.jpg"))
        images += list(opts.scan_path.glob("*.png"))

    images.sort(key=lambda item: [str(item.parent), str(item.name)])

    write_html(opts, images, dir_left)

    write_markdown(opts, images, dir_left)

    return 0


if __name__ == "__main__":
    main()
