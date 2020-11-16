from flask import jsonify, make_response

from DAOs.UsersDao import UsersDao
from Handlers.ParentHandler import ParentHandler
import re

USERKEYS = {"email":str, "type":str}
TYPES = ["admin", "user"]

class UsersHandler(ParentHandler):

    def __init__(self):
        super().__init__()
        self.UsersDao = UsersDao()
        self.NestsHandler = None

    def setNestHandler(self, nestsHandler):
        self.NestsHandler = nestsHandler

    def getAllUsers(self):
        """
        Function to get all users in the database.
        :return:
            response with status code 404: Status code due to there not being any users in the system. Response
                will have the format:
                {
                    "Error": "error information string"
                }
            response with status code 200: Status code acknowledges request was successful. Response will have the
                format:
                [
                    {
                        "_id": document_id,
                        "email": user_email,
                        "type": user_type
                    },
                    {
                        "_id": document_id,
                        "email": user_email,
                        "type": user_type
                    },
                    .
                    .
                    .
                ]
            response with status code 500: Response code signifies there was an error in the server while processing
            the request.
        """
        try:
            user = self.UsersDao.getAllUsers()
            if user is None or len(user) == 0:
                response = make_response(jsonify(Error="No users on system"), 404)
            else:
                response = make_response(jsonify(user), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getUser(self, userid):
        """
        Function to Get a Specific User from the database using the document id as an identifier. Will perform
        validation for id to verify it is not empty and it has the correct length. Will also verify id belongs to an
        actual user in the database.
        :param userid: ID of the database document holding the user information.
        :return: response with status code 404: Response code due to the document id not existing on the user
                collection in the database. Response will have the format:
                {
                    "Error": "error information string"
                }
            response with status code 400: Response code due to the id passed as a parameter not being valid. Response
                will have the same format as the 404 response explained above.

            response with status code 200: Response code acknowledges request was successful. Response will have the
                format:
                    {
                        "_id": document_id,
                        "email": user_email,
                        "type": user_type
                    }
            response with status code 500: Response code signifies there was an error in the server while processing
            the request.
        """
        try:
            if userid is None:
                return make_response(jsonify(Error="userid is incorrect format"), 400)
            if self.verifyIDString(userid) is False:
                return make_response(jsonify(Error="ID must be a valid 24-character hex string"), 400)

            user = self.getUserExternal(userid)
            if user is None:
                response = make_response(jsonify(Error="No user with this id"), 404)
            else:
                response = make_response(jsonify(user), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getUserExternal(self, userid):
        return self.UsersDao.getUserByID(userid)

    def getUserByEmail(self, email):
        """
        Function to get user a unique user from the database by their email
        :param email: email of desired user
        :return:
        """
        try:
            user = self.UsersDao.getUserByEmail(email)
            if user is None:
                response = make_response(jsonify(Error="No user with this email"), 404)
            else:
                response = make_response(jsonify(user), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def insertuser(self, user):
        """
        Function to insert Users in the database. Will validate JSON parameter corresponding to the request body of
        the API route /nestmatics/users. Validation will make sure request.json has the required keys and also that
        the value of keys are of the correct type. If values are not expected, if keys are missing, if user is already
        registered, if values of "email" key or "type" key are not valid, 4xx client errors will be issued. If request
        is accepted, the json parameter will the user information will be inserted in the database
        :param user: json object with new user information. Should have the format:
            {
                "email":"user_email@domain.com",
                "type":"user_type"
            }
            ** domain should be either gmail or skootel
            ** user_type should be either "user" or "admin"
        :return:
            response with status code 400: missing fields, incorrect value type, incorrect email domain,
                incorrect user_type value.
            response with status code 201: successful insertion of new user into system. Will return an HTTP response
                with the format:
                { "ok":
                    { "_id": id_Number  }
                }
                ** id_Number refers to the db id for the newly inserted field
            response with status code 500: error in server
            response with status code 403: request was ok but user is already registered in system
        """
        try:
            for key in USERKEYS:
                if key not in user:
                    return make_response(jsonify(Error='Missing fields from submission: ' + key), 400)
                keyType = USERKEYS[key]
                print("key tye: ", keyType)
                print("user[key]: ", type(user[key]))
                if type(user[key]) is not keyType:
                    return make_response(jsonify(Error='Key ' + key+' is not the expected type: '+str(keyType)), 400)

            if user["type"] == TYPES[0] or user["type"] == TYPES[1]:

                if re.match(r"^[\w.\-]{1,25}@(skootel|gmail)\.com(\W|$)", user["email"]):
                    findUser = self.UsersDao.getUserByEmail(user['email'])
                    if findUser is not None:
                        return make_response(jsonify(Error='User already registered'), 403)

                    print(user)
                    id = self.UsersDao.insertUser(user)
                    print(id)
                    if id is None:
                        response = make_response(jsonify(Error="Error on insertion"), 404)
                    else:
                        response = make_response(jsonify(ok={"_id": id}), 201)
                    return response

                else:
                    print(user["email"])
                    return make_response(jsonify(Error='Email should be @gmail.com or @skootel.com '
                                                       'and include at least one character before domain.'), 400)
            else:
                return make_response(jsonify(Error='Type should be "admin" or "user"'), 400)
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def deleteUser(self, userid):
        """
        Delete a specified user from the database. User to be deleted is identified by the userid passed as a
        parameter.
        :param userid: ID of the user to delete
        :return:
            response with status code 201: successful insertion of new user into system. Will return an HTTP response
                with the format:
                { "ok":
                    { "deleted": number_of_documents_deleted  }
                }

            response with status code 400: User Id in incorrect format.
            response with status code 500: error in server.
            response with status code 404: No user with specified ID, no user was found to delete.
            Response for codes 400,404,500 will have format:
            {
                "Error": "error information string"
            }

        """
        try:
            if userid is None:
                return make_response(jsonify(Error="userid is incorrect format"), 400)
            if self.verifyIDString(userid) is False:
                return make_response(jsonify(Error="ID must be a valid 24-character hex string"), 400)

            findUser = self.UsersDao.getUserByID(userid)
            if findUser is None:
                return make_response(jsonify(Error="No User with that ID"), 404)

            nests = self.NestsHandler.deleteNestsByUserID(userid)

            result = self.UsersDao.deleteUser(str(userid))
            if result == 0 or result is None:
                response = make_response(jsonify(Error="No User was deleted"), 404)
            else:
                response = make_response(jsonify(ok={"deleted_user": str(result),
                                                     "deleted_nests":nests}), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)
