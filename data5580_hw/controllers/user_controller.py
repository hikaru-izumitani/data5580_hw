import uuid
from dataclasses import asdict
from datetime import datetime

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from data5580_hw.models.user_model import User, validate_email
from data5580_hw.services.database.database_client import db
from data5580_hw.services.database.user_sql import UserSQL


def error_response(message, status):
    return jsonify({"error": message}), status


class UserController(object):

    def _query_user(self, user_id):
        return db.session.query(UserSQL).filter(UserSQL.id == user_id).one_or_none()

    def _request_json(self):
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else {}

    def _commit(self):
        try:
            db.session.commit()
            return None
        except IntegrityError:
            db.session.rollback()
            return error_response("the email is already in use", 400)

    def _user_payload(self, user_sql, message=None):
        data = asdict(User.from_user_sql(user_sql))
        if message:
            data["message"] = message
        return jsonify(data), 200

    def create_user(self) -> tuple:
        request_data = self._request_json()
        try:
            email = request_data["email"]
            name = request_data["name"]
        except KeyError as exc:
            return error_response(f"{exc.args[0]} is required", 400)

        if not validate_email(email):
            return error_response("Invalid email format", 400)

        user = User(id=uuid.uuid4().hex, name=name, email=email)
        db.session.add(user.to_user_sql())
        commit_error = self._commit()
        if commit_error:
            return commit_error

        return self._user_payload(self._query_user(user.id), "User created successfully.")

    def get_user(self, user_id: str) -> tuple:
        user_sql = self._query_user(user_id)
        if not user_sql:
            return error_response("User not found", 404)
        return jsonify(asdict(User.from_user_sql(user_sql))), 200

    def patch_user(self, user_id: str) -> tuple:
        user_sql = self._query_user(user_id)
        if not user_sql:
            return error_response("User not found", 404)

        request_data = self._request_json()
        if "name" not in request_data and "email" not in request_data:
            return error_response(
                "No valid fields to update. You need name or email to update",
                400,
            )

        if "name" in request_data:
            user_sql.name = request_data["name"]
        if "email" in request_data:
            if not validate_email(request_data["email"]):
                return error_response("Invalid email format", 400)
            user_sql.email = request_data["email"]

        user_sql.updated = datetime.now()
        commit_error = self._commit()
        if commit_error:
            return commit_error
        return self._user_payload(user_sql, "User updated successfully.")

    def put_user(self, user_id: str) -> tuple:
        user_sql = self._query_user(user_id)
        if not user_sql:
            return error_response("User not found", 404)

        request_data = self._request_json()
        if not request_data:
            return error_response(
                "No valid fields to update. You need name and email.",
                400,
            )
        if "name" not in request_data:
            return error_response("You need name to update.", 400)
        if "email" not in request_data:
            return error_response("You need email to update.", 400)
        if not validate_email(request_data["email"]):
            return error_response("Invalid email format", 400)

        user_sql.name = request_data["name"]
        user_sql.email = request_data["email"]
        user_sql.updated = datetime.now()
        commit_error = self._commit()
        if commit_error:
            return commit_error
        return self._user_payload(user_sql, "User details updated successfully.")

    def delete_user(self, user_id: str) -> tuple:
        user_sql = self._query_user(user_id)
        if not user_sql:
            return error_response("User not found", 404)
        db.session.delete(user_sql)
        db.session.commit()
        return jsonify({"message": "User deleted successfully."}), 200

    def fetch_all_users(self) -> tuple:
        users = db.session.query(UserSQL).all()
        return jsonify([asdict(User.from_user_sql(user)) for user in users]), 200


user_controller = UserController()
