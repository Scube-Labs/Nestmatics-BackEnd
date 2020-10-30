from re import search

from flask import jsonify, make_response
from datetime import datetime

from DAOs.UsersDao import UsersDao
from DAOs.ParentDao import ParentDao

USERKEYS = {"email":str, "privilege":str}

class UsersHandler(ParentDao):

    def getAllUsers(self):
        try:
            user = UsersDao().getAllUsers()
            if user is None:
                response = make_response(jsonify(Error="No users on system"), 404)
            else:
                response = make_response(jsonify(user), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 400)
            return response

    def getUser(self, userid):
        try:
            user = UsersDao().getUserByID(userid)
            if user is None:
                response = make_response(jsonify(Error="No user with this id"), 404)
            else:
                response = make_response(jsonify(user), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def insertuser(self, user):
        try:
            for key in USERKEYS:
                if key not in user:
                    return jsonify(Error='Missing fields from submission: ' + key)
                keyType = USERKEYS[key]
                print("key tye: ",keyType)
                print("user[key]: ", type(user[key]))
                if type(user[key]) is not keyType:
                    return jsonify(Error='Key ' + key+' is not the expected type: '+str(keyType))

            if (user["email"].find('@gmail.com') != -1) or (user["email"].find('@skootel.com') != -1):
                findUser = UsersDao().getUserByEmail(user['email'])
                if findUser is not None:
                    return jsonify(Error='User already registered')

                print(user)
                id = UsersDao().insertUser(user)
                print(id)
                if id is None:
                    response = make_response(jsonify(Error="Error on insertion"), 404)
                else:
                    response = make_response(jsonify(ok=id), 200)
                return response

            else:
                print(user["email"])
                return jsonify(Error='Email should be @gmail.com or @skootel.com')
        except Exception as e:
            return jsonify(Error=str(e))

    def deleteUser(self, userid):
        try:
            findUser = UsersDao().getUserByID(userid)

            if findUser is None:
                response = make_response(jsonify(Error="No User with that ID"), 404)
                return response

            result = UsersDao().deleteUser(str(userid))
            if result is None:
                response = make_response(jsonify(Error="No Nest with that ID"), 404)
            else:
                response = make_response(jsonify(ok="deleted "+ str(result) +" entries"), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response
