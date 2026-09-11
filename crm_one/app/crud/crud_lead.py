from typing import Optional, List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.lead import Lead, LeadStatus
from app.models.account import Account
from app.models.contact import Contact
from app.models.deal import Deal, DealStage
from app.schemas.lead import LeadCreate, LeadUpdate


class CRUDLead:
    async def get(self, db: AsyncSession, lead_id: int) -> Optional[Lead]:
        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100, status: Optional[LeadStatus] = None, assigned_to_id: Optional[int] = None
    ) -> List[Lead]:
        query = select(Lead)
        if status is not None:
            query = query.where(Lead.status == status)
        if assigned_to_id is not None:
            query = query.where(Lead.assigned_to_id == assigned_to_id)
        result = await db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: LeadCreate) -> Lead:
        db_obj = Lead(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Lead, obj_in: LeadUpdate) -> Lead:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, lead_id: int) -> Optional[Lead]:
        lead = await self.get(db, lead_id)
        if lead:
            await db.delete(lead)
            await db.flush()
        return lead

    async def convert(self, db: AsyncSession, lead: Lead) -> Tuple[Lead, Account, Contact, Deal]:
        """Convert a qualified lead into Account + Contact + Deal."""
        account_name = lead.company_name if lead.company_name else f"{lead.first_name} {lead.last_name} Household"
        
        # 1. Create Account
        account = Account(
            name=account_name,
            phone=lead.phone,
            owner_id=lead.assigned_to_id
        )
        db.add(account)
        await db.flush()
        await db.refresh(account)

        # 2. Create Contact
        contact = Contact(
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            lead_source=lead.source,
            account_id=account.id,
            owner_id=lead.assigned_to_id
        )
        db.add(contact)
        await db.flush()
        await db.refresh(contact)

        # 3. Create Deal
        deal = Deal(
            title=f"Deal: {lead.title}",
            amount=lead.estimated_value or 0.0,
            stage=DealStage.QUALIFICATION,
            probability=20,
            account_id=account.id,
            contact_id=contact.id,
            owner_id=lead.assigned_to_id
        )
        db.add(deal)
        await db.flush()
        await db.refresh(deal)

        # 4. Mark Lead as Converted
        lead.status = LeadStatus.CONVERTED
        db.add(lead)
        await db.flush()
        await db.refresh(lead)

        return lead, account, contact, deal


crud_lead = CRUDLead()
