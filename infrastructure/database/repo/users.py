from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.orm import aliased

from infrastructure.database.models import User, Purchase, Lesson
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
        # Используем session.get для извлечения пользователя по первичному ключу
        return await self.session.get(User, user_id)  # Avoids try-except block

    async def update_user(self, user_id: int, username: Optional[str] = None) -> Optional[User]:
        """Обновление данных пользователя"""
        # Открываем асинхронную сессию и начинаем транзакцию
        async with self.session as session:
            await session.begin()
            # begin() автоматически начнёт транзакцию
            # Получаем пользователя из базы данных
            result = await self.session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()  # Получаем пользователя или None

            if user:
                if username is not None:
                    user.username = username
                # Если нужно, можно явно вызвать commit() для сохранения изменений
                await self.session.commit()  # Обычно в async контексте commit нужно делать вручную

        # Возвращаем обновленного пользователя
        return user

    async def delete_user(self, user_id: int) -> bool:
        try:
            # Начинаем транзакцию
            async with self.session as session:
                await session.begin()
                # Открываем транзакцию
                # Получаем пользователя из базы данных с использованием метода select
                user = await self.session.get(User, user_id)

                if user:
                    # Удаляем пользователя
                    await self.session.delete(user)
                    return True  # Если пользователь найден и удален
                else:
                    return False  # Если пользователь не найден
        except SQLAlchemyError as e:
            # Логируем ошибку при работе с SQLAlchemy
            raise
        except Exception as e:
            # Логируем ошибку или обрабатываем исключение, если необходимо
            print(f"Error while deleting user: {e}")

    async def get_all_users(self) -> List[dict]:
        lesson_alias = aliased(Lesson)  # Создаём псевдоним для таблицы Lesson

        stmt = (
            select(User, Purchase.is_paid, lesson_alias.lesson_number)
            .outerjoin(Purchase, User.id == Purchase.user_id)
            .outerjoin(lesson_alias, User.id == lesson_alias.user_id)  # Добавляем соединение с таблицей Lesson
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "user": row[0],
                "is_paid": row[1],  # будет None, если покупок нет
                "lesson_number": row[2]  # добавляем lesson_number
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
