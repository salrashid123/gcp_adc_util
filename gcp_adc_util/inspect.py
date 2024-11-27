import os, json

import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import google.oauth2.service_account
import google.auth.identity_pool
import google.auth.external_account
import google.auth.compute_engine.credentials
import google.auth.impersonated_credentials
import google.auth.aws
import requests

import logging
import http
from base64 import b64encode

from requests.exceptions import HTTPError

class ADCInspect():

    def __init__(
        self,
        debug=False, 
        client_id='32555940559.apps.googleusercontent.com',
        client_secret='ZmssLNjJy2998hD4CTg2ejr2'     
    ):


        self._debug = debug
        self._client_id = client_id
        self._client_secret = client_secret

        if self._debug:
            http.client.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

        self._credentials, self._project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform","https://www.googleapis.com/auth/userinfo.email"])
        
    def getProjectID(self):
       return self._project_id
    
    def _basic_auth(self,username, password):
      token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
      return f'Basic {token}'

    
    def getPrincipal(self):
          identity = None
          try:
              match type(self._credentials):
                  case google.auth.identity_pool.Credentials | google.auth.external_account.Credentials | google.auth.aws.Credentials:
                      auth_header = self._basic_auth(self._client_id, self._client_secret)
                      headers = {'Authorization': auth_header}            
                      s = requests.Session()            
                      s.headers.update(headers)
                      request = google.auth.transport.requests.Request(session=s)
                      self._credentials._workforce_pool_user_project = ''
                      self._credentials.refresh(request)

                      if self._credentials._service_account_impersonation_url is not None:
                        r = s.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": credentials.token})
                        if r.status_code != 200:
                            raise Exception("error getting tokeninfo + " + r.text)
                        identity = r.json()['email']
                      else:
                        if self._credentials._subject_token_type == "urn:ietf:params:oauth:token-type:mtls":
                          try:
                            loc = self._credentials._credential_source['certificate']['certificate_config_location']
                            with open(loc) as f:
                              data = json.load(f)
                              cert = data['cert_configs']['workload']['cert_path']
                              key = data['cert_configs']['workload']['key_path']
                          except OSError as e:
                            raise Exception("Error reading key file: " + str(e))
                          except KeyError as e:
                            raise Exception("Error parsing cert_config field: " + str(e))
                          r = s.post(self._credentials._token_info_url, headers=headers, json={"token": self._credentials.token}, cert=(cert,key))
                        else:
                          r = s.post(self._credentials._token_info_url, headers=headers, json={"token": self._credentials.token})
                        if r.status_code != 200:
                          raise Exception("error getting tokeninfo + " + r.text)
                        identity = r.json()['username']
                  case google.oauth2.service_account.Credentials | google.oauth2.credentials.Credentials | google.auth.impersonated_credentials.Credentials:
                      s = requests.Session()
                      request = google.auth.transport.requests.Request(session=s)
                      self._credentials.refresh(request)
                      r = s.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": self._credentials.token})
                      if r.status_code != 200:
                          raise Exception("error getting tokeninfo + " + r.text)
                      identity = r.json()['email']
                  case google.auth.compute_engine.credentials.Credentials:
                      headers = {'Metadata-Flavor': 'Google'}            
                      s = requests.Session()            
                      s.headers.update(headers)
                      request = google.auth.transport.requests.Request(session=s)
                      host = os.environ.get('GCE_METADATA_HOST','169.254.169.254:80')
                      r = s.get('http://' + host + '/computeMetadata/v1/instance/service-accounts/default/email', headers=headers)
                      if r.status_code != 200:
                          raise Exception("error getting tokeninfo + " + r.text)
                      identity = r.text
                  case _:
                      raise Exception("Unknown credential type " + str(type(self._credentials)))
          except HTTPError as e:
              raise Exception(e.response.text)

          if identity is None:
            raise Exception('no ADC set')
          else:
            return identity
