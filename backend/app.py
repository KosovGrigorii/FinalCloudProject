from flask import Flask, request, jsonify
import controller as dynamodb
from flask_cors import CORS, cross_origin
from config import BACKEND_VERSION

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_ORIGINS'] = ['https://project-backet.website.yandexcloud.net']
app.config['CORS_HEADERS'] = ['Content-Type']
replica_id = dynamodb.get_replica_val()

@app.route('/test')
def test():
    print("TEST SUCCESS")
    return 'TEST SUCCESS'


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response


@app.route('/')
def root_route():
    response = dynamodb.create_table_movie()
    return jsonify({"msg": response})


@app.route('/info')
def get_info():
    data = {'replica': replica_id, 'version': BACKEND_VERSION}
    return jsonify(data)


@app.route('/movie', methods=['POST'])
def add_movie():
    data = request.get_json()
    response = dynamodb.write_to_movie(data['id'], data['title'], data['director'])    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return {
            'msg': 'Added successfully',
        }
    return {  
        'msg': 'Some error occcured',
        'response': response
    }


@app.route('/movie/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    response = dynamodb.read_from_movie(movie_id)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        if 'Item' in response:
            return {'Item': response['Item']}
        return {'msg': 'Item not found!'}
    return {
        'msg': 'Some error occured',
        'response': response
    }


@app.route('/movies', methods=['GET'])
@cross_origin(origins='https://project-backet.website.yandexcloud.net/')
def get_movies():
    response = dynamodb.read_movies()

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        if 'Items' in response:
            return {'Items': response['Items']}
        return {'msg': 'Item not found!'}
    return {
        'msg': 'Some error occured',
        'response': response
    }


@app.route('/movie/<movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    response = dynamodb.delete_from_movie(movie_id)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return {
            'msg': 'Deleted successfully',
        }
    return {  
        'msg': 'Some error occcured',
        'response': response
    } 


@app.route('/movie/<movie_id>', methods=['PUT'])
def update_movie(movie_id):

    data = request.get_json()
    response = dynamodb.update_in_movie(movie_id, data)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return {
            'msg': 'Updated successfully',
            'ModifiedAttributes': response['Attributes'],
            'response': response['ResponseMetadata']
        }
    return {
        'msg': 'Some error occured',
        'response': response
    }


if __name__ == '__main__':
    from waitress import serve
    serve(app)
