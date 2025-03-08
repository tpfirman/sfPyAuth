import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import json

class remoteSecretsManager:
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
        
        self.accessToken : str = None
        self.refreshToken : str = None
        
    def set_secret(self):     
        secret = {
            "accessToken": self.accessToken,
            "refreshToken": self.refreshToken
        }
        
        secretString = json.dumps(secret)
        
        # Create a Secrets Manager client
        
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
        print(secret)


test = remoteSecretsManager()
test.get_secret()
test.accessToken = "test"
test.refreshToken = "test2"
test.set_secret()
test.get_secret()