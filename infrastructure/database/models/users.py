from typing import Optional

from sqlalchemy import String, BIGINT, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, TableNameMixin


class User(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    full_name: Mapped[str] = mapped_column(String)
    username: Mapped[Optional[str]] = mapped_column(String(128))
    deeplink: Mapped[int] = mapped_column(BIGINT, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=True)

    def __repr__(self):
        return f"<User {self.id} {self.username}>"
