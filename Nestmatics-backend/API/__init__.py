from flask import Flask
from flask_cors import CORS

from Handlers.RidesHandler import RidesHandler
from Handlers.NestsHandler import NestsHandler
from Handlers.RideStatsHandler import RideStatsHandler
from Handlers.UsersHandler import UsersHandler
from Handlers.ServiceAreaHandler import ServiceAreaHandler
from Handlers.DropStrategyHandler import DropStrategyHandler
from Handlers.ExperimentsHandler import ExperimentsHandler
from Handlers.ModelHandler import ModelHandler

app = Flask(__name__)
app.config["DEBUG"] = True

UPLOAD_FOLDER = '././ridesData'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Apply CORS to this app
CORS(app)

UsersHandler = UsersHandler()
ModelHandler = ModelHandler()
RideStatsHandler = RideStatsHandler()

NestsHandler = NestsHandler()
DropStrategyHandler = DropStrategyHandler()
ExperimentsHandler = ExperimentsHandler()

RidesHandler = RidesHandler()
ServiceAreaHandler = ServiceAreaHandler()

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
