from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


class CRUDAccount:
    async def get(self, db: AsyncSession, account_id: int) -> Optional[Account]:
        result = await db.execute(select(Account).where(Account.id == account_id))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100, owner_id: Optional[int] = None) -> List[Account]:
        query = select(Account)
        if owner_id is not None:
            query = query.where(Account.owner_id == owner_id)
        result = await db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: AccountCreate) -> Account:
        db_obj = Account(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Account, obj_in: AccountUpdate) -> Account:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, account_id: int) -> Optional[Account]:
        account = await self.get(db, account_id)
        if account:
            await db.delete(account)
            await db.flush()
        return account


crud_account = CRUDAccount()
