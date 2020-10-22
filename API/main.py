from flask import Flask, jsonify, request

# Import Cross-Origin Resource Sharing to enable
# services on other ports on this machine or on other
# machines to access this app
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config["DEBUG"] = True

# Apply CORS to this app
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "henlo"

#TODO
@app.route('/nestmatics/rides/position/area/', methods=['GET'])
def getRidesCoordinates():
    return "henlo"

if __name__ == '__main__':
    app.run(debug=True)
