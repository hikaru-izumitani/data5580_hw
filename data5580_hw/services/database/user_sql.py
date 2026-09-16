from sqlalchemy import UniqueConstraint, Index

from data5580_hw.services.database.database_client import db


class UserSQL(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    UniqueConstraint(email)