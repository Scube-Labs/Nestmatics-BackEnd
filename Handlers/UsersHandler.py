from re import search

from flask import jsonify, make_response
from datetime import datetime

from DAOs.UsersDao import UsersDao
from DAOs.ParentDao import ParentDao

USERKEYS = ["email", "privilege"]

class UsersHandler(ParentDao):

    def getAllUsers(self):
        try:
            user = UsersDao().getAllUsers()
            if user is None:
                response = make_response(jsonify(error="No users on system"), 404)
            else:
                response = make_response(jsonify(user), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getUser(self, userid):
        try:
            user = UsersDao().getUser(userid)
            if user is None:
                response = make_response(jsonify(error="No user with this id"), 404)
            else:
                response = make_response(jsonify(user), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def insertuser(self, user):
        for key in USERKEYS:
            if key not in user:
                return jsonify(Error='Missing fields from submission: ' + key)

        if (user["email"].find('@gmail.com') != -1) or (user["email"].find('@skootel.com') != -1):

            try:
                id = UsersDao().insertUser(user)
                if id is None:
                    response = make_response(jsonify(error="Error on insertion"), 404)
                else:
                    response = make_response(jsonify(ok=id), 200)
                return response
            except:
                response = make_response(jsonify("there was an error on the request"), 400)
                return response
        else:
            print(user["email"])
            return jsonify(Error='Email should be @gmail.com or @skootel.com')

    def deleteUser(self, userid):
        try:
            result = UsersDao().deleteUser(userid)
            if result is None:
                response = make_response(jsonify(error="No Nest with that ID"), 404)
            else:
                response = make_response(jsonify(ok="deleted "+ result +" entries"), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response