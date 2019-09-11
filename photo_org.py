import argparse
import os
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS


def chkpath(path):
    """
    Checks for valid directory path.
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            msg = "{0} is not a directory.".format(path)
    else:
        msg = "{0} does not exist.".format(path)

    raise argparse.ArgumentTypeError(msg)


def getargs():
    """
    Return a list of valid arguments. If no argument is given, default to $PWD.
    """
    parser = argparse.ArgumentParser(
        description='Remove invalid characters from a given path.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--interactive", action="store_true",
                       help="prompt before renaming each path")
    group.add_argument("-a", "--automate", action="store_true",
                       help="rename each path without prompting")
    group.add_argument("-t", "--dry_run", action="store_true",
                       help="preform a dry run to see what would be renamed")
    group.add_argument("-q", "--quiet", action="store_true",
                       help="run silently")
    group.add_argument("-f", "--find", action="store_true",
                       help="print a list of invalid paths")
    parser.add_argument("path", type=chkpath, nargs='?',
                        default=".", help="a valid path")
    return parser.parse_args()


def get_exiftags(path):
    exiftags = {}

    try:
        img = Image.open(path)
        if hasattr(img, '_getexif'):
            exifdata = img._getexif()
        else:
            return

        if exifdata and exifdata != 'None':
            for tag, value in exifdata.items():
                tagname = TAGS.get(tag)
                exiftags[tagname] = value
        else:
            return

    except IOError:
        print("IOError accessing {}".format(path))

    return exiftags


def get_date(path):
    exiftags = get_exiftags(path)
    exifdate = "DateTimeOriginal"

    if exiftags:
        if exifdate in exiftags:
            date = datetime.strptime(exiftags[exifdate], '%Y:%m:%d %H:%M:%S')
            date = datetime.strftime(date, '%Y-%m-%d_%H-%M-%S')
            return date
        else:
            return "NO " + exifdate + " TAG"
    else:
        return "NO EXIFTAGS"


def main():
    args = getargs()
    path = os.path.abspath(args.path)

    images = []
    videos = []

    imgext = (
        "*.[jJ][pP][gG]",
        "*.[jJ][pP][eE][gG]",
        "*.[pP][nN][gG]",
        "*.[gG][iI][fF]",
    )
    vidext = (
        "*.[mM][pP][4]",
        "*.[mM][4][vV]",
        "*.[mM][oO][vV]",
    )

    for ext in imgext:
        images = images + list(Path(path).rglob(ext))

    for ext in vidext:
        videos = videos + list(Path(path).rglob(ext))

    for img in images:
        date = get_date(img)
        print("{} = {}".format(img, date))

    for vid in videos:
        # https://stackoverflow.com/a/52492906
        date = get_date(vid)


if __name__ == '__main__':
    main()
