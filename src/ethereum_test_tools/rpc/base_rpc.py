"""
Base JSON-RPC class and helper functions for EEST based hive simulators.
"""
import time

import requests
from jwt import encode


class BaseRPC:
    """
    Represents a base RPC class for every RPC call used within EEST based hive simulators.
    """

    def __init__(self, client):
        self.client = client
        self.url = f"http://{client.ip}:8551"
        self.jwt_secret = (
            b"secretsecretsecretsecretsecretse"  # oh wow, guess its not a secret anymore
        )

    def generate_jwt_token(self):
        """
        Generates a JWT token based on the issued at timestamp and JWT secret.
        """
        iat = int(time.time())
        return encode({"iat": iat}, self.jwt_secret, algorithm="HS256")

    def post_request(self, method, params):
        """
        Sends a JSON-RPC POST request to the client RPC server at port 8551.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.generate_jwt_token()}",
        }
        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("result")
