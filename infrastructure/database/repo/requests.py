from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repo.deeplink import DeeplinkRepo
from infrastructure.database.repo.lessons import LessonRepo
from infrastructure.database.repo.products import ProductRepo
from infrastructure.database.repo.purchases import PurchaseRepo
from infrastructure.database.repo.users import UserRepo

@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def purchases(self) -> PurchaseRepo:
        return PurchaseRepo(self.session)

    @property
    def products(self) -> ProductRepo:
        return ProductRepo(self.session)

    @property
    def deeplink(self) -> DeeplinkRepo:
        return DeeplinkRepo(self.session)

    @property
    def lessons(self) -> LessonRepo:
        return LessonRepo(self.session)
