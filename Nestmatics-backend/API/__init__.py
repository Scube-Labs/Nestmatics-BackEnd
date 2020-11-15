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
ServiceAreaHandler = ServiceAreaHandler()
ModelHandler = ModelHandler()
RidesHandler = RidesHandler(RideStatsHandler, ServiceAreaHandler, NestsHandler)
RideStatsHandler = RideStatsHandler(ServiceAreaHandler)
NestsHandler = NestsHandler(UsersHandler, ServiceAreaHandler, RidesHandler)
DropStrategyHandler = DropStrategyHandler(ServiceAreaHandler)
ExperimentsHandler = ExperimentsHandler(NestsHandler)

