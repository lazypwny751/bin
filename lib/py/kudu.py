import json
import logging
import requests
import traceback
from assertpy import assert_that


def get_kudu_url(url):
    url = url.replace("http://", "https://")
    url = url.replace("azurewebsites", "scm.azurewebsites")
    url = url + f"/api/"
    logging.debug(url)
    return url


class KuduClient:
    """
    https://github.com/projectkudu/kudu/wiki/REST-API
    """

    def __init__(self, url, user, passwd):
        self.url = get_kudu_url(url)
        self.auth = (user, passwd)
        logging.debug(f"USER: {user}, PASS: {passwd}")

    def get_endpoint(self, endpoint):
        try:
            response = requests.get(self.url + endpoint, auth=self.auth)
            assert_that(response.status_code).is_equal_to(200)
            logging.debug(response.json())
            return response.text
        except Exception as error:
            logging.error(f"Failed to get {endpoint} from {self.url}: {error}")
            logging.debug(traceback.format_exc())

    def run_cmd(self, cmd, cwd):
        logging.debug(f"Running {cmd} on {self.url}...")
        payload = {"command": cmd, "dir": cwd}
        try:
            response = requests.post(self.url + "command", auth=self.auth, json=payload)
            response_text = json.loads(response.text)
            assert_that(response.status_code).is_equal_to(200)

            if response_text["ExitCode"] == 0:
                logging.info(f"Successfully ran {cmd} on {self.url}.")
            else:
                logging.error(
                    f"Failed to run {cmd} on {self.url}:\n"
                    + f"Exitcode: {response_text['ExitCode']}\n"
                    + f"Message: {response_text['Error']}"
                )

            if response_text["Output"]:
                logging.info(f"Command output:\n{response_text['Output']}")
        except Exception as error:
            logging.error(f"Failed to run {cmd} on {self.url}: {error}")
            logging.debug(traceback.format_exc())
