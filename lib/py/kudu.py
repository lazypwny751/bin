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

    def deploy_zip(self, path):
        """
        https://github.com/projectkudu/kudu/wiki/REST-API#zip-deployment

        Deploy from zip asynchronously. The Location header of the response
        will contain a link to a pollable deployment status.
        """
        try:
            with open(path, "rb") as f:
                zipfile = f.read()

            response = requests.put(
                self.url + "zipdeploy?isAsync=true", auth=self.auth, data=zipfile
            )

            if response.ok:
                while True:
                    logging.debug(f"Checking deployment {response.headers['Location']}")
                    status = requests.get(response.headers["Location"], auth=self.auth)
                    if status.json()["complete"]:
                        return status.json()
            else:
                raise AssertionError(
                    f"Deploying {path} on {self.url}zipdeploy\n"
                    + f"Code:{response.status_code}, Message: {response.text}"
                )
        except Exception as error:
            logging.error(f"Failed to deploy {path} from {self.url}zipdeploy: {error}")
            logging.debug(traceback.format_exc())

    def download_zip(self, source, destination):
        """
        https://github.com/projectkudu/kudu/wiki/REST-API#zip

        Zip up and download the specified folder. The zip doesn't include the
        top folder itself. Make sure you include the trailing slash!
        """
        try:
            response = requests.get(f"{self.url}zip/{source}", auth=self.auth)
            logging.debug(response.headers)
            zipbytes = response.content
            zipfile = open(destination, "wb")
            zipfile.write(zipbytes)
            zipfile.close()
            return response.ok
        except Exception as error:
            logging.error(
                f"Failed to download zip from {self.url}zip/{source}: {error}"
            )
            logging.debug(traceback.format_exc())

    def get_endpoint(self, endpoint):
        """
        https://github.com/projectkudu/kudu/wiki/REST-API
        """
        try:
            response = requests.get(self.url + endpoint, auth=self.auth)
            if response.ok:
                return response.json()
            raise AssertionError(
                f"Failed to get {endpoint} on {self.url}\n"
                + f"Code:{response.status_code}\n"
                + f"Response: {response.text}"
            )
        except Exception as error:
            logging.error(f"Failed to get {endpoint} from {self.url}: {error}")
            logging.debug(traceback.format_exc())

    def run_cmd(self, cmd, cwd):
        """
        https://github.com/projectkudu/kudu/wiki/REST-API#command
        """
        logging.debug(f"Running {cmd} on {self.url}...")
        payload = {"command": cmd, "dir": cwd}
        try:
            response = requests.post(self.url + "command", auth=self.auth, json=payload)
            if response.ok:
                return response.json()
            raise AssertionError(
                f"Failed to run {cmd} on {self.url}\n"
                + f"Code:{response.status_code}\n"
                + f"Response: {response.text}"
            )
        except Exception as error:
            logging.error(f"Failed to run {cmd} on {self.url}: {error}")
            logging.debug(traceback.format_exc())
