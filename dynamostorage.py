import boto3
from botocore.exceptions import ClientError

class dynamoStorage(): 
    

    def __init__(self,tableName="KeyValue",sortKey=False):
            super().__init__()
            self.session = boto3.Session(profile_name='itesodev', region_name='us-east-1')
            self.dynamodb = self.session.resource('dynamodb')
            try: 
                self.table = self.dynamodb.Table(tableName)
                print ('Table Id: ', self.table.table_id)
            except ClientError as ce:
                if ce.response['Error']['Code'] == 'ResourceNotFoundException':
                    print('Creating table....')
                    if (not sortKey):
                        self.createTable(tableName)
                        
                    else:
                        self.createSortTable(tableName)

                    print ('Table Id: ', self.table.table_id)   
                    pass
                else:
                    print('Unkown Error in Describe Table')
            #if self._cur.fetchone() is None:
            #   if(not sortKey):
            #      self._cur.execute('CREATE TABLE {0} (skey TEXT PRIMARY KEY, value TEXT)'.format(self._table))
            # else:
                #    self._cur.execute('CREATE TABLE {0} (skey TEXT, sort TEXT, value TEXT, PRIMARY KEY(skey,sort))'.format(self._table))

    def createTable(self, tableName):
        client = self.session.client('dynamodb')
        client.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'keyword',
                    'AttributeType': 'S'
                },
            ],
            TableName=tableName,
            KeySchema=[
                {
                    'AttributeName': 'keyword',
                    'KeyType': 'HASH'
                },
            ],
            
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        response = client.describe_table(
                TableName=tableName
            )
        while response['Table']['TableStatus'] != 'ACTIVE':
            response = client.describe_table(
                TableName=tableName
            )
        print ('Table Ready')
    
    
    def createSortTable(self, tableName):
        client = self.session.client('dynamodb')
        client.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'keyword',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'inx',
                    'AttributeType': 'N'
                },
            ],
            TableName=tableName,
            KeySchema=[
                {
                    'AttributeName': 'keyword',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'inx',
                    'KeyType': 'RANGE'
                },
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        response = client.describe_table(
                TableName=tableName
            )
        while response['Table']['TableStatus'] != 'ACTIVE':
            response = client.describe_table(
                TableName=tableName
            )
        print ('Table Ready')


    # put 
    def putItem(self, item):
        response = self.table.put_item(
            Item = item,
        )
        print (response)
    # get

    def getItem(self, keyword):
        response = self.table.get_item(
            Key = keyword,
        )
        return response

    def batchWriteItem(self, queryList):
        print(queryList)
        with self.table.batch_writer() as batch:
            for i in range(5):
                batch.put_item(Item=queryList[i])

    def queryItem(self, value):
        response = self.table.query(
            KeyConditions={
                'keyword': {
                    'AttributeValueList': [ value ],
                    'ComparisonOperator': 'EQ'
                }
            }
        )
        return response