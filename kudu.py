#!/usr/bin/env python
import json
import logging
import os
import sys
from argparse import ArgumentParser, ArgumentTypeError
from configparser import ConfigParser
from lib.py.azure import get_access_token, get_publish_profile
from lib.py.kudu import KuduClient


def chkpath(path):
    if os.path.exists(path):
        return os.path.abspath(path)

    raise ArgumentTypeError(f"{path} does not exist.")


def get_args():
    parser = ArgumentParser()
    parser.add_argument("-a", "--app", help="azure app name")
    parser.add_argument(
        "--config",
        type=chkpath,
        default=f"{os.path.expanduser('~')}/.kudu.ini",
        help="path to azure configuration file",
    )
    parser.add_argument("-r", "--resource_group", help="azure resource group")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-c", "--cmd", help="command to run (use quotes for multi-word commands)"
    )
    group.add_argument("-e", "--endpoint", help="view api endpoint")
    group.add_argument("-z", "--zipdeploy", type=chkpath, help="deploy a zip file")
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
        logging.info(f"Found Azure configuration at {path}.")
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

    try:
        az = get_az_details(args.config)
        token = get_access_token(az["client_id"], az["secret"], az["tenant"])
        pp = get_publish_profile(az["sub_id"], args.resource_group, args.app, token)
        kudu = KuduClient(pp["web_url"], pp["web_user"], pp["web_passwd"])
    except Exception as error:
        logging.error(error)
        sys.exit(1)

    if args.cmd:
        response = kudu.run_cmd(args.cmd, args.cwd)
        logging.debug("Output:\n" + json.dumps(response, indent=2, sort_keys=True))
        if response["ExitCode"] == 0:
            logging.info(f"Ran '{args.cmd}' in {pp['web_url']}/{args.cwd}.")
            print(response["Output"].strip())
        else:
            logging.error(
                f"Failed to run '{args.cmd}' in {pp['web_url']}/{args.cwd}\n"
                + f"Exitcode: {response['ExitCode']} "
                + f"Message: {response['Error']}".strip()
            )
    elif args.endpoint:
        response = kudu.get_endpoint(args.endpoint)
        if response:
            logging.info(f"{kudu.url}{args.endpoint}:")
            print(json.dumps(response, indent=2, sort_keys=True))
        else:
            logging.info(f"{kudu.url}{args.endpoint} returned no data.")
    elif args.zipdeploy:
        print(f"Deploying {args.zipdeploy} to {pp['web_url']}.. ", end="", flush="True")
        response = kudu.deploy_zip(args.zipdeploy)
        if response == 200:
            print(f"DONE.")
        else:
            print(f"FAIL.")
            logging.warning(
                f"Deploying {args.zipdeploy} to {pp['web_url']}. Status: {response}."
            )
