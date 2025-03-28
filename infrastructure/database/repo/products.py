from typing import Optional, List

from sqlalchemy.future import select

from infrastructure.database.models.products import Product
from infrastructure.database.repo.base import BaseRepo


class ProductRepo(BaseRepo):
    async def create_product(self, name: str, info: str, description: Optional[str], price: float) -> Product:
        """Создание нового продукта"""
        async with self.session.begin():  # Ensures proper transaction handling
            product = Product(name=name, info=info, description=description, price=price)
            self.session.add(product)
            await self.session.commit()
            return product

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Получение продукта по ID"""
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_all_products(self) -> List[Product]:
        """Получение списка всех продуктов"""
        result = await self.session.execute(select(Product))
        return result.scalars().all()

    async def update_product(
        self,
        product_id: int,
        name: Optional[str] = None,
        info: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
    ) -> Optional[Product]:
        """Обновление продукта"""
        async with self.session.begin():
            product = await self.get_product_by_id(product_id)
            if product:
                if name is not None:
                    product.name = name
                if info is not None:
                    product.info = info
                if description is not None:
                    product.description = description
                if price is not None:
                    product.price = price
                await self.session.commit()
                return product
        return None

    async def delete_product(self, product_id: int) -> bool:
        """Удаление продукта"""
        async with self.session.begin():
            result = await self.session.execute(
                select(Product).where(Product.id == product_id)
            )
            product = result.scalar_one_or_none()
            if product:
                await self.session.delete(product)
                await self.session.commit()
                return True
        return False
