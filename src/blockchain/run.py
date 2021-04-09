import flask
from flask_cors import CORS

from blockchain import Blockchain


# Create the blockchain
blockchain = Blockchain()

def create_app():
    app = flask.Flask(__name__)
    app.config["DEBUG"] = True
    CORS(app)

    from endpoints import bp
    app.register_blueprint(bp)

    return app


if __name__ == '__main__':
    from argparse import ArgumentParser

    app = create_app()

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)