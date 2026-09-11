from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


class CRUDContact:
    async def get(self, db: AsyncSession, contact_id: int) -> Optional[Contact]:
        result = await db.execute(select(Contact).where(Contact.id == contact_id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, account_id: Optional[int] = None, owner_id: Optional[int] = None
    ) -> List[Contact]:
        query = select(Contact)
        if account_id is not None:
            query = query.where(Contact.account_id == account_id)
        if owner_id is not None:
            query = query.where(Contact.owner_id == owner_id)
        result = await db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: ContactCreate) -> Contact:
        db_obj = Contact(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Contact, obj_in: ContactUpdate) -> Contact:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, contact_id: int) -> Optional[Contact]:
        contact = await self.get(db, contact_id)
        if contact:
            await db.delete(contact)
            await db.flush()
        return contact


crud_contact = CRUDContact()
