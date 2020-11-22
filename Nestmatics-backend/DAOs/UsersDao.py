from bson import ObjectId
from DAOs.ParentDao import ParentDao


class UsersDao(ParentDao):

    def __init__(self, db):
        #super().__init__()
        self.usersCollection = db["users"]

    def getAllUsers(self):
        """
        Gets all users from database
        :return: dictionary with all users of system
        """
        cursor = self.usersCollection.find()
        return self.returnMany(cursor)

    def getUserByID(self, userid):
        """
        Gets a specific user from the database identified by a provided userid
        :param userid: ID of the user to get from the database
        :return: dictionary with user data
        """
        cursor = self.usersCollection.find_one({"_id": ObjectId(userid)})
        return self.returnOne(cursor)

    def getUserByEmail(self, email):
        """
        Gets a specific user from the database identified by a provided email
        :param email: email of the user to get from the database
        :return: dictionary with user data
        """
        cursor = self.usersCollection.find_one({"email": email})
        return self.returnOne(cursor)

    def insertUser(self, user):
        """
        Insert a user into the database
        :param user: new user information
        :return: id of inserted user
        """
        cursor = self.usersCollection.insert_one(user)
        return self.insertOne(cursor)

    def deleteUser(self, userid):
        """
        Delete a specified user from the database
        :param userid: ID identifying the user to delete
        :return: number of documents deleted
        """
        cursor = self.usersCollection.delete_one({"_id": ObjectId(userid)})
        return cursor.deleted_count
