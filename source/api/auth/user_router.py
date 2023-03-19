from fastapi import Body, APIRouter, Depends
from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256

from source.api.schemas.user_schemas import UserSchema, UserLoginSchema
from source.api.auth.auth_handler import sign_jwt
from source.api.services.utils import get_db
from source.db.models import Users

user_router = APIRouter(prefix='/auth/user', tags=['Users'])


@user_router.post('/signup')
def create_user(user: UserSchema = Body(...), db: Session = Depends(get_db)) -> dict:
    prepare_data = user.dict()
    prepare_data['password'] = pbkdf2_sha256.hash(user.password)
    data = insert(Users).values(**prepare_data)
    db.execute(data)
    db.commit()
    return sign_jwt()


@user_router.post('/login')
def user_login(user: UserLoginSchema = Body(...), db: Session = Depends(get_db)) -> dict:
    query = select(Users).filter_by(email=user.email)
    db_data = db.execute(query).scalars().first()
    if db_data and pbkdf2_sha256.verify(user.password, db_data.password):
        return sign_jwt()
    return {
        'error': 'Wrong login details!',
    }
