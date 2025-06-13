# Test Requierments.
# Whever the class is initialized, it will require the user to input the secret code, unless it is saved in the tokens file.
# We need to test the web browser loading is working

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open, MagicMock
import os
# Adjust the import statement to correctly reference the sfPyAuth module
from src.sfPyAuth.sfPyAuth import oAuthController

class TestoAuthController(unittest.TestCase):

    @patch('src.sfPyAuth.sfPyAuth.requests.request')
    @patch('src.sfPyAuth.sfPyAuth.oAuthController.getSecretCodeFromOauth', return_value='secretKeyForTesting')
    @patch('src.sfPyAuth.sfPyAuth.load_dotenv')
    @patch('src.sfPyAuth.sfPyAuth.os.getenv')
    def setUp(self, mock_getenv, mock_load_dotenv, mock_getSecretCodeFromOauth, mock_request):
        """
        Set up the test environment by mocking environment variables and initializing the oAuthController instance.
        """
        mock_getenv.side_effect = lambda key: {
            'SF_USERNAME': 'test_username',
            'SF_PASSWORD': 'test_password',
            'SF_CLIENT_ID': 'test_client_id',
            'SF_CLIENT_SECRET': 'test_client_secret',
            'SF_INSTANCE_URL': 'https://test.salesforce.com'
        }.get(key)
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token'
        }
        self.oauth = oAuthController()

    @patch('src.sfPyAuth.sfPyAuth.os.path.exists')
    @patch('src.sfPyAuth.sfPyAuth.os.path.isfile')
    @patch('builtins.open', new_callable=mock_open, read_data='accessToken=test_access_token\nrefreshToken=test_refresh_token\n')
    def test_localTokenHandler_load(self, mock_open, mock_isfile, mock_exists):
        """
        Test loading tokens from a local file.
        Expected outcome: Tokens are loaded successfully and assigned to the instance variables.
        """
        mock_exists.return_value = True
        mock_isfile.return_value = True
        result = self.oauth.localTokenHandler_load()
        self.assertTrue(result)
        self.assertEqual(self.oauth.sf_access_token, 'test_access_token')
        self.assertEqual(self.oauth.sf_refresh_token, 'test_refresh_token')

    @patch('builtins.open', new_callable=mock_open)
    def test_localTokenHandler_save(self, mock_open):
        """
        Test saving tokens to a local file.
        Expected outcome: Tokens are saved successfully to the specified file.
        """
        self.oauth.sf_access_token = 'test_access_token'
        self.oauth.sf_refresh_token = 'test_refresh_token'
        result = self.oauth.localTokenHandler_save()
        self.assertTrue(result)
        mock_open().write.assert_called_with('accessToken=test_access_token\nrefreshToken=test_refresh_token\n')

    @patch('src.sfPyAuth.sfPyAuth.requests.request')
    def test_webServerFlow(self, mock_request):
        """
        Test the web server flow for obtaining access and refresh tokens.
        Expected outcome: Tokens are obtained successfully and assigned to the instance variables.
        """
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token'
        }
        result = self.oauth.webServerFlow('test_secret_code')
        self.assertTrue(result)
        self.assertEqual(self.oauth.sf_access_token, 'test_access_token')
        self.assertEqual(self.oauth.sf_refresh_token, 'test_refresh_token')

    @patch('src.sfPyAuth.sfPyAuth.requests.request')
    def test_testAccessToken(self, mock_request):
        """
        Test the validity of the access token by querying the Salesforce API.
        Expected outcome: The access token is valid and the query returns a successful response.
        """
        self.oauth.sf_access_token = 'test_access_token'
        self.oauth.sf_instanceUrl = 'https://test.salesforce.com'
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {'totalSize': 1}
        result = self.oauth.testAccessToken()
        self.assertTrue(result)

    @patch('src.sfPyAuth.sfPyAuth.requests.request')
    def test_getOauthTokens(self, mock_request):
        """
        Test obtaining a new refresh token using the existing refresh token.
        Expected outcome: A new refresh token and access token are obtained and assigned to the instance variables.
        """
        self.oauth.sf_refresh_token = 'test_refresh_token'
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token'
        }
        result = self.oauth.getOauthTokens()
        self.assertTrue(result)
        self.assertEqual(self.oauth.sf_access_token, 'new_access_token')
        self.assertEqual(self.oauth.sf_refresh_token, 'new_refresh_token')

if __name__ == '__main__':
    unittest.main()
