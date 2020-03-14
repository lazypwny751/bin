import requests
import logging


class SlackClient:
    def __init__(self, token, channel="test-channel", user="Slack Bot"):
        self.url = "https://slack.com/api/"
        self.token = token
        self.chaname = channel
        self.channel = self.__get_channel_id(channel)
        self.user = user
        self.params = {
            "username": user,
            "token": self.token,
            "channel": self.channel,
            "link_names": True,
        }

    def __get_channels(self):
        logging.debug(f"Getting all Slack channels...")
        response = requests.get(
            self.url + "conversations.list", params={"token": self.token},
        )
        channels = response.json()["channels"]
        channel_names = [chan["name"] for chan in response.json()["channels"]]
        logging.debug(f"Slack channels: " + ", ".join(channel_names))
        return channels

    def __get_channel_id(self, channel_name):
        logging.debug(f"Looking for {channel_name} channel...")
        channels = self.__get_channels()
        channel_id = [ch["id"] for ch in channels if ch["name"] == channel_name][0]
        logging.debug(f"{channel_name} = {channel_id}")
        return channel_id

    def __get_channel_messages(self, limit=10):
        params = self.params
        params["limit"] = limit
        response = requests.get(self.url + "conversations.history", params=params)
        return response.json()["messages"]

    def get_messages(self, limit=10):
        logging.info(f"Retrieving Slack messages from {self.chaname}...")
        messages = self.__get_channel_messages(limit)
        return [msg["text"] for msg in messages]

    def post_message(self, message):
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
