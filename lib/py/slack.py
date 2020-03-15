import requests
import logging


class SlackClient:
    """
    Do funky Slack stuff :-)
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, token, channel_name="test-channel", user="Slack Bot"):
        self.url = "https://slack.com/api/"
        self.token = token
        self.channel_name = channel_name
        self.channels = self.get_channels_json()
        self.channel_names = [channel["name"] for channel in self.channels]
        self.channel_id = [
            channel["id"]
            for channel in self.channels
            if channel["name"] == self.channel_name
        ][0]
        self.user = user
        self.params = {
            "username": user,
            "token": self.token,
            "channel": self.channel_id,
            "link_names": True,
        }

    def get_channels_json(self):
        """
        Retrieve channel json objects.
        """
        logging.debug(f"Getting all Slack channels...")
        response = requests.get(
            self.url + "conversations.list", params={"token": self.token},
        )
        return response.json()["channels"]

    def get_messages_json(self, limit=10):
        """
        Retrieve messages json objects.
        """
        params = self.params
        params["limit"] = limit
        response = requests.get(self.url + "conversations.history", params=params)
        return response.json()["messages"]

    def get_messages(self, limit=10):
        """
        Retrieve message strings from Slack.
        """
        logging.info(f"Retrieving Slack messages from {self.channel_name}...")
        messages = self.get_messages_json(limit)
        return [msg["text"] for msg in messages]

    def post_message(self, message):
        """
        Post a message to Slack.
        """
        logging.info(f"Posting {message} to {self.channel}...")
        params = self.params
        params["text"] = message
        response = requests.get(self.url + "chat.postMessage", params=params)
        if response.ok:
            logging.info(f'Successfully sent "{message}" to {self.channel}.')
            logging.debug(response.json())
        else:
            logging.info(f'Failed to send "{message}" to {self.channel}.')
            logging.debug(response.json())
        return response.status_code

    def send_command(self, command):
        """
        This doesn't actually appear to work despite returning a 200 status code...

        https://github.com/ErikKalkoken/slackApiDoc/blob/master/chat.command.md
        """
        cmd, arg = command
        logging.debug(f'Sending "/{cmd} {arg}" to {self.channel}...')
        params = self.params
        params["command"] = f"/{cmd}"
        params["text"] = arg
        response = requests.get(self.url + "chat.command", params=params)
        if response.ok:
            logging.info(f'Successfully sent "/{cmd} {arg}" to {self.channel}.')
            logging.debug(response.json())
        else:
            logging.info(f'Failed to send "/{cmd} {arg}" to {self.channel}.')
            logging.debug(response.json())
        return response.status_code
