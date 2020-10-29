from bson import ObjectId
from DAOs.ParentDao import ParentDao

class UsersDao(ParentDao):

    def getAllUsers(self):
        users = []
        cursor = self.usersCollection.find({})
        if cursor is not None:
            for i in cursor:
                i["_id"] = str(i["_id"])
                users.append(i)
        return users

    def getUser(self, userid):
        cursor = self.usersCollection.find_one({"_id": ObjectId(userid)})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def insertUser(self, user):
        cursor = self.usersCollection.insert_one(user)
        print(cursor.inserted_id)
        id = (str(cursor.inserted_id))
        return id

    def deleteUser(self, userid):
        cursor = self.usersCollection.delete_one({"_id": ObjectId(userid)})
        return cursor.deleted_count

#print(UsersDao().deleteUser("5f91c682bc71a04fda4b9dc4"))