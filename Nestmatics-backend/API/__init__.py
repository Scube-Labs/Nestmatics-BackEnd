from flask import Flask
from flask_cors import CORS

import os
from pymongo import MongoClient

from Handlers.RidesHandler import RidesHandler
from Handlers.NestsHandler import NestsHandler
from Handlers.RideStatsHandler import RideStatsHandler
from Handlers.UsersHandler import UsersHandler
from Handlers.ServiceAreaHandler import ServiceAreaHandler
from Handlers.DropStrategyHandler import DropStrategyHandler
from Handlers.ExperimentsHandler import ExperimentsHandler
from Handlers.ModelHandler import ModelHandler

DB_USERNAME = None
DB_PASSWD = None
DB_HOST = None
PORT = None
try:
    DB_USERNAME = os.environ['DB_USERNAME']
    DB_PASSWD = os.environ['DB_PASWD']
    DB_HOST = os.environ['DB_HOST']
    print("HOST: ", DB_HOST)
    PORT = 27017
except KeyError:
    DB_USERNAME = "root"
    DB_PASSWD = "example"
    DB_HOST = "localhost"
    PORT = 2717

client = MongoClient("mongodb://"+DB_HOST+":"+str(PORT),
                     username=DB_USERNAME,
                     password=DB_PASSWD,
                     connect=False)

db = client["Nestmatics"]

UsersHandler = UsersHandler(db)
ModelHandler = ModelHandler(db)
RideStatsHandler = RideStatsHandler(db)

NestsHandler = NestsHandler(db)
DropStrategyHandler = DropStrategyHandler(db)
ExperimentsHandler = ExperimentsHandler(db)

RidesHandler = RidesHandler(db)
ServiceAreaHandler = ServiceAreaHandler(db)

ServiceAreaHandler.setNestHandler(NestsHandler)
ServiceAreaHandler.setDropsHandler(DropStrategyHandler)
ServiceAreaHandler.setRidesHandler(RidesHandler)
ServiceAreaHandler.setModelHandler(ModelHandler)

RidesHandler.setNestHandler(NestsHandler)
RidesHandler.setServiceAreaHandler(ServiceAreaHandler)
RidesHandler.setRideStatsHandler(RideStatsHandler)

DropStrategyHandler.setSAHandler(ServiceAreaHandler)

NestsHandler.setRidesHandler(RidesHandler)
NestsHandler.setServiceAreaHandler(ServiceAreaHandler)
NestsHandler.setExperimentsHandler(ExperimentsHandler)
NestsHandler.setUsersHandler(UsersHandler)

ExperimentsHandler.setNestHandler(NestsHandler)

RideStatsHandler.setSAHandler(ServiceAreaHandler)

UsersHandler.setNestHandler(NestsHandler)
