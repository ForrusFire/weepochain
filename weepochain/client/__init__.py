import flask


def create_app():
    app = flask.Flask(__name__)
    app.config["DEBUG"] = True

    from .views import bp
    app.register_blueprint(bp)

    return app
