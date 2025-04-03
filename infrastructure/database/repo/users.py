from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from infrastructure.database.models import User, Purchase
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_or_create_user(self, id: int, full_name: str, is_premium: bool, username: Optional[str] = None, deeplink: Optional[int] = None) -> User:
        """Получение или создание пользователя"""
        # Check if the user already exists
        user = await self.session.execute(select(User).filter_by(id=id))
        user = user.scalar_one_or_none()

        if user:
            return user

        insert_stmt = (
            insert(User)
            .values(
                id=id,
                full_name=full_name,
                username=username,
                deeplink=deeplink,
                is_premium=is_premium
            )
            .returning(User)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()  # Avoids try-except block

    async def update_user(self, user_id: int, username: Optional[str] = None) -> Optional[User]:
        """Обновление данных пользователя"""
        async with self.session.begin():
            user = await self.get_user_by_id(user_id)
            if user:
                if username is not None:
                    user.username = username
                await self.session.commit()
                return user
        return None

    async def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        async with self.session.begin():
            result = await self.session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                await self.session.delete(user)
                await self.session.commit()
                return True
        return False

    async def get_all_users(self) -> List[dict]:
        stmt = (
            select(User, Purchase.is_paid)
            .outerjoin(Purchase, User.id == Purchase.user_id)  # ← заменили на outerjoin
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "user": row[0],
                "is_paid": row[1],  # будет None, если покупок нет
            }
            for row in rows
        ]


    async def get_users_with_payment(self) -> List[dict]:
        stmt = (
            select(User, Purchase.is_paid)
            .join(Purchase, User.id == Purchase.user_id)
            .where(Purchase.is_paid == True)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "user": row[0],
                "is_paid": row[1],
            }
            for row in rows
        ]

    async def get_users_without_payment(self) -> List[dict]:
        stmt = (
            select(User, Purchase.is_paid)
            .outerjoin(Purchase, User.id == Purchase.user_id)
            .where(or_(Purchase.is_paid == False, Purchase.is_paid == None))
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "user": row[0],
                "is_paid": row[1],
            }
            for row in rows
        ]
