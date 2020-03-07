#!/usr/bin/env python
import argparse
import logging
import os
import re
import sys


def chkpath(path):
    """
    Checks if a path exists.
    """
    if os.path.exists(path):
        return path
    else:
        msg = "{0} does not exist.".format(path)
        raise argparse.ArgumentTypeError(msg)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "gitroot",
        type=chkpath,
        nargs="?",
        default=f"{os.path.expanduser('~')}/src",
        help="path to look for Git repositories in",
    )
    parser.add_argument(
        "backup_dest",
        type=chkpath,
        nargs="?",
        default=f"{os.path.expanduser('~')}/Dropbox/Documents/gitbak",
        help="path leave backup archive in",
    )
    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="increase output verbosity"
    )
    return parser.parse_args()


def mklog(verbosity):
    if verbosity > 1:
        loglevel = logging.DEBUG
    elif verbosity == 1:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARNING
    logging.basicConfig(
        # filename='',
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=loglevel,
        stream=sys.stdout,
    )


if __name__ == "__main__":
    args = get_args()
    mklog(args.verbosity)
    logging.debug(f"GITROOT: {args.gitroot}, BACKUP_DEST: {args.backup_dest}")

    for root, dirs, files in os.walk(args.gitroot):
        logging.debug(f"Looking for git directories in {root}/{dirs}..")
        for d in dirs:
            if d == ".git":
                logging.info(f"Found {root}/{d}")
