from typing import Optional, List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select

from infrastructure.database.models.deeplink import Deeplink
from infrastructure.database.repo.base import BaseRepo


class DeeplinkRepo(BaseRepo):
    async def create_deeplink(self, source: str, target: str, link: Optional[str] = None) -> Deeplink:
        insert_stmt = (
            insert(Deeplink)
            .values(source=source, target=target, link=link)
            .returning(Deeplink)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

    async def get_deeplink_by_id(self, deeplink_id: int) -> Optional[Deeplink]:
        result = await self.session.execute(
            select(Deeplink).where(Deeplink.id == deeplink_id)
        )
        return result.scalar_one_or_none()  # Avoids exception handling manually

    async def get_all_deeplinks(self) -> List[Deeplink]:
        result = await self.session.execute(select(Deeplink))
        return result.scalars().all()

    async def update_deeplink(self, deeplink_id: int, source: Optional[str] = None, target: Optional[str] = None, link: Optional[str] = None) -> Optional[Deeplink]:
        async with self.session.begin():
            deeplink = await self.get_deeplink_by_id(deeplink_id)
            if deeplink:
                if source is not None:
                    deeplink.source = source
                if target is not None:
                    deeplink.target = target
                if link is not None:
                    deeplink.link = link
                await self.session.commit()
                return deeplink
        return None

    async def delete_deeplink(self, deeplink_id: int) -> bool:
        async with self.session.begin():
            result = await self.session.execute(
                select(Deeplink).where(Deeplink.id == deeplink_id)
            )
            deeplink = result.scalar_one_or_none()
            if deeplink:
                await self.session.delete(deeplink)
                await self.session.commit()
                return True
        return False
