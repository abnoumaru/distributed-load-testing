import json
import logging
import os
import time

from locust import HttpUser, TaskSet, task
import google.auth
from google.auth import iam
from google.auth.transport.requests import Request as GRequest
from google.oauth2.service_account import Credentials
import jwt
from jwt.algorithms import RSAAlgorithm

from requests import Session

IAM_SCOPE='https://www.googleapis.com/auth/iam'
OAUTH_TOKEN_URI='https://www.googleapis.com/oauth2/v4/token'

_oidc_token = None
_session =Session()
_adc_credentials, _ = google.auth.default(scopes=[IAM_SCOPE])

_signer = iam.Signer(
    GRequest(), _adc_credentials, _adc_credentials.service_account_email)

class OIDCToken(object):

    def __init__(self, token_str):
        self._token_str = token_str
        self._claims = jwt.decode(token_str, verify=False, algorithms=['RS256'])

    def __str__(self):
        return self._token_str

    def is_expired(self):
        return int(time.time()) >= self._claims['exp']

def get_google_oidc_token():

    credentials = Credentials(
        _signer, _adc_credentials.service_account_email,
        token_uri=OAUTH_TOKEN_URI,
        additional_claims={'target_audience': os.getenv('CLIENT_ID')}
    )
    service_accunt_jwt = credentials._make_authorization_grant_assertion()
    request = GRequest()
    body = {
        'assertion': service_accunt_jwt,
        'grant_type': google.oauth2._client._JWT_GRANT_TYPE,
    }
    token_response = google.oauth2._client._token_endpoint_request(
        request, OAUTH_TOKEN_URI, body)

    return OIDCToken(token_response['id_token'])

class IapTasks(TaskSet):
    @task(1)
    def health(self):

        global _oidc_token
        if not _oidc_token:
            _oidc_token = get_google_oidc_token()
            logging.info('Renewed OIDC bearer token for {}'.format(
                _adc_credentials.service_account_email))

        payload = dict()
        payload['Authorization'] = 'Bearer {}'.format(str(_oidc_token))
        
        self.client.get("/health",headers=payload)

class IapWarmer(HttpUser):
    tasks = [IapTasks]
    min_wait = 1000
    max_wait = 3000
