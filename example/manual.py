#!/usr/bin/python

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

from requests.exceptions import HTTPError

# import logging
# import http
# http.client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

credentials, project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform","https://www.googleapis.com/auth/userinfo.email"])

identity = None

try:
    match type(credentials):
        case google.auth.identity_pool.Credentials | google.auth.external_account.Credentials | google.auth.aws.Credentials:
            # b64encode("32555940559.apps.googleusercontent.com:ZmssLNjJy2998hD4CTg2ejr2")
            headers = {'Authorization': 'Basic MzI1NTU5NDA1NTkuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb206Wm1zc0xOakp5Mjk5OGhENENUZzJlanIy'}            
            s = requests.Session()            
            s.headers.update(headers)
            request = google.auth.transport.requests.Request(session=s)
            credentials._workforce_pool_user_project = ''
            credentials.refresh(request)

            if credentials._service_account_impersonation_url is not None:
              r = s.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": credentials.token})
              if r.status_code != 200:
                  raise Exception("error getting tokeninfo + " + r.text)
              identity = r.json()['email']
            else:
              if credentials._subject_token_type == "urn:ietf:params:oauth:token-type:mtls":
                try:
                  loc = credentials._credential_source['certificate']['certificate_config_location']
                  with open(loc) as f:
                    data = json.load(f)
                    cert = data['cert_configs']['workload']['cert_path']
                    key = data['cert_configs']['workload']['key_path']
                except OSError as e:
                  raise Exception("Error reading key file: " + str(e))
                except KeyError as e:
                  raise Exception("Error parsing cert_config field: " + str(e))
                r = s.post(credentials._token_info_url, headers=headers, json={"token": credentials.token}, cert=(cert,key))
              else:
                r = s.post(credentials._token_info_url, headers=headers, json={"token": credentials.token})
              if r.status_code != 200:
                raise Exception("error getting tokeninfo + " + r.text)
              identity = r.json()['username']
        case google.oauth2.service_account.Credentials | google.oauth2.credentials.Credentials | google.auth.impersonated_credentials.Credentials:
            s = requests.Session()
            request = google.auth.transport.requests.Request(session=s)
            credentials.refresh(request)
            r = s.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": credentials.token})
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
            raise Exception("Unknown credential type " + str(type(credentials)))
except HTTPError as e:
    print(e.response.text)

if identity is None:
  print('no adc set')
else:
  print(identity)
