# sfPyAuth

A simple Python library for authenticating to Salesforce.

## Setup

### Create Connected App for Authentication in Salesforce

Official Documentation from SF for reference:
- [Create Connected App Basics](https://help.salesforce.com/s/articleView?id=xcloud.connected_app_create_basics.htm&type=5)
- [Create API Integration](https://help.salesforce.com/s/articleView?id=xcloud.connected_app_create_api_integration.htm&type=5)

My shorthand version:
1. Go to Setup Console -> App Manager -> New Connected App
2. Create a Connected App
3. Fill in details in Basic Information
4. Tick Enable API
5. Set Callback URL to "https://login.salesforce.com/services/oauth2/success"
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

#### Example .env file

```
SF_CLIENT_ID=your_client_id_here
SF_CLIENT_SECRET=your_client_secret_here
SF_USERNAME=your_username_here
```

## Usage

### Import and Instantiate

To use `sfPyAuth` as a library, import and instantiate the `oAuthController` class:

```python
from oAuth import oAuthController

oauth = oAuthController()
```

### Authenticating When Required

If there is no usable token (first use, token missing/invalid/expired), you will need to authenticate to your Salesforce org again. This will be done as part of the library's initialization. The script will attempt to open your browser to the login page for your Connected App. The URL will also be displayed in the console.

Once you have authenticated, copy the URL from the browser and paste it into the console. The script will extract the secret code and proceed to save the required tokens.

### Using it to Get an Auth Token for Subsequent API Calls

Once authenticated, you can use the access token for subsequent API calls:

```python
from simple_salesforce import Salesforce

oauth.checkTokenExpiry()

sf = Salesforce(instance_url=oauth.sf_instanceUrl, session_id=oauth.sf_access_token)
result = sf.query("SELECT Id FROM Account LIMIT 1")
print(result)
```

## Plans
* Provide way to authenticate without user interaction (for use in serverless/headless environments)
* Implement key management (Azure/AWS) as an option
* Tests


## Contributing
If you want to contribute, feel free.

1. Fork the repository.
2. Create a new branch.
3. Make/commit your changes.
4. Raise PR, with the following details.
    * Feature/Functionality/Fix you are implimenting
    * Changes made.
    * Any other details you feel are relevant.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE.md) file for details.

## Copyright

© 2025 Tim Firman. All rights reserved.

