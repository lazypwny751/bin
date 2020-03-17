#!/usr/bin/env python
import logging
import sys
from argparse import ArgumentParser
from configparser import ConfigParser
from os.path import expanduser
from lib.py.azure import get_jwt, get_creds
from lib.py.kudu import KuduClient


def get_args():
    parser = ArgumentParser()
    parser.add_argument("-a", "--app", help="azure app name")
    parser.add_argument(
        "--config",
        default=f"{expanduser('~')}/.kudu.ini",
        help="path to azure configuration",
    )
    parser.add_argument("-r", "--resource_group", help="azure resource group")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--cmd", help="command to run")
    group.add_argument("-e", "--endpoint", help="view api endpoint")
    parser.add_argument(
        "-p", "--cwd", default="site\\wwwroot", help="remote current working directory"
    )
    parser.add_argument("-v", action="count", default=0, help="increase verbosity")
    return parser.parse_args()


def get_az_details(path):
    try:
        config = ConfigParser()
        config.read(path)
        az_details = config["azure"]
    except Exception as error:
        logging.error(f"Failed to retrieve config from {path}. Aborting.")
        logging.error(error)
        sys.exit(1)

    if az_details:
        logging.debug(f"Found {path}")
        logging.debug(az_details)
        return az_details

    logging.error(f"Failed to retrieve Azure details from {path}. Aborting.")
    sys.exit(1)


def mklog(verbosity):
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
        stream=sys.stdout,
    )


if __name__ == "__main__":
    args = get_args()
    mklog(args.v)

    az = get_az_details(args.config)
    az["rg"] = args.resource_group

    jwt = get_jwt(az["client_id"], az["client_secret"], az["tenant_id"])
    creds = get_creds(az["sub_id"], az["rg"], args.app, jwt)
    kudu = KuduClient(creds["web_url"], creds["web_user"], creds["web_passwd"])

    if args.cmd:
        kudu.run_cmd(args.cmd, args.cwd)
    elif args.endpoint:
        kudu.get_endpoint(args.endpoint)
