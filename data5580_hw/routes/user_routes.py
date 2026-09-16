from flask import Blueprint

# In-app modules
from data5580_hw.controllers.user_controller import user_controller

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/users', methods=['POST'])
def create_user():
    return user_controller.create_user()


@user_blueprint.route('/users/<user_id>', methods=['GET'])
def get_user(user_id: str):
    return user_controller.get_user(user_id)

@user_blueprint.route('/users/<user_id>', methods=['PATCH'])
def patch_user(user_id: str):
    return user_controller.patch_user(user_id)

@user_blueprint.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id: str):
    return user_controller.delete_user(user_id)

@user_blueprint.route('/users', methods=['GET'])
def fetch_all_users():
    return user_controller.fetch_all_users()

@user_blueprint.route('/users/<user_id>', methods=["PUT"])
def put_user(user_id: str):
    return user_controller.put_user(user_id)