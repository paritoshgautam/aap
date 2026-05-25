from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import User, UserRole


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        return result.scalar_one_or_none()

    async def count_admins(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.role == UserRole.admin)
        )
        return int(result.scalar_one())
