import flask


def create_app():
    app = flask.Flask(__name__)
    app.config["DEBUG"] = True

    from endpoints import bp
    app.register_blueprint(bp)

    return app


if __name__ == '__main__':
    from argparse import ArgumentParser

    app = create_app()

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)