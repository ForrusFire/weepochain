import flask
from flask_cors import CORS

from .blockchain import Blockchain
from .nodes import NodeNetwork
from .database import load_blocks


# Create the blockchain instance
blockchain = Blockchain()

# Loads the blockchain from the database
load_blocks(blockchain)

# Create the node network instance
node_network = NodeNetwork()


def create_app():
    app = flask.Flask(__name__)
    app.config["DEBUG"] = True
    CORS(app)

    from .views import bp
    app.register_blueprint(bp)

    return app
