import re
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core import security

def validate_username(username: str) -> str:
        # Username constraints
    if " " in username:
        raise ValueError("Username cannot contain spaces")
    if not re.match(r'^[A-Za-z0-9_]+$', username):
        raise ValueError("Username can only contain letters, numbers, and underscores")

def register_user(request: schemas.auth.UserCreate, db: Session):
    # Validate fields
    if not request.username or not request.email or not request.password:
        raise ValueError("All fields are required")
    
    request.username = request.username.lower()
    validate_username(request.username)

    # Check uniqueness
    if crud.user.get_user_by_username(request.username, db):
        raise ValueError("Username already exists")
    if crud.user.get_user_by_email(request.email, db):
        raise ValueError("Email already exists")

    # Hash password
    hashed_password = security.Security.hash_password(request.password)
    request.password = hashed_password

    return crud.user.create(request, db)

def login_user(request: schemas.auth.UserLogin, db: Session):
    if not request.username or not request.password:
        raise ValueError("Username and password are required")
    request.username = request.username.lower()
    user = crud.user.get_user_by_username(request.username, db)

    validate_username(request.username)

    if not user:
        raise ValueError(f"{request.username} does not exist")
    
    if not security.Security.verify_password(request.password, user.password):
        raise ValueError("incorrect password")
    
    return user
