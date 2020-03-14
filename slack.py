#!/usr/bin/env python

import requests
import logging
from argparse import ArgumentParser
from configparser import ConfigParser
from os.path import expanduser
from sys import exit, stdout
from lib.py.slack import SlackClient


def make_log(verbosity):
    if verbosity > 1:
        loglevel = logging.DEBUG
        logformat = "%(asctime)s %(threadName)s %(levelname)s %(message)s"
    elif verbosity == 1:
        loglevel = logging.INFO
        logformat = "%(asctime)s %(levelname)s %(message)s"
    else:
        loglevel = logging.WARNING
        logformat = "%(levelname)s %(message)s"
        logging.basicConfig(
            # filename='',
            format=logformat,
            datefmt="%Y-%m-%d %H:%M:%S",
            level=loglevel,
            stream=stdout,
        )


def get_token():
    try:
        config = ConfigParser()
        config.read(f'{expanduser("~")}/.slack.token')
        token = config["slack"]["token"]
    except Exception as error:
        logging.error(f"Failed to retrieve token from ~/.slack.token. Aborting.")
        exit(1)

    if token:
        return token

    logging.error(f"Failed to retrieve token from ~/.slack.token. Aborting.")
    exit(1)


def get_args():
    parser = ArgumentParser()

    parser.add_argument(
        "-c", "--channel", default="test-channel", help="send a slack command",
    )
    parser.add_argument(
        "-g", "--get_messages", action="store_true", help="get messages from channel",
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=10, help="number of messages to retrieve",
    )
    parser.add_argument(
        "-p", "--post_message", help="a message to post to slack",
    )
    parser.add_argument(
        "-s", "--send_command", nargs=2, help="send a slack command",
    )
    parser.add_argument(
        "-t", "--token", default=get_token(), nargs=2, help="send a slack command",
    )
    parser.add_argument(
        "-u", "--user", default="Slack Bot", help="send a slack command",
    )
    parser.add_argument(
        "-v", "--verbosity", action="count", default=0, help="increase output verbosity"
    )

    return parser.parse_args()


if __name__ == "__main__":
    """
    Put your Slack token in $HOME/.slack.token in this format:

    [slack]
    token = your-super-long-token-string

    Or pass it in as a command line option. It's up to you.
    """
    args = get_args()
    make_log(args.verbosity)
    slack = SlackClient(args.token, args.channel, args.user)

    if args.post_message:
        slack.post_message(args.post_message)
    elif args.get_messages:
        print("\n".join(slack.get_messages(args.limit)))
    elif args.send_command:
        slack.send_command(args.send_command)
