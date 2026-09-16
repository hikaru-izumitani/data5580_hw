import uuid
from dataclasses import asdict

from flask import jsonify, request

from data5580_hw.models.user_model import User
from data5580_hw.services.database.database_client import db
from data5580_hw.services.database.user_sql import UserSQL


class UserController(object):

    @staticmethod
    def create_user() -> tuple[str, int]:

        request_data = request.get_json()

        id_ = uuid.uuid4().hex

        try:
            user_ = User(
                id=id_,
                name=request_data['name'],
                email=request_data['email'],
            )

            user_sql = user_.to_user_sql()

            db.session.add(user_sql)

            db.session.commit()

            user_sql = db.session.query(UserSQL).filter(UserSQL.id == id_).one_or_none()

            user_ = User.from_user_sql(user_sql)

        except KeyError as e:
            return jsonify({'error': str(e)}), 400

        return jsonify(asdict(user_)), 200

    def get_user(self, user_id: str) -> tuple[str, int]:

        user_sql = db.session.query(User).filter(User.id == user_id).one_or_none()

        user_ = User.from_user_sql(user_sql)

        return jsonify(user_), 200


user_controller = UserController()
