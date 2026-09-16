from flask import Flask, jsonify, request

from data5580_hw.routes import init_blueprints
from data5580_hw.services.database.database_client import init_db

# $body = @{
#     a = 5
#     b = 7
# } | ConvertTo-Json
#
# Invoke-RestMethod `
#     -Uri "http://localhost:5000/add" `
#     -Method Post `
#     -ContentType "application/json" `
#     -Body $body

def create_app():
    app = Flask(__name__)

    from data5580_hw.config import Config

    app.config.from_object(Config)

    init_db(app)

    @app.route('/')
    def index():
        return jsonify({'message': 'Hello World!'})

    init_blueprints(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
