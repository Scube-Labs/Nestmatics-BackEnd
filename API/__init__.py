from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config["DEBUG"] = True

# Apply CORS to this app
CORS(app)