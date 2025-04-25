from typing import Optional
from sqlalchemy import BIGINT, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base, TimestampMixin, TableNameMixin

class Lesson(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.id'), nullable=False)
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[Optional[str]] = mapped_column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return f"<Lesson(user_id={self.user_id}, lesson_number={self.lesson_number}, completed_at={self.completed_at})>"