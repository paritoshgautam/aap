from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.core.security import create_access_token, hash_password, verify_password
from app.models.student import User, UserRole
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/bootstrap-admin", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def bootstrap_admin(payload: UserCreate, session: SessionDep) -> TokenResponse:
    repository = UserRepository(session)
    if await repository.count_admins() > 0:
        raise HTTPException(status_code=409, detail="An admin user already exists")
    if await repository.get_by_email(payload.email):
        raise HTTPException(status_code=409, detail="A user with this email already exists")

    user = await repository.create_user(
        User(
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            role=UserRole.admin,
            full_name=payload.full_name,
        )
    )
    await session.commit()
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: SessionDep) -> TokenResponse:
    user = await UserRepository(session).get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _token_response(user)


def _token_response(user: User) -> TokenResponse:
    token = create_access_token(str(user.id), {"role": user.role, "email": user.email})
    return TokenResponse(
        access_token=token,
        user=UserRead(id=user.id, email=user.email, role=user.role, full_name=user.full_name),
    )
