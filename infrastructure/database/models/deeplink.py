from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from .base import Base, TimestampMixin, TableNameMixin

class Deeplink(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String)
    target: Mapped[str] = mapped_column(String)
    link: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f"<Deeplink {self.id} {self.source} {self.target} {self.link}>"