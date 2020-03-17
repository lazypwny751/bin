import json
import logging
import re
import requests
import traceback
from azure.common.credentials import ServicePrincipalCredentials
from bs4 import BeautifulSoup


def get_access_token(client_id, secret, tentant):
    try:
        credentials = ServicePrincipalCredentials(
            client_id=client_id, secret=secret, tenant=tentant,
        )
        access_token = credentials.token["access_token"]
        logging.debug(f"Access Token:\n\n{access_token}\n")
        return access_token
    except Exception as error:
        logging.debug(traceback.format_exc())
        raise error


def get_publish_profile(sub, rg, app, jwt):
    """
    Get FTP and Web App credentials (username, password, hostname)
    https://docs.microsoft.com/en-us/rest/api/appservice/webapps/listpublishingprofilexmlwithsecrets
    """
    url = (
        f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}"
        + f"/providers/Microsoft.Web/sites/{app}/publishxml"
    )
    headers = {"Authorization": f"Bearer {jwt}"}
    params = {"api-version": "2016-08-01"}

    try:
        response = requests.post(url, headers=headers, params=params)

        if response.ok:
            soup = BeautifulSoup(response.text, features="html.parser")
            logging.debug(f"Response XML:\n\n{soup.prettify()}\n")

            web_pp = soup.select("publishProfile")[0]
            ftp_pp = soup.select("publishProfile")[1]
            ftp_host = re.search(
                r"ftp:\/\/(.*)/site/wwwroot", ftp_pp["publishurl"], re.IGNORECASE
            ).group(1)

            publish_profile = {
                "web_url": web_pp["destinationappurl"],
                "web_user": web_pp["username"],
                "web_passwd": web_pp["userpwd"],
                "ftp_host": ftp_host,
                "ftp_user": ftp_pp["username"],
                "ftp_passwd": ftp_pp["userpwd"],
            }

            logging.debug("Publish Profile:\n" + json.dumps(publish_profile, indent=2))
            return publish_profile

        logging.debug(f"Subscription ID: {sub}")
        logging.debug("\n" + json.dumps(response.json(), indent=2, sort_keys=True))
        raise AssertionError(f"{response.json()['error']['message']}")
    except Exception as error:
        logging.debug(traceback.format_exc())
        raise error
