from flask import Flask, jsonify

from data5580_hw.routes import init_blueprints
from data5580_hw.services.database.database_client import init_db


def create_app(test_config=None):
    app = Flask(__name__)

    from data5580_hw.config import Config

    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    init_db(app)

    @app.route("/")
    def index():
        return jsonify({"message": "Hello World!"})

    init_blueprints(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
