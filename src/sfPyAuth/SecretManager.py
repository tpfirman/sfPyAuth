import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import json

class SecretsManager:
    def __init__(self):
        load_dotenv()
        
        secretManagerType : str = os.getenv('SECRET_MANAGEMENT_TYPE')
        
        if secretManagerType == 'local':
            self._secretsManager = localSecretsManager()
        
        elif secretManagerType == 'aws':
            self._secretsManager = awsSecretsManager()
        
        elif secretManagerType == 'azure':
            print('Azure Secret Manager is not implemented yet')
            return
        else:
            print('Invalid Secret Manager Type')
            return
        
        self.accessToken : str = None
        self.refreshToken : str = None
        
        self.get_secret()
        
    def set_secret(self, accessToken, refreshToken):
        try:
            self._secretsManager.set_secret(accessToken, refreshToken)
            return True
        
        except Exception as e:
            print(f'Error while setting the secret {e}')
            return False
        
    def get_secret(self):
        secret = self._secretsManager.get_secret()
        if secret != None:
            self.accessToken = secret['accessToken']
            self.refreshToken = secret['refreshToken']
        return secret
        
class localSecretsManager:
    def __init__(self):
        load_dotenv()
        
        self.tokenFolder : str = os.path.join(os.getcwd(),'src','sfPyAuth', '.tokens')
        self.tokenFileName : str = '.token'
        self.tokenPath = os.path.join(self.tokenFolder, self.tokenFileName)  
        
        ## Action initTasks
        if os.path.exists(self.tokenFolder):
            self.get_secret()
        else:
            try:
                os.mkdir(self.tokenFolder)
            except Exception as e:
                print(f'Error while creating the token directory: {e}')
                os._exit(1)
            
        
    def set_secret(self, accessToken, refreshToken):
        """
        Saves the access and refresh tokens to a file specified by `self.tokenPath`.

        Returns:
            bool: True if the tokens were successfully saved, False otherwise.
        Raises:
            Exception: If there is an error while writing to the file, it prints an error message and returns False.
        """
        
        print(f"\nSaving the tokens to the {self.tokenPath} file...")
        data = (f'accessToken={accessToken}\nrefreshToken={refreshToken}\n')

        try:
            with open(self.tokenPath, 'w') as file:
                file.write(data)
            print('Tokens saved successfully! \n')
            return
        
        except Exception as e:
            print(f'Error while saving the token: {e} \n\n')
            return
        
    def get_secret(self):
        """
        Loads the Salesforce access and refresh tokens into self from a local file specified by `self.tokenPath`.
        
        Returns:
            bool: True if the tokens were successfully loaded, False otherwise.
        Raises:
            Exception: If there is an error while reading the file or parsing the tokens.
        """
        
        try:
            accessToken : str = None
            refreshToken : str = None
            
            if not os.path.exists(self.tokenPath) or not os.path.isfile(self.tokenPath):
                print(f'Token file not found at {self.tokenPath}')
                return
           
            with open(self.tokenPath, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if 'accessToken' in line:
                        accessToken = line.split('=')[1].strip()
                    elif 'refreshToken' in line:
                        refreshToken = line.split('=')[1].strip()
            print(f'Tokens loaded successfully from {self.tokenPath} \n')
            
            secret : dict = {
                'accessToken': accessToken,
                'refreshToken': refreshToken
            }
            
            return secret 

        except Exception as e:
            print(f'Error while loading the token: {e}')
            return

class awsSecretsManager:
    def __init__(self):  # Fix the constructor method name
        load_dotenv()
        
        self.secret_name: str = os.getenv('AWSSM_SECRET_NAME')
        self.region_name: str = os.getenv('AWSSM_REGION_NAME')
        self.aws_access_key_id: str = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key: str = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_session_token: str = os.getenv('AWS_SESSION_TOKEN')
        
        self.session = boto3.session.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token
        )
        
        self.client = self.session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )
        
    def set_secret(self, accessToken, refreshToken):     
        secret = {
            "accessToken": accessToken,
            "refreshToken": refreshToken
        }
        
        secretString = json.dumps(secret)
                
        try:
            self.client.put_secret_value(
                SecretId=self.secret_name,
                SecretString=secretString
            )
        except ClientError as e:
            raise e
        
    def get_secret(self):
        # Create a Secrets Manager client
        
        client = self.session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=self.secret_name
            )
        except ClientError as e:
            raise e

        secret = get_secret_value_response['SecretString']
        return json.loads(secret)

