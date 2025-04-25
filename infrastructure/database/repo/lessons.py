from typing import Optional, List
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from infrastructure.database.models import Lesson, User
from infrastructure.database.repo.base import BaseRepo


class LessonRepo(BaseRepo):
    async def get_or_create_lesson_progress(self, user_id: int, lesson_number: int) -> Lesson:
        """Получение или создание записи о прогрессе пользователя по урокам"""
        # Проверка, существует ли уже прогресс для данного пользователя и урока
        lesson = await self.session.execute(
            select(Lesson).filter_by(user_id=user_id, lesson_number=lesson_number)
        )
        lesson = lesson.scalar_one_or_none()

        if lesson:
            return lesson

        # Если прогресс не найден, создаем новый
        insert_stmt = (
            insert(Lesson)
            .values(user_id=user_id, lesson_number=lesson_number)
            .returning(Lesson)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()

        return result.scalar_one()

    async def update_lesson_progress(self, user_id: int) -> Optional[Lesson]:
        """Автоматическое обновление номера урока до 3 включительно для пользователя"""
        async with self.session as session:
            await session.begin()
            lesson = await self.session.execute(
                select(Lesson).filter_by(user_id=user_id)
            )
            lesson = lesson.scalar_one_or_none()

            if not lesson:
                return None

            # Проверяем, что номер урока меньше 3, и увеличиваем его
            if lesson.lesson_number < 3:
                lesson.lesson_number += 1

            await self.session.commit()
            return lesson

    async def get_lesson_progress_by_user(self, user_id: int) -> Optional[Lesson]:
        """Получение прогресса уроков для пользователя"""
        result = await self.session.execute(
            select(Lesson).where(Lesson.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_users_lesson_progress(self) -> List[dict]:
        """Получение прогресса всех пользователей по урокам"""
        stmt = (
            select(Lesson, User)
            .join(User, User.id == Lesson.user_id)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "user": row[1],
                "lesson_number": row[0].lesson_number,
                "completed_at": row[0].completed_at,
            }
            for row in rows
        ]