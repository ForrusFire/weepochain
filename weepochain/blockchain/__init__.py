import flask
from flask_cors import CORS

from .blockchain import Blockchain


# Create the blockchain instance
blockchain = Blockchain()


def create_app():
    app = flask.Flask(__name__)
    app.config["DEBUG"] = True
    CORS(app)

    from .views import bp
    app.register_blueprint(bp)

    return app
