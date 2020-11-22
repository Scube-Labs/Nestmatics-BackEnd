from bson import ObjectId
from datetime import datetime, timedelta
from DAOs.ParentDao import ParentDao

class DropStrategyDao(ParentDao):

    def __init__(self, db):
        #super().__init__()
        self.dropStrategyCollection = db["drop_strategies"]

    def insertDropStrategy(self, data):
        """
        insert a drop strategy in the database
        :param data: data of drop strategy to insert
        :return: if of newly inserted document
        """
        cursor = self.dropStrategyCollection.insert_one(data)
        return self.insertOne(cursor)

    def getDropStrategyForDate(self, start_date, end_date, areaid):
        """
        Get drop strategy for date specified on are specified
        :param start_date: start date of drop stretegy to find
        :param end_date: end date of drop strategy to find
        :param areaid: ID of area from which to get drop strategy
        :return: drop strategies that meet specified criteria
        """
        cursor = self.dropStrategyCollection.find({"start_date": {"$gte": start_date},
                                                   "end_date": {"$lte": end_date},
                                                    "service_area": areaid})
        return self.returnMany(cursor)

    def getDropStrategiesForArea(self, areaid):
        """
        Gets drop strategy for a specified area
        :param areaid: ID of area from which to find drop strategies
        :return: drop strategies that area in specified area
        """
        cursor = self.dropStrategyCollection.find({"service_area": areaid})
        return self.returnMany(cursor)

    def getDropStrategyFromId(self, dropid):
        """
        Gets a drop strategy identified by provided id
        :param dropid: d of drop strategy to retrieve
        :return: drop strategy identified by provided id
        """
        cursor = self.dropStrategyCollection.find_one({"_id": ObjectId(dropid)})
        return self.returnOne(cursor)

    def getMostRecentDropStrategy(self, areaid):
        """
        Gets most recently made drop strategy
        :param areaid:
        :return:
        """
        cursor = self.dropStrategyCollection.find({"service_area":areaid}).\
            sort([("start_date", -1)]).limit(1)
        return self.returnMany(cursor)

    def deleteDropStrategy(self, dropid):
        """
        Deletes a drop strategy identified by id provided
        :param dropid: Id of drop strategy to delete
        :return:
        """
        cursor = self.dropStrategyCollection.delete_one({"_id": ObjectId(dropid)})
        return cursor.deleted_count

    def deleteDropStrategyByArea(self, areaid):
        """
        Deletes a drop strategy identified by id provided
        :param dropid: Id of drop strategy to delete
        :return:
        """
        cursor = self.dropStrategyCollection.delete_many({"service_area": areaid})
        return cursor.deleted_count

    def editDropStrategy(self, dropid, dayNum, config):
        cursor = self.dropStrategyCollection.update_one({"_id": ObjectId(dropid)},
                                                 { "$set":
                                                 {"days."+dayNum+".configurations": config}})
        return cursor.modified_count






