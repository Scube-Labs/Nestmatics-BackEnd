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

    def getUserByID(self, userid):
        cursor = self.usersCollection.find_one({"_id": ObjectId(userid)})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def getUserByEmail(self, email):
        cursor = self.usersCollection.find_one({"email": email})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def insertUser(self, user):
        cursor = self.usersCollection.insert_one(user)
        id = (str(cursor.inserted_id))
        return id

    def deleteUser(self, userid):
        cursor = self.usersCollection.delete_one({"_id": ObjectId(userid)})
        return cursor.deleted_count

# item = {
#     "email":"bean@gmail.com",
#     "privilege":"user"
# }
#print(UsersDao().insertUser(item))