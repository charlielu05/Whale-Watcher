from typing import Protocol
import boto3
from botocore.exceptions import ClientError
import logging
from boto3.dynamodb.types import TypeSerializer
serializer = TypeSerializer()

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)

class DB(Protocol):
    def __init__(self):
        ...
        
    def create_table(self, table_name:str) -> None:
        ...
        
    def insert_data(self, table_name:str, data) -> None:
        ...
        
    def get_data(self, table_name:str, query):
        ...
        
    def delete_data(self, reference) -> None:
        ...


class DynamoDB:
    def __init__(self):
        self.client =  boto3.client('dynamodb', endpoint_url='http://localhost:8000')
        self.table = None
        
    def create_table(self, table_name:str)->None:
        # check if table already exists
        if self.client.describe_table(TableName=table_name) == self.client.exceptions.ResourceNotFoundException:
            try:
                self.table = self.client.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': 'image_name', 'KeyType': 'HASH'},  # Partition key
                        {'AttributeName': 'image_tag', 'KeyType': 'RANGE'}  # Sort key
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'image_name', 'AttributeType': 'S'},
                        {'AttributeName': 'image_tag', 'AttributeType': 'S'}
                    ],
                    BillingMode = 'PAY_PER_REQUEST',
                    )
                waiter = self.client.get_waiter('table_exists')
                waiter.wait(TableName=table_name)
                
            except ClientError as err:
                logger.error(
                    "Couldn't create table %s. Here's why: %s: %s", table_name,
                    err.response['Error']['Code'], err.response['Error']['Message'])
                raise
            else:
                return self.table
        else:
            self.table = self.client.describe_table(TableName = table_name)
    
    def insert_data(self, table_name:str, data:dict):
        try:
            self.client.put_item(TableName = table_name, 
                                 Item = {key: serializer.serialize(value) for key, value in data.items()})
            
        except ClientError as err:
            logger.error(f"Couldn't add {data} to {self.table.get('Table').get('TableName')}, errors: {err.response['Error']['Code'], err.response['Error']['Message']}")
            raise
    
    def get_data(self, table_name:str, query:dict) -> dict:
        return self.client.get_item(TableName = table_name, 
                                    Key = {key: serializer.serialize(value) for key, value in query.items()}
                                    )
        
    def delete_data(self, table:str, reference):
        pass
    
    
def insert_data_to_db(database: DB, data) -> None:
    database.insert_data(data)