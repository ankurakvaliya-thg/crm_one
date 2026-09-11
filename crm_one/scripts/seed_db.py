import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine, Base
from app.crud.crud_user import crud_user
from app.crud.crud_account import crud_account
from app.crud.crud_contact import crud_contact
from app.crud.crud_lead import crud_lead
from app.crud.crud_deal import crud_deal
from app.crud.crud_task import crud_task
from app.schemas.user import UserCreate
from app.schemas.account import AccountCreate
from app.schemas.contact import ContactCreate
from app.schemas.lead import LeadCreate
from app.schemas.deal import DealCreate
from app.schemas.task import TaskCreate
from app.models.user import UserRole
from app.models.lead import LeadStatus
from app.models.deal import DealStage
from app.models.task import TaskStatus, TaskPriority, TaskType

# Ensure models are imported
import app.models  # noqa


async def seed_data():
    print("Initializing Database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Create Initial Admin User
        admin_user = await crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not admin_user:
            print(f"Creating default superuser: {settings.FIRST_SUPERUSER_EMAIL}")
            admin_user = await crud_user.create(
                db,
                obj_in=UserCreate(
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    full_name="System Administrator",
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    role=UserRole.ADMIN,
                    is_active=True,
                ),
            )
        else:
            print("Superuser already exists.")

        # 2. Create Sales Manager & Rep Users
        manager = await crud_user.get_by_email(db, email="manager@crm.local")
        if not manager:
            manager = await crud_user.create(
                db,
                obj_in=UserCreate(
                    email="manager@crm.local",
                    full_name="Sarah Connor (Sales Manager)",
                    password="ManagerPass123!",
                    role=UserRole.SALES_MANAGER,
                    is_active=True,
                ),
            )

        rep = await crud_user.get_by_email(db, email="agent@crm.local")
        if not rep:
            rep = await crud_user.create(
                db,
                obj_in=UserCreate(
                    email="agent@crm.local",
                    full_name="John Doe (Sales Rep)",
                    password="AgentPass123!",
                    role=UserRole.SALES_REP,
                    is_active=True,
                ),
            )

        # 3. Create Sample Accounts
        acc1 = await crud_account.create(
            db,
            obj_in=AccountCreate(
                name="Acme Corporation",
                industry="Manufacturing & Enterprise Hardware",
                website="https://acmecorp.com",
                phone="+1-555-0199",
                annual_revenue=15000000.0,
                employees_count=450,
                owner_id=rep.id,
            ),
        )

        acc2 = await crud_account.create(
            db,
            obj_in=AccountCreate(
                name="Stark Logistics Inc.",
                industry="Transportation & Logistics",
                website="https://starklogistics.io",
                phone="+1-555-0288",
                annual_revenue=8500000.0,
                employees_count=120,
                owner_id=rep.id,
            ),
        )

        # 4. Create Sample Contacts
        c1 = await crud_contact.create(
            db,
            obj_in=ContactCreate(
                first_name="Alice",
                last_name="Smith",
                email="alice.smith@acmecorp.com",
                phone="+1-555-0101",
                title="VP of Procurement",
                lead_source="Website Form",
                account_id=acc1.id,
                owner_id=rep.id,
            ),
        )

        c2 = await crud_contact.create(
            db,
            obj_in=ContactCreate(
                first_name="Bob",
                last_name="Vance",
                email="bob.vance@starklogistics.io",
                phone="+1-555-0202",
                title="Chief Technology Officer",
                lead_source="LinkedIn Outreach",
                account_id=acc2.id,
                owner_id=rep.id,
            ),
        )

        # 5. Create Sample Leads
        l1 = await crud_lead.create(
            db,
            obj_in=LeadCreate(
                title="Enterprise Cloud Migration",
                company_name="Wayne Enterprises",
                first_name="Bruce",
                last_name="Wayne",
                email="bruce@wayneent.com",
                phone="+1-555-0303",
                source="Referral",
                status=LeadStatus.QUALIFIED,
                estimated_value=250000.0,
                assigned_to_id=rep.id,
            ),
        )

        l2 = await crud_lead.create(
            db,
            obj_in=LeadCreate(
                title="SaaS CRM Subscription 500 Seats",
                company_name="Cyberdyne Systems",
                first_name="Miles",
                last_name="Dyson",
                email="m.dyson@cyberdyne.com",
                phone="+1-555-0404",
                source="Inbound Call",
                status=LeadStatus.NEW,
                estimated_value=75000.0,
                assigned_to_id=rep.id,
            ),
        )

        # 6. Create Sample Deals
        d1 = await crud_deal.create(
            db,
            obj_in=DealCreate(
                title="Acme Hardware Supply Contract",
                amount=120000.0,
                stage=DealStage.PROPOSAL,
                probability=60,
                expected_close_date=datetime.now(timezone.utc) + timedelta(days=30),
                account_id=acc1.id,
                contact_id=c1.id,
                owner_id=rep.id,
            ),
        )

        d2 = await crud_deal.create(
            db,
            obj_in=DealCreate(
                title="Stark Logistics Software Automation",
                amount=85000.0,
                stage=DealStage.CLOSED_WON,
                probability=100,
                expected_close_date=datetime.now(timezone.utc) - timedelta(days=5),
                account_id=acc2.id,
                contact_id=c2.id,
                owner_id=rep.id,
            ),
        )

        # 7. Create Sample Tasks
        t1 = await crud_task.create(
            db,
            obj_in=TaskCreate(
                title="Schedule follow-up demo with Alice",
                description="Review custom integration requirement document.",
                task_type=TaskType.MEETING,
                status=TaskStatus.PENDING,
                priority=TaskPriority.HIGH,
                due_date=datetime.now(timezone.utc) + timedelta(days=2),
                assigned_to_id=rep.id,
                contact_id=c1.id,
                deal_id=d1.id,
            ),
        )

        t2 = await crud_task.create(
            db,
            obj_in=TaskCreate(
                title="Send contract agreement to Bob Vance",
                description="Finalized pricing schedule attached.",
                task_type=TaskType.EMAIL,
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.MEDIUM,
                due_date=datetime.now(timezone.utc) - timedelta(days=1),
                assigned_to_id=rep.id,
                contact_id=c2.id,
                deal_id=d2.id,
            ),
        )

        await db.commit()
        print("Database successfully seeded with initial accounts, leads, deals, tasks, and users!")


if __name__ == "__main__":
    asyncio.run(seed_data())
