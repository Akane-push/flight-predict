from dotenv import load_dotenv
import os
import requests
import json

# Load from .env file
load_dotenv()

class LufthansaAPI:
    def __init__(self):
        self.client_id = os.getenv("Lufth_client_id")
        self.client_secret = os.getenv("Lufth_client_secret")
        self.url = "https://api.lufthansa.com/v1"
        self.token = None
        self.token = self.get_token()

    # Token retrieval method
    def get_token(self):
        url = f"{self.url}/oauth/token"
        response = requests.post(url, data={
                                                'client_id': self.client_id,
                                                'client_secret': self.client_secret,
                                                'grant_type': 'client_credentials'
                                            })
        if response.status_code == 200:
            self.token = response.json()['access_token']
            print("[INFO] Successfully authenticated with Lufthansa API.")
            return self.token
        else:
            raise ValueError(f"[ERROR] : {response.status_code} - {response.text}")



if __name__ == "__main__":
    lufthansa_api = LufthansaAPI()
    token = lufthansa_api.get_token()
    print(f"Token d'accès : {lufthansa_api.token}")



#401 token invalid