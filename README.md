## Inspect Google Application Default Credentials Tokens

Simple script which prints out the principal/user currently enabled for [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)


If you want a standalone script without importing the library, see the `example/manual.py` script in this repo


- `stsinspect.py`

```python
from gcp_adc_util.inspect import ADCInspect

p = ADCInspect()

print(p.getProjectID())
print(p.getPrincipal())
```

---

>> requires `Python3.11+` 

---

### User

```bash
gcloud auth application-default login

$ python3 stsinspect.py 
   admin@domain.com
```

### With ServiceAccount JSON

```bash
$ export GOOGLE_APPLICATION_CREDENTIALS=/path/to/svc-account.json

$ python stsinspect.py 
svc-account@PROJECT.iam.gserviceaccount.com
```

### With GCE Metadata Server

```bash
python3 stsinspect.py 
  708288290784-compute@developer.gserviceaccount.com
```

### With GCE Metadata Server Emulator

https://github.com/salrashid123/gce_metadata_server

```bash
export GCE_METADATA_HOST=localhost:8080
python3 stsinspect.py 
```


### Workload Federation OIDC using curl

```bash
export BASIC_AUTH_HEADER="MzI1NTU5NDA1NTkuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb206Wm1zc0xOakp5Mjk5OGhENENUZzJlanIy"

STS_TOKEN_INSPECT=$(curl -s https://sts.googleapis.com/v1/token -H "Authorization: Basic $BASIC_AUTH_HEADER" \
    --data-urlencode "audience=//iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/providers/$PROVIDER_ID" \
    --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
    --data-urlencode "requested_token_type=urn:ietf:params:oauth:token-type:access_token" \
    --data-urlencode "scope=https://www.googleapis.com/auth/cloud-platform" \
    --data-urlencode "subject_token_type=urn:ietf:params:oauth:token-type:jwt" \
    --data-urlencode "subject_token=$SUBJECT_TOKEN" | jq -r .access_token)
echo $STS_TOKEN_INSPECT

curl -s -H "Authorization: Basic $BASIC_AUTH_HEADER" -H "Content-Type: application/json" --data "{\"token\":\"$STS_TOKEN_INSPECT\"}" https://sts.googleapis.com/v1/introspect
```

### Workload federation OIDC

see [Simple GCP OIDC workload Federation using a fake oidc server](https://gist.github.com/salrashid123/677866e42cf2785fe885ae9d6130fc21)

```bash
$ cat sts-creds.json 
{
  "universe_domain": "googleapis.com",
  "type": "external_account",
  "audience": "//iam.googleapis.com/projects/995081019036/locations/global/workloadIdentityPools/fake-oidc-pool-1/providers/fake-oidc-provider-1",
  "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
  "token_url": "https://sts.googleapis.com/v1/token",
  "credential_source": {
    "file": "/tmp/oidccred.txt",
    "format": {
      "type": "text"
    }
  },
  "token_info_url": "https://sts.googleapis.com/v1/introspect"
}


$ export GOOGLE_APPLICATION_CREDENTIALS=`pwd`/sts-creds.json
$ python3 stsinspect.py 
   principal://iam.googleapis.com/projects/995081019036/locations/global/workloadIdentityPools/fake-oidc-pool-1/subject/alice@domain.com
```

### Workload Federation mTLS

```bash
$ cat sts-creds-mtls.json 
{
  "universe_domain": "googleapis.com",
  "type": "external_account",
  "audience": "//iam.googleapis.com/projects/995081019036/locations/global/workloadIdentityPools/cert-pool-1/providers/cert-provider-1",
  "subject_token_type": "urn:ietf:params:oauth:token-type:mtls",
  "token_url": "https://sts.mtls.googleapis.com/v1/token",
  "credential_source": {
    "certificate": {
      "certificate_config_location": "/pat/to/cert_config.json"
    }
  },
  "token_info_url": "https://sts.mtls.googleapis.com/v1/introspect"
}

$ export GOOGLE_APPLICATION_CREDENTIALS=`pwd`/sts-creds-mtls.json
$ python3 stsinspect.py 
  principal://iam.googleapis.com/projects/995081019036/locations/global/workloadIdentityPools/cert-pool-1/subject/workload3
```

### Workload Federation with service_account_impersonation_url

```bash
$ cat sts-creds-mtls-impersonation.json 
{
  "universe_domain": "googleapis.com",
  "type": "external_account",
  "audience": "//iam.googleapis.com/projects/995081019036/locations/global/workloadIdentityPools/cert-pool-1/providers/cert-provider-1",
  "subject_token_type": "urn:ietf:params:oauth:token-type:mtls",
  "token_url": "https://sts.mtls.googleapis.com/v1/token",
  "credential_source": {
    "certificate": {
      "certificate_config_location": "/path/to/cert_config.json"
    }
  },
  "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/wif-svc@core-eso.iam.gserviceaccount.com:generateAccessToken",
  "token_info_url": "https://sts.mtls.googleapis.com/v1/introspect"
}

$ export GOOGLE_APPLICATION_CREDENTIALS=`pwd`/sts-creds-mtls-impersonation.json

$ python3 stsinspect.py 
  wif-svc@core-eso.iam.gserviceaccount.com
```

### Workforce Federation SAML

```bash
$ cat saml-creds.json 
{
  "universe_domain": "googleapis.com",
  "type": "external_account",
  "audience": "//iam.googleapis.com/locations/global/workforcePools/wfpool-saml/providers/wfprovider-saml",
  "subject_token_type": "urn:ietf:params:oauth:token-type:saml2",
  "token_url": "https://sts.googleapis.com/v1/token",
  "credential_source": {
    "file": "/tmp/samlassertion.txt",
    "format": {
      "type": "text"
    }
  },
  "workforce_pool_user_project": "core-eso",
  "token_info_url": "https://sts.googleapis.com/v1/introspect"
}

$ export GOOGLE_APPLICATION_CREDENTIALS=`pwd`/saml-creds.json
$ python3 stsinspect.py 
  principal://iam.googleapis.com/locations/global/workforcePools/wfpool-saml/subject/alice@domain.com
```


### Workload Federation with AWS

see
[GCP Workload Identity Federation using AWS Credentials](https://github.com/salrashid123/gcpcompat-aws)

```bash
$ cat sts-creds-aws.json
{
    "universe_domain": "googleapis.com",    
    "type": "external_account",
    "audience": "//iam.googleapis.com/projects/995081019036/locations/global/workloadIdentityPools/aws-pool-1/providers/aws-provider-1",
    "subject_token_type": "urn:ietf:params:aws:token-type:aws4_request",
    "token_url": "https://sts.googleapis.com/v1/token",
    "credential_source": {
      "environment_id": "aws1",
      "region_url": "http://169.254.169.254/latest/meta-data/placement/availability-zone",
      "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials",
      "regional_cred_verification_url": "https://sts.{region}.amazonaws.com?Action=GetCallerIdentity&Version=2011-06-15"
    },
    "token_info_url": "https://sts.googleapis.com/v1/introspect"    
}

export AWS_ACCESS_KEY_ID=AKIAUH-redacted
export AWS_SECRET_ACCESS_KEY=lIs-redacted
export AWS_DEFAULT_REGION=us-east-2

$  aws sts get-caller-identity
{
    "UserId": "AIDAUH-redacted",
    "Account": "291738886548",
    "Arn": "arn:aws:iam::291738886548:user/svcacct1"
}


$ export GOOGLE_APPLICATION_CREDENTIALS=`pwd`/sts-creds-aws.json
$ python3 stsinspect.py 
  principal://iam.googleapis.com/projects/995081019036/locations/global/workloadIdentityPools/aws-pool-1/subject/arn:aws:iam::291738886548:user/svcacct1
```

### Workload Federation with Azure

see [Exchange Google and Firebase OIDC tokens for Azure STS](https://github.com/salrashid123/azcompat)



TODO: incorporate into [gcloud alias for Application Default Credentials](https://github.com/salrashid123/gcloud_alias_adc)
