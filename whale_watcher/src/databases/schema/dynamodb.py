
ddb_schema = {'KeySchema': 
                [
                    {'AttributeName': 'image_name', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'image_tag', 'KeyType': 'RANGE'}  # Sort key
                ],
              'AttributeDefinitions': 
                [
                    {'AttributeName': 'image_name', 'AttributeType': 'S'},
                    {'AttributeName': 'image_tag', 'AttributeType': 'S'}
                ], 
                'BillingMode':
                    'PAY_PER_REQUEST'}