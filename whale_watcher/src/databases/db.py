from typing import Protocol
import boto3
from .schema.dynamodb import ddb_schema
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
    def __init__(self, endpoint_url:str):
        self.client =  boto3.client('dynamodb', endpoint_url=endpoint_url)
        self.table = None
        
    def create_table(self, table_name:str)->None:
        # check if table already exists
        if self.client.describe_table(TableName=table_name) == self.client.exceptions.ResourceNotFoundException:
            try:
                self.table = self.client.create_table(
                    TableName=table_name,
                    **ddb_schema
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

if __name__ == "__main__":
    # test dynamodb class
    dynamo = DynamoDB(endpoint_url='http://localhost:8000')
    dynamo.create_table('test')
    
    # test insert scan finding
    test_dict = {'findings': image_scan_finding} | {'image_name': app_details[1].imageDetail.repoName,
                                         'image_tag': app_details[1].imageDetail.imageTag}
    
    dynamo.insert_data('test', test_dict)
    
    # test fetch data from dynamodb
    ddb_query = {'image_name': app_details[1].imageDetail.repoName,
                'image_tag': app_details[1].imageDetail.imageTag}
    
    ddb_response =dynamo.get_data(table_name = 'test', 
                    query = ddb_query)
    
    # deserialised reseults
    deserializer = TypeDeserializer()
    deserialized_findings = deserializer.deserialize(ddb_response.get('Item').get('findings'))
    
    # filter out dict keys we are interested in
    # name, severity and description
    interested_keys = ['name', 'severity', 'description']
    
    filtered_findings = [{key: finding.get(key) 
                          for key 
                          in interested_keys}
                        for finding
                        in deserialized_findings]