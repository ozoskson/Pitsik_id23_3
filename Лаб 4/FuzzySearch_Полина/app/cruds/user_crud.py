from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User  # модель пользователя
from schemas.auth import SignUpRequest  # схема входящих данных при регистрации


def find_user_by_email(db: Session, email: str) -> User:
    """
    Возвращает пользователя по email, если он существует.
    """
    return db.query(User).filter(User.email == email).first()


def create_new_user(db: Session, user_in: SignUpRequest) -> User:
    """
    Создаёт нового пользователя. Пароль хешируется перед сохранением в БД.
    """
    hashed_password = generate_password_hash(user_in.password)
    user = User(email=user_in.email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def is_user_exists(db: Session, email: str) -> bool:
    return bool(find_user_by_email(db, email))

def validate_accsess(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not check_password_hash(user.password, password):
        return None
    return user

def get_user_access(db: Session, user_in: SignUpRequest) -> bool:
    user = validate_accsess(db, user_in.email, user_in.password)
    return user if user else False