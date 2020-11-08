from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config["DEBUG"] = True

UPLOAD_FOLDER = '././ridesData'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Apply CORS to this app
CORS(app)