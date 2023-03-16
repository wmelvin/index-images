# index_images.py

**index_images.py** is a stand-alone Python script (it only uses standard library modules) that scans a directory for image files and creates a HTML index of any found images. Currently the script only looks for `*.jpg` and `*.png` files.

### Mouseover Images

Mouseover images may be added using a file naming convention.

An image that has a file name (excluding the extension) ending with **-over**, where there is another image with the same file name (without the "-over"), is treated as a mouseover image. The purpose of a mouseover image might be to add annotations to, or highlight sections of, an original image.

For example, if `screen_20220808_1904.png` is the name of an image included in the index, then a file named `screen_20220808_1904-over.jpg` will be displayed on mouseover. Note the file type (extension) does not need to be the same.

Inline JavaScript is added to the **anchor tag** to display the image when the **mouseover** event fires.

Mouseover images are **not included** in the index document. They are only referenced in the JavaScript.

### Screenshots and Example Output

This [images-index.html](https://wmelvin.github.io/examples/index_images/images-index.html) was created by running *index_images.py* on the screenshots (screenshots of screenshots) used to make the following animated GIF.

---

![Screenshot animation of running index_images.py](readme_images/run-index_images.gif)

---

### Command-line Usage

```
usage: index_images.py [-h] [-n OUT_NAME] [-d OUT_DIR] [--no-list] [dir_name]

Create an HTML index of images.

positional arguments:
  dir_name              Name of the directory to scan for image files (*.png
                        and *.jpg). Optional. If not specified, the current
                        working directory is scanned.

optional arguments:
  -h, --help            show this help message and exit
  -n OUT_NAME, --name OUT_NAME
                        Name of the output HTML file. Optional. If not
                        specified, the file is named 'images-index.html'.
  -d OUT_DIR, --out-dir OUT_DIR
                        Directory in which to create the output HTML file.
                        Optional. If not specified, the file is written to the
                        same directory as is scanned for image files.
  --no-list             Do not include a Contents section listing links to
                        each image.
```
