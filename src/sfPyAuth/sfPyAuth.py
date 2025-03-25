"""
oAuth.py

This module provides an OAuth controller for authenticating with Salesforce using OAuth 2.0.
It is intended to be imported and used as part of a larger application, not run as a standalone script.

Classes:
    oAuthController: Handles OAuth authentication and token management for Salesforce.

Usage:
    from src.sfPyAuth.sfPyAuth import oAuthController
    from simple_salesforce import Salesforce

    oauth = oAuthController()
    if oauth.initComplete:
        # Perform actions with authenticated session

    oauth.checkTokenExpiry()

    sf = Salesforce(instance_url=oAuth.sf_instanceUrl, session_id=oAuth.sf_access_token)
    result = sf.query("SELECT Id FROM Account LIMIT 1")
"""

import requests
import os
import webbrowser
import urllib.parse
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sys
import select

try:
    from .SecretManager import SecretsManager
except ImportError:
    from SecretManager import SecretsManager
    
devmode : bool = False

class oAuthController:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        
        ## Populate instance variables from .env file
        load_dotenv()        
        self.sf_username : str = os.getenv('SF_USERNAME')
        self.sf_password : str = os.getenv('SF_PASSWORD')
        self.sf_consumer_key : str = os.getenv('SF_CLIENT_ID')
        self.sf_consumer_secret : str = os.getenv('SF_CLIENT_SECRET')
        self.sf_instanceUrl : str = os.getenv('SF_INSTANCE_URL')
        self.sf_apiVersion : str = 'v60.0'
        self.sf_base_url : str = None      
        
        self.sf_access_token_expires : str = None

        # Check if the required info is available before moving on.
        if not self.sf_username or not self.sf_consumer_key or not self.sf_consumer_secret:
            print('Error: Salesforce credentials are not set in the environment variables. Exiting...')
            os._exit(1)
           
        self.sm = SecretsManager()
        secrets = self.sm.get_secret()
        self.accessToken = secrets['accessToken'] if 'accessToken' in secrets else None
        self.refreshToken = secrets['refreshToken'] if 'refreshToken' in secrets else None
                
        self.initComplete : bool = self.initTasks()
        if self.initComplete:
            accessTokenWorks = self.testAccessToken()
            if not accessTokenWorks:
                print('Access token is not valid!')
                
        else:
            print('Error while initializing the oAuth module. Exiting...\n------------------------------------------\n\n')
            os._exit(1)       
   
    
    def getSecretCodeFromOauth(self):
        """
        **REQUIRES USER INTERACTION AND WEB BROWSER**
        Opens a web browser to the Salesforce OAuth authorization URL and for the user to auth and capture the secret code.
        The secret code is in the URL of the browser after the user has authorized the app. The code must be entered into the console by the user.
        
        Returns:
            str: The secret code entered by the user.

        To do:
            - capture the full url from the console, amd extract the code from the url
            - later, capture the secret code from the url directly
        """
        

        url = f'{self.sf_instanceUrl}/services/oauth2/authorize?response_type=code&redirect_uri=https://login.salesforce.com/services/oauth2/success&client_id={self.sf_consumer_key}'      
        print(f'Opening the browser to the Salesforce OAuth authorization URL\n {url}')
        webbrowser.open(url)

        secretCode = input("Enter the secretCode: ")
        secretCode = secretCode.split('code=')[-1]
        secretCode = urllib.parse.unquote(secretCode)       

        return secretCode
    
        
    def testAccessToken(self):
        """
        Tests the validity of the Salesforce access token by querying the Account object.
        Returns:
            bool: True if the access token is valid, False otherwise.
        """

        # Setup and send the request
        if self.accessToken == None:
            print('Access token is not set')
            return False
        if self.sf_instanceUrl == None:
            print('Instance URL is not set')
            return False

        url = f'{self.sf_instanceUrl}/services/data/{self.sf_apiVersion}/query/?q=SELECT+Id+FROM+User+LIMIT+1'
        headers = {
            'Authorization' : f'Bearer {self.accessToken}'
        }

        response = requests.request("GET", url, headers=headers)  

        # Handler the response.
        if response.status_code == 200:
            responseJson = response.json()
            if responseJson['totalSize'] == 1:
                print('Access token is valid. Account returned successfully')
                return True
            else:
                print(f'Access token is invalid. Query result total size is {responseJson["totalSize"]}')
                return False
        else:
            print(f'Error while testing the access token.\nStatus code: {response.status_code}')
            return False


    def getOauthTokens(self):
        """
        Obtains a new refresh token using OAuth flow and class based variables.
        Returns:
            bool: True if the refresh token is successfully obtained and updated, False otherwise.
        """

        if not self.refreshToken:
            print('Refresh token is not set, cannot proceed')
            return False

        oauthUrl = 'https://login.salesforce.com/services/oauth2/token'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.sf_consumer_key,
            'client_secret': self.sf_consumer_secret,
            'format': 'json',
            'refresh_token' : self.refreshToken
        }

        response = requests.request("POST", oauthUrl, headers=headers, data=payload)

        saveResult : bool = False
        if response.status_code != 200:
            print(f'Error while generating new Refresh Token. Status code: {response.status_code} \n {response.text}')
            return False
        else:
            
            isUpdated : bool = False
            if 'refresh_token' in response.json() and self.refreshToken != response.json()['refresh_token']:
                self.refreshToken = response.json()['refresh_token']
                isUpdated = True
                
            if self.accessToken != response.json()['access_token']:
                self.accessToken = response.json()['access_token']
                isUpdated = True
                
            if self.sf_instanceUrl != response.json()['instance_url']:
                self.sf_instanceUrl = response.json()['instance_url']
                isUpdated = True            

            if isUpdated:
                self.sf_accessToken_expires = datetime.now() + timedelta(hours=4)
                print('Refresh token has been updated successfully')
                
                saveResult = self.sm.set_secret(self.accessToken, self.refreshToken)
        
        if saveResult:
            print(f'New access token and refesh token saved successfully. \n')
            # self.refreshToken = self.sm.refreshToken
            # self.accessToken = self.sm.accessToken
            
            return True
        else:
            return False
        
    # def checkTokenExpiry(self):
    #     """
    #     Checks if the Salesforce access token has expired and refreshes it if necessary.
    #     """
        
    #     print('Checking token expiry')
    #     now = datetime.now()

    #     if self.sf_accessToken_expires == None or now > self.sf_accessToken_expires:
    #         print('Token is expired, refreshing...')
    #         self.getOauthTokens()
    #     else:
    #         print('Token is still valid')
            
    #     return
    
    def initOauth(self):
        # Prompt user to generate a new secretCode for OAuth
        secretCode : str = self.getSecretCodeFromOauth()

        if secretCode == None:
            print('Error while getting the secret code')
            return False
        
        # Get the new refresh and access token 
        webServerResult : bool = self.webServerFlow(secretCode)
        if webServerResult:
            print('Refresh token has been updated successfully')
            return True
        
        else:
            return False
    
    def webServerFlow(self, secretCode : str):
        """
        Authenticates with Salesforce using the OAuth 2.0 Web Server Flow.
        Args:
            secretCode (str): The authorization code received from Salesforce.
        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        

        oauthUrl = 'https://login.salesforce.com/services/oauth2/token'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'code': secretCode,
            'grant_type': 'authorization_code',
            'client_id': self.sf_consumer_key,
            'client_secret': self.sf_consumer_secret,
            'format': 'json',
            'redirect_uri' : 'https://login.salesforce.com/services/oauth2/success',
            'response_type' : 'code'
        }

        response = requests.request("POST", oauthUrl, headers=headers, data=payload)

        if response.status_code != 200:
            print('Error while authenticating')
            return False
        else:
            print('Authenticated successfully')

        jsonResponse = response.json()
        self.accessToken = jsonResponse['access_token']
        self.refreshToken = jsonResponse['refresh_token']        
        self.sf_accessToken_expires = datetime.now() + timedelta(hours=4)

        # save the tokens to the token file
        self.sm.set_secret(self.accessToken, self.refreshToken)

        return True
     

    def initTasks(self):
        """
        Initialization tasks related to OAuth authentication.

        Returns:
            bool: True if the access token is valid or successfully updated, False otherwise.
        """
        
        
        # Check if the refresh token is populated
        if self.refreshToken:
            print('Refresh token is available in memory.')

            refreshTokenUpdated : bool = self.getOauthTokens()
            if refreshTokenUpdated:
                print('Refresh and Access tokens have been updated successfully, and is ready to use.')
                return True
            else:
                print('Error while updating the refresh token. Moving on to secret code generation')        

                    
        initOauthResult : bool = self.initOauth()

        # If auth fails prompt for the secret code again
        if not initOauthResult:
            print('Error while authenticating with the secret code provided. \nWould you like to try again?  (Y/n)')
            retry : bool = True
            print('Would you like to try again?  (Y/n) (default is "n" after 10 seconds): ', end='', flush=True)
            inputRetry = 'n'
            i, o, e = select.select([sys.stdin], [], [], 10)
            if i:
                inputRetry = sys.stdin.readline().strip()

            if inputRetry.lower() == 'n':
                retry = False

            if retry:
                initOauthResult : bool = self.initOauth()

                if not initOauthResult:
                    print('Error while authenticating with the secret code provided. Exiting...')
                    return  False
            else:
                print('Exiting...')
                return  False
                
        else:
            return  True


if __name__ == '__main__':
    if devmode:
        print('Running the oAuth module as a standalone script...')
        oauth = oAuthController()
        if oauth.initComplete:
            print('oAuth module Initialised. Ready to roll...\n------------------------------------------\n\n')
        else:
            print('Error while initializing the oAuth module. Exiting...\n------------------------------------------\n\n')
            os._exit(1)
    else:            
        print("This module is not intended to be run as a standalone script.")
