# sfPyAuth

A simple Python library for authenticating to Salesforce using OAuth.

## Features
* OAuth token management
* AWS Secret Manager or local `.tokens` file
* Access and Refresh tokens available for API calls by external modules/packages

## Setup

### Create Connected App for Authentication in Salesforce

Official Documentation from Salesforce for reference:
- [Create Connected App Basics](https://help.salesforce.com/s/articleView?id=xcloud.connected_app_create_basics.htm&type=5)
- [Create API Integration](https://help.salesforce.com/s/articleView?id=xcloud.connected_app_create_api_integration.htm&type=5)

My shorthand version:
1. Go to Setup Console -> App Manager -> New Connected App
2. Create a Connected App
3. Fill in details in Basic Information
4. Tick Enable API
5. Set Callback URL to `https://login.salesforce.com/services/oauth2/success`
6. Add the minimum required OAuth scopes:
    - Access Content Resources (content)
    - Access custom permissions (custom_permissions)
    - Full access (full)
    - Perform requests at any time (refresh token, offline_access)
7. Untick "Require Proof Key for Code Exchange (PKCE) Extension for Supported Authorization Flows."
8. Tick Require Secret for Web Server Flow
9. Tick Require Secret for Refresh Token Flow
10. Tick Enable Token Exchange
11. Tick Require Secret for Token Exchange Flow
12. Tick Enable Refresh Token Rotation

### Create your .env file

1. Copy `.env-template` and rename it to `.env`.
2. Update and set the `SF_CLIENT_ID`, `SF_CLIENT_SECRET` from the Connected App in Salesforce, and the username to the user you want to authenticate as.

#### Breakdown of .env settings

- `SF_CLIENT_ID`: The Consumer Key from your Salesforce Connected App.
- `SF_CLIENT_SECRET`: The Consumer Secret from your Salesforce Connected App.
- `SF_USERNAME`: The username of the Salesforce user you want to authenticate as.
- `SF_INSTANCE_URL`: (OPTIONAL) The instance URL of your Salesforce org (e.g., `https://login.salesforce.com`). This will usually autodetect.
- `SALESFORCE_API_VERSION`: (OPTIONAL) API version you want to use for authentication. This will usually autodetect.
- `SECRET_MANAGEMENT_TYPE`: The type of secret management to use. Options are `local` (default) or `aws`. Also planned is Azure.
- `AWS_ACCESS_KEY_ID`: Your AWS access key ID for AWS Secret Manager.
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key for AWS Secret Manager.
- `AWS_SESSION_TOKEN`: (OPTIONAL) Your AWS session token for AWS Secret Manager.
- `AWSSM_SECRET_NAME`: The name of the secret in AWS Secret Manager.
- `AWSSM_REGION_NAME`: The AWS region where your secret is stored.

## Usage

### Import and Instantiate

To use `sfPyAuth` as a library, import and instantiate the `oAuthController` class:

```python
from src.sfPyAuth.sfPyAuth import oAuthController

oauth = oAuthController()
```

### Authenticating When Required

If there is no usable token (first use, token missing/invalid/expired), you will need to authenticate to your Salesforce org again. This will be done as part of the library's initialization. The script will attempt to open your browser to the login page for your Connected App. The URL will also be displayed in the console.

Once you have authenticated, copy the URL from the browser and paste it into the console. The script will extract the secret code and proceed to save the required tokens.

### Secret Management

The `SecretManager` module handles the storage and retrieval of Salesforce tokens. It supports local file storage and AWS Secret Manager.

Currently, both a local `.tokens` file and AWS Secret Manager are supported options. Each is its own class, but they are instantiated under the `SecretManager` class. However, it is a requirement that all classes utilized by `SecretManager` must use the standard `get_secret` and `set_secret` methods.

#### Standardization and Requirements for `get_secret` and `set_secret` Functions

All secret management classes must implement the `get_secret` and `set_secret` methods. These methods are responsible for retrieving and storing the `accessToken` and `refreshToken` variables.

- `get_secret`: This method should retrieve the stored tokens and return them in a dictionary with keys `accessToken` and `refreshToken`. If the tokens are not found, it should return `None`.
- `set_secret`: This method should accept `accessToken` and `refreshToken` as parameters and store them securely.

Example structure for `get_secret` and `set_secret` methods:

```python
def get_secret(self):
    # Retrieve tokens from storage
    secret = {
        'accessToken': self.accessToken,
        'refreshToken': self.refreshToken
    }
    return secret

def set_secret(self, accessToken, refreshToken):
    # Store tokens securely
    self.accessToken = accessToken
    self.refreshToken = refreshToken
    # Save tokens to storage
```

#### Local Secret Management

By default, tokens are stored in a local file. The file is located in the `.tokens` directory within the `src/sfPyAuth` directory.

#### AWS Secret Manager

To use AWS Secret Manager, set the `SECRET_MANAGEMENT_TYPE` to `aws` in your `.env` file and provide the necessary AWS credentials and secret details.

```env
SECRET_MANAGEMENT_TYPE=aws
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_SESSION_TOKEN=your_session_token (optional)
AWSSM_SECRET_NAME=your_secret_name
AWSSM_REGION_NAME=your_region_name
```

##### Setting up AWS Secret Manager

Please review AWS best practices and security documentation when setting up any AWS-related service. AWS official documentation can be found here: [AWS Secret Manager Documentation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html).

Requirements for the Secret itself:
* Secret Type: "Other type of secret"
* Plaintext:
  ```json
  {
    "accessToken": "", 
    "refreshToken": ""
  }
  ```

## Plans
* Provide a way to authenticate without user interaction (for use in serverless/headless environments)

## Contributing
If you want to contribute, feel free.

1. Fork the repository.
2. Create a new branch.
3. Make/commit your changes.
4. Raise a PR with the following details:
    * Feature/Functionality/Fix you are implementing
    * Changes made
    * Any other details you feel are relevant

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE.md) file for details.

## Copyright

© 2025 Tim Firman. All rights reserved.

Canary line 222123312123123111