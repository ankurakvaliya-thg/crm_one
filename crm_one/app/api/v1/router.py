from fastapi import APIRouter
from app.api.v1 import auth, users, accounts, contacts, leads, deals, tasks, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users & Access Control"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Accounts (Companies)"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads & Conversion"])
api_router.include_router(deals.router, prefix="/deals", tags=["Deals & Sales Pipeline"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks & Activities"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["CRM Analytics & Reports"])
