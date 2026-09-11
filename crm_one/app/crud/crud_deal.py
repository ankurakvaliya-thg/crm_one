from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deal import Deal, DealStage
from app.schemas.deal import DealCreate, DealUpdate


class CRUDDeal:
    async def get(self, db: AsyncSession, deal_id: int) -> Optional[Deal]:
        result = await db.execute(select(Deal).where(Deal.id == deal_id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, stage: Optional[DealStage] = None, owner_id: Optional[int] = None
    ) -> List[Deal]:
        query = select(Deal)
        if stage is not None:
            query = query.where(Deal.stage == stage)
        if owner_id is not None:
            query = query.where(Deal.owner_id == owner_id)
        result = await db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: DealCreate) -> Deal:
        db_obj = Deal(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Deal, obj_in: DealUpdate) -> Deal:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, deal_id: int) -> Optional[Deal]:
        deal = await self.get(db, deal_id)
        if deal:
            await db.delete(deal)
            await db.flush()
        return deal


crud_deal = CRUDDeal()
