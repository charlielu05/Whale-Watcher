from fastapi import FastAPI
from databases.db import DynamoDB
from resources.aws_lambda import return_lambda_image_details
from ww_helpers import get_app_details
from image_scanners.ecr import get_severity_counts, get_image_scan_findings
from boto3.dynamodb.types import TypeDeserializer

app = FastAPI()

@app.get('/')
def main():
    lambda_code_details = return_lambda_image_details()
    
    app_details = get_app_details(lambda_code_details)
   
    images_severity_counts = get_severity_counts(app_details)
    
    return images_severity_counts

if __name__ == "__main__":
    lambda_code_details = return_lambda_image_details()
    
    app_details = get_app_details(lambda_code_details)
   
    images_severity_counts = get_severity_counts(app_details)
    
    # sample image scan finding
    image_scan_finding = get_image_scan_findings(app_details[0].imageDetail).get('imageScanFindings').get('findings')
    
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
                         