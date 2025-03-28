from typing import Optional, List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from sqlalchemy import update, func

from infrastructure.database.models import User
from infrastructure.database.models.purchases import Purchase
from infrastructure.database.repo.base import BaseRepo


class PurchaseRepo(BaseRepo):
    async def create_purchase(self, user_id: int, product_id: int, amount: int) -> Purchase:
        """Создание новой покупки"""
        insert_stmt = (
            insert(Purchase)
            .values(
                user_id=user_id, product_id=product_id, amount=amount
            )
            .returning(Purchase)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_purchase_by_id(self, purchase_id: int) -> Optional[Purchase]:
        """Получение покупки по ID"""
        result = await self.session.execute(
            select(Purchase).where(Purchase.id == purchase_id)
        )
        return result.scalar_one_or_none()  # Avoids try-except

    async def get_purchase_by_user(self, user_id: int) -> Purchase:
        """Получение всех покупок пользователя"""
        result = await self.session.execute(
            select(Purchase).where(Purchase.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_purchase(
            self,
            id: int,
            payment_id: Optional[int] = None,
            link: Optional[int] = None
    ) -> Optional[Purchase]:
        """Обновление информации о покупке"""
        # Build the update statement
        update_stmt = (
            update(Purchase).values(payment_id=payment_id, link=link).where(Purchase.id == id)
        )

        # Execute the update and fetch the updated record
        await self.session.execute(update_stmt)

        # Commit the transaction
        await self.session.commit()

    async def toggle_is_paid(
            self,
            id: int,
    ) -> Optional[Purchase]:
        """Обновление информации о покупке"""
        # Build the update statement
        update_stmt = (
            update(Purchase).values(is_paid=True).where(Purchase.id == id)
        )

        # Execute the update and fetch the updated record
        await self.session.execute(update_stmt)

        # Commit the transaction
        await self.session.commit()

    async def delete_purchase(self, purchase_id: int) -> bool:
        """Удаление покупки"""
        async with self.session.begin():
            result = await self.session.execute(
                select(Purchase).where(Purchase.id == purchase_id)
            )
            purchase = result.scalar_one_or_none()
            if purchase:
                await self.session.delete(purchase)
                await self.session.commit()
                return True
        return False

    async def count_users(self) -> int:
        """Подсчет количества пользователей"""
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar_one()

    async def get_paid_users_count(self) -> int:
        """Подсчет количества пользователей, которые совершили оплату"""
        result = await self.session.execute(
            select(func.count(User.id))
            .join(Purchase, Purchase.user_id == User.id)
            .filter(Purchase.is_paid == True)
        )
        return result.scalar_one()
