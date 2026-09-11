import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User, UserRole
from app.crud.crud_user import crud_user
from app.schemas.user import UserCreate

# In-memory SQLite engine for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh database session for each test function."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP AsyncClient connected to the FastAPI application with test database override."""
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession) -> User:
    """Create a default admin user for tests."""
    user_in = UserCreate(
        email="admin@test.com",
        full_name="Test Admin",
        password="TestPassword123!",
        role=UserRole.ADMIN,
        is_active=True
    )
    return await crud_user.create(db_session, obj_in=user_in)


@pytest_asyncio.fixture(scope="function")
async def admin_headers(client: AsyncClient, admin_user: User) -> dict:
    """Obtain authorization headers for admin user."""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": admin_user.email, "password": "TestPassword123!"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
