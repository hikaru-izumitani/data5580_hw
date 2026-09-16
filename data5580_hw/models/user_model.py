from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from data5580_hw.services.database.user_sql import UserSQL
from data5580_hw.services.database.database_client import db


@dataclass
class User(object):
    id: str
    name: str
    email: str
    updated: Optional[datetime] = field(default_factory=datetime.now)
    created: Optional[datetime] = field(default_factory=datetime.now)

    def to_user_sql(self) -> UserSQL:

        return UserSQL(id=self.id
                       , name=self.name
                       , email=self.email
                       , created=self.created
                       , updated=self.updated
                        )

    @classmethod
    def from_user_sql(cls, id_):
        user_sql = db.session.query(UserSQL).filter(UserSQL.id == id_).first()

        return cls(
            id=user_sql.id
            , name=user_sql.name
            , email=user_sql.email
            , created=user_sql.created
            , updated=user_sql.updated
        )
