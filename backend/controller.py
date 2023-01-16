from boto3 import resource
from config import DB_URL, REGION, ACCESS_ID, ACCESS_KEY


resource = resource('dynamodb',
                    endpoint_url=DB_URL,
                    region_name=REGION,
                    aws_access_key_id=ACCESS_ID,
                    aws_secret_access_key=ACCESS_KEY)

client = resource.meta.client


def create_table_movie():
    try:
        table = resource.create_table(
            TableName='Replica',
            KeySchema=[
                {
                    'AttributeName': 'key',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'key',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'value',
                    'AttributeType': 'N'
                },
            ]
        )

        table.put_item(
            Item={
                'key': 0,
                'value': 1,
            }
        )

        table = resource.create_table(
            TableName='Movie',  # Name of the table
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # HASH = partition key, RANGE = sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',  # Name of the attribute
                    'AttributeType': 'S'  # N = Number (S = String, B= Binary)
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    except client.exceptions.ResourceInUseException as e:
        return str(e)

    return "Success"


create_table_movie()
MovieTable = resource.Table('Movie')
ReplicaTable = resource.Table('Replica')


def get_replica_val():

    response = ReplicaTable.update_item(Key={'key': 0},
                                        ReturnValues="UPDATED_NEW",
                                        ExpressionAttributeValues={":inc": 1},
                                        UpdateExpression='ADD value :inc',)
    return response['Attributes'].get('value', 0)


def write_to_movie(movie_id, title, director):
    response = MovieTable.put_item(
        Item={
            'id': movie_id,
            'title': title,
            'director': director
        }
    )
    return response


def read_from_movie(movie_id):
    response = MovieTable.get_item(
        Key={
            'id': movie_id
        },
        AttributesToGet=[
            'title', 'director' # valid types dont throw error,
        ]                      # Other types should be converted to python type before sending as json response
    )
    return response


def read_movies():
    response = MovieTable.scan()
    return response


def update_in_movie(movie_id, data: dict):
    response = MovieTable.update_item(
        Key={
            'id': movie_id
        },
        AttributeUpdates={
            'title': {
                'Value': data['title'],
                'Action': 'PUT' # available options = DELETE(delete), PUT(set/update), ADD(increment)
            },
            'director': {
                'Value': data['director'],
                'Action': 'PUT'
            }
        },
        ReturnValues="UPDATED_NEW"  # returns the new updated values
    )
    return response


def modify_director_for_movie(movie_id, director):
    response = MovieTable.update_item(
        Key={
            'id': movie_id
        },
        UpdateExpression='SET info.director = :director', #set director to new value
        #ConditionExpression = '', # execute until this condition fails # no condition
        ExpressionAttributeValues={ # Value for the variables used in the above expressions
            ':new_director': director
        },
        ReturnValues="UPDATED_NEW"  #what to return
    )
    return response


def delete_from_movie(movie_id):
    response = MovieTable.delete_item(
        Key={
            'id': movie_id
        }
    )

    return response
