import pytest

from data5580_hw.app_old import create_app
from data5580_hw.controllers.user_controller import UserController


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

"""
def test_create_user(client):
    user_controller = UserController()

    user_controller.create_user()"""