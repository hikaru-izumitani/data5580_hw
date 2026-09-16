from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=BaseModel)


def init_db(app) -> None:
    import data5580_hw.services.database.user_sql  # noqa: F401

    db.init_app(app)

    with app.app_context():
        db.create_all()
