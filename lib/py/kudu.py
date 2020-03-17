import logging
import requests
import traceback


class KuduClient:
    """
    https://github.com/projectkudu/kudu/wiki/REST-API
    """

    def __init__(self, url, user, passwd):
        self.url = (
            url.replace("http://", "https://").replace(
                "azurewebsites", "scm.azurewebsites"
            )
            + "/api/"
        )
        self.auth = (user, passwd)
        logging.debug(f"URL: {url}")
        logging.debug(f"KUDU URL: {self.url}")
        logging.debug(f"USER: {user}, PASS: {passwd}")

    def get_endpoint(self, endpoint):
        try:
            response = requests.get(self.url + endpoint, auth=self.auth)
            if response.ok:
                return response.json()
            logging.error(
                f"Failed to run {cmd} on {self.url}\n"
                + f"Code:{response.status_code}\n"
                + f"Response: {response.text}"
            )
        except Exception as error:
            logging.error(f"Failed to get {endpoint} from {self.url}: {error}")
            logging.debug(traceback.format_exc())

    def run_cmd(self, cmd, cwd):
        logging.debug(f"Running {cmd} on {self.url}...")
        payload = {"command": cmd, "dir": cwd}
        try:
            response = requests.post(self.url + "command", auth=self.auth, json=payload)
            if response.ok:
                return response.json()
            logging.error(
                f"Failed to run {cmd} on {self.url}\n"
                + f"Code:{response.status_code}\n"
                + f"Response: {response.text}"
            )
        except Exception as error:
            logging.error(f"Failed to run {cmd} on {self.url}: {error}")
            logging.debug(traceback.format_exc())
