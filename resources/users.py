import json

from flask import jsonify, Blueprint, abort, make_response

from flask_restful import (Resource, Api, reqparse,
                               inputs, fields, marshal,
                               marshal_with, url_for)

from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
import models

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
}

workout_fields = {
    'id': fields.Integer,
    'muscle': fields.String,
    'workout_name': fields.String,
    'equipment': fields.String, 
    'weight': fields.String,
    'sets': fields.String,
    'reps': fields.String,
    'created_by': fields.String
}


class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required=True,
            help='No email provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=True,
            help='No password provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'verify_password',
            required=True,
            help='No password verification provided',
            location=['form', 'json']
        )
        super().__init__()
    def get(self):
        all_users = [marshal(user, user_fields) for user in models.User]
        return all_users

    def post(self):
        #registrations
        args = self.reqparse.parse_args()
        print(args)
        if args['password'] == args['verify_password']:
            print(args, ' this is args')
            user = models.User.create_user(**args)

            # Pass the user to login_user
            # set up our session for us!
            login_user(user)

            return marshal(user, user_fields), 201
        return make_response(
            json.dumps({
                'error': 'Password and password verification do not match'
            }), 400)# just another way to send something back to the client
    

class User(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument(
            'username',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required=True,
            help='No email provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=True,
            help='No password provided', 
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'verify_password',
            required=True,
            help='No password verification provided',
            location=['form', 'json']
        )
        super().__init__()

    # @marshal_with(user_fields)
    @marshal_with(workout_fields)
    def get(self, id):
        try:
            user = models.User.get(models.User.id==id)
            print(user.__dict__, "this is the")
            workouts = [marshal(workout, workout_fields)
                for workout in models.Workout.select().where(models.Workout.created_by == user.id)
            ]
            
        except models.User.DoesNotExist:
            abort(404)
        else:
            print(user)
            # data = { 'user':  user, 'workout': workouts}
            return (workouts, 200)
    
    @marshal_with(user_fields)
    def put(self, id):
        try:
            args = self.reqparse.parse_args()
            new_args = {key: value for key, value in args.items() if value is not None}
            query = models.User.update(**new_args).where(models.User.id==id)
            query.execute()
        except models.User.DoesNotExist:
            abort(404)
        else:
            return (models.User.get(models.User.id==id), 200)

    def delete(self, id):
        query = models.User.delete().where(models.User.id==id)
        query.execute()
        return {'message': 'This user has been deleted'}


class Login(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=True,
            help='No password provided',
            location=['form', 'json']
        )
        super().__init__()
    def post(self):
        try:
            args = self.reqparse.parse_args()
            user = models.User.get(models.User.username==args['username'])
            if(user):
                if(check_password_hash(user.password, args['password'])):
                    return make_response(
                        json.dumps({
                            'user': marshal(user, user_fields),
                            'message': "success",
                        }), 202)
                else:
                    return make_response(
                        json.dumps({
                            'message': "incorrect password"
                        }), 401)
        except models.User.DoesNotExist:
            return make_response(
                json.dumps({
                    'message': "Username does not exist"
                }), 401) 

class Logout(Resource):
    @login_required
    def get(self):
        logout_user()
        print('user has logged out')
        return "user has logged out"





users_api = Blueprint('resources.users', __name__)
api = Api(users_api)
api.add_resource(
    UserList,
    '/'
)
api.add_resource(
    Login,
    '/login'
)

api.add_resource(
    User, 
    '/<int:id>',
)

api.add_resource(
    Logout, 
    '/logout',
)