import http
import json
from functools import cached_property

import requests
from external.apis.smartthings import exceptions
from external.apis.smartthings.commands import Command

# BASE_URL = "https://api.smartthings.com/v1/"
DEVICES = "devices"
CAPABILITIES = "capabilities"
COMMAND = "commands"
STATUS = "status"


class Api:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    @cached_property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def get(self, url: str):
        return requests.get(url=url, headers=self.headers)

    def post(self, url: str, payload: dict):
        data = json.dumps(payload)
        return requests.post(url=url, headers=self.headers, data=data)

    def devices(self):
        url = f"{self.base_url}{DEVICES}"
        response = self.get(url)
        return self.process_response(response)

    def device_status(self, device_id: str):
        url = f"{self.base_url}{DEVICES}/{device_id}/{STATUS}"
        response = self.get(url)
        return self.process_response(response)

    def capability(self, name: str):
        url = f"{self.base_url}{CAPABILITIES}/{name}/1"
        response = self.get(url)
        return self.process_response(response)

    def command(self, device_id: str, command: Command):
        url = f"{self.base_url}{DEVICES}/{device_id}/{COMMAND}"
        payload = command.to_dict()
        response = self.post(url=url, payload=payload)
        return self.process_response(response)

    @staticmethod
    def process_response(response):
        if response.status_code != http.HTTPStatus.OK:
            raise exceptions.SmartthingsApiException(response.text)
        return response.json()
