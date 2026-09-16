import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from data5580_hw.services.database.user_sql import UserSQL

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def validate_email(email):
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email))


@dataclass
class User(object):
    id: str
    name: str
    email: str
    updated: Optional[datetime] = field(default_factory=datetime.now)
    created: Optional[datetime] = field(default_factory=datetime.now)

    def to_user_sql(self) -> UserSQL:
        return UserSQL(
            id=self.id,
            name=self.name,
            email=self.email,
            created=self.created,
            updated=self.updated,
        )

    @classmethod
    def from_user_sql(cls, user_sql: UserSQL) -> Optional["User"]:
        if not user_sql:
            return None
        return cls(
            id=user_sql.id,
            name=user_sql.name,
            email=user_sql.email,
            created=user_sql.created,
            updated=user_sql.updated,
        )
