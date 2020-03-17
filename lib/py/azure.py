import re
import requests
from assertpy import assert_that
from azure.common.credentials import ServicePrincipalCredentials
from bs4 import BeautifulSoup


def get_jwt(client_id, client_secret, tenant_id):
    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id,
    )
    return credentials.token["access_token"]


def get_creds(sub, rg, app, jwt):
    """
    Get FTP and Web App credentials (username, password, hostname)
    https://docs.microsoft.com/en-us/rest/api/appservice/webapps/listpublishingprofilexmlwithsecrets
    """
    url = (
        f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}"
        + f"/providers/Microsoft.Web/sites/{app}/publishxml"
    )
    headers = {"Authorization": f"Bearer {jwt}"}
    query_params = {"api-version": "2016-08-01"}
    response = requests.post(url, headers=headers, params=query_params)
    assert_that(response.status_code).is_equal_to(200)
    pch_soup = BeautifulSoup(response.text, features="html.parser")
    web_pp = pch_soup.select("publishProfile")[0]
    ftp_pp = pch_soup.select("publishProfile")[1]
    ftp_host = re.search(
        r"ftp:\/\/(.*)/site/wwwroot", ftp_pp["publishurl"], re.IGNORECASE
    ).group(1)
    return {
        "web_url": web_pp["destinationappurl"],
        "web_user": web_pp["username"],
        "web_passwd": web_pp["userpwd"],
        "ftp_host": ftp_host,
        "ftp_user": ftp_pp["username"],
        "ftp_passwd": ftp_pp["userpwd"],
    }
