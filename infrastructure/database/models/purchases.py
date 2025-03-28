from sqlalchemy import BIGINT, Integer, ForeignKey, String, Boolean, Sequence
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, TableNameMixin


class Purchase(Base, TimestampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True,
                                    autoincrement=True,
                                    default=Sequence('purchase_id_seq', start=50))
    payment_id: Mapped[int] = mapped_column(BIGINT, nullable=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('products.id'), nullable=False)
    link: Mapped[str] = mapped_column(String, nullable=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<Purchase {self.id} {self.user_id} {self.product_id} {self.amount}>"
