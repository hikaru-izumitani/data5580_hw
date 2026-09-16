from flask import Blueprint

# In-app modules
from data5580_hw.controllers.user_controller import user_controller

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/user', methods=['POST'])
def create_user():
    return user_controller.create_user()


@user_blueprint.route('/user/<user_id>', methods=['GET'])
def get_user(user_id: str):
    return user_controller.get_user(user_id)
