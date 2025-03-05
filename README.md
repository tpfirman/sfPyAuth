

**SETUP**

***Create Connected App for Authentication in Salesforce***
https://help.salesforce.com/s/articleView?id=xcloud.connected_app_create_basics.htm&type=5
https://help.salesforce.com/s/articleView?id=xcloud.connected_app_create_api_integration.htm&type=5

1. Setup Console -> App Manager -> New Connected App
2. Create a Connected App
3. Fill in deatils in Basic Information
4. Tick Enable API
5. Set Callback URL to "https://login.salesforce.com/services/oauth2/success"
6. Add the minimum required OAuth scopes
    Access Content Resources (content)
    Access custom permissions (custom_permissions)
    Full access (full)
    Perform requests at any time (refresh token, offline_access)
7. Untick "Require Proof Key for Code Exchange (PKCE) Extension for Supported Authorization Flows.
8. Tick Require Secrect for Web Server Flow
9. Tick Require Secrect for Refresh Token Flow
10. Tick Enable Token Exchange
11. Tick Require Secret for Token Exchange Flow
12. Tick Enable Refresh Token Rotation

   