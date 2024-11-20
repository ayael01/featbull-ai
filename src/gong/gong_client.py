import base64
import logging

import requests

from src.schemas.schemas import CallResponse


class GongClient:
    logger = logging.getLogger(__name__)

    def __init__(self, username: str, password: str):
        self.base_url = 'https://api.gong.io/v2'
        self.headers = {
            'Authorization': f'Basic {self.generate_auth_token(username, password)}'
        }

    @staticmethod
    def generate_auth_token(username: str, password: str) -> str:
        token = base64.b64encode(f'{username}:{password}'.encode()).decode()
        return token

    def get_transcription(self, call_ids: list):
        url = f'{self.base_url}/calls/transcript'
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'
        data = {
            "filter": {
                "callIds": call_ids
            }
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            self.logger.error(
                'Error while getting gong calls %s - %s', response.status_code, response.text)
            response.raise_for_status()

    def get_extensive_calls(self):
        url = f'{self.base_url}/calls/extensive'
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'
        data = {
            "contentSelector": {
                "context": "Extended"
            },
            "filter": {
                "fromDateTime": "2024-11-01T23:59:00-08:00",
                "toDateTime": "2024-12-01T23:59:00-08:00",
            }
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            gong_response = response.json()
            transformed_response:list[CallResponse] = []
            for call in gong_response.get('calls', []):
                customer_name = None
                for field in call.get('context', [])[0].get('objects', [])[0].get('fields', []):
                    if field.get('name') == 'Name':
                        customer_name = field.get('value')
                        break
                transformed_response.append(CallResponse(
                    id=call.get('metaData', {}).get('id'),
                    title=call.get('metaData', {}).get('title'),
                    started=call.get('metaData', {}).get('started'),
                    customer_name=customer_name  # type: ignore
                ))
            return transformed_response
        else:
            self.logger.error(
                'Error while getting extensive calls %s - %s', response.status_code, response.text)
            response.raise_for_status()
