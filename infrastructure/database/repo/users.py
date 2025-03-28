from typing import Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select

from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_or_create_user(self, id: int, username: Optional[str] = None, deeplink: Optional[int] = None) -> User:
        """Получение или создание пользователя"""
        # Check if the user already exists
        user = await self.session.execute(select(User).filter_by(id=id))
        user = user.scalar_one_or_none()

        if user:
            return user

        insert_stmt = (
            insert(User)
            .values(id=id, username=username, deeplink=deeplink)
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
