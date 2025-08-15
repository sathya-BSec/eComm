from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
from typing import Optional

from database import get_db
import models
import schemas
from auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from services.otp_service import otp_service
from services.social_auth import social_auth_service

router = APIRouter()

# Additional Pydantic models for OTP and social auth
class OTPRequest(BaseModel):
    contact: str  # email or phone
    method: str   # "email" or "sms"

class OTPVerify(BaseModel):
    contact: str
    method: str
    otp: str

class SocialAuthRequest(BaseModel):
    provider: str  # "google", "facebook", "instagram", "apple"
    token: str

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token."""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """Get current user info."""
    return current_user

@router.post("/send-otp")
async def send_otp(otp_request: OTPRequest):
    """Send OTP to email or phone."""
    try:
        otp = otp_service.send_otp(otp_request.contact, otp_request.method)
        if otp:
            return {"message": f"OTP sent to {otp_request.contact}", "success": True}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send OTP"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending OTP: {str(e)}"
        )

@router.post("/verify-otp", response_model=schemas.Token)
def verify_otp_login(otp_verify: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and log in user."""
    # Verify OTP
    if not otp_service.verify_contact_otp(otp_verify.contact, otp_verify.method, otp_verify.otp):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )
    
    # Find or create user
    if otp_verify.method == "email":
        user = db.query(models.User).filter(models.User.email == otp_verify.contact).first()
        if not user:
            # Create new user with email
            user = models.User(
                email=otp_verify.contact,
                username=otp_verify.contact.split('@')[0],  # Use email prefix as username
                hashed_password=get_password_hash("temp_password"),  # Temporary password
                first_name="",
                last_name=""
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    else:  # SMS/phone
        # For phone authentication, we'd need to add a phone field to the User model
        # For now, create with phone as username
        user = db.query(models.User).filter(models.User.username == otp_verify.contact).first()
        if not user:
            user = models.User(
                email=f"{otp_verify.contact}@phone.temp",  # Temporary email
                username=otp_verify.contact,
                hashed_password=get_password_hash("temp_password"),
                first_name="",
                last_name=""
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/social-auth", response_model=schemas.Token)
async def social_authentication(social_request: SocialAuthRequest, db: Session = Depends(get_db)):
    """Authenticate user with social provider."""
    try:
        # Verify token with social provider
        user_info = await social_auth_service.authenticate_social_user(
            social_request.provider, 
            social_request.token
        )
        
        if not user_info:
            raise HTTPException(
                status_code=400,
                detail="Invalid social authentication token"
            )
        
        # Find or create user
        email = user_info.get("email")
        provider_id = user_info.get("provider_id")
        
        if email:
            user = db.query(models.User).filter(models.User.email == email).first()
        else:
            # For providers that don't give email (like Instagram), use provider_id
            username = f"{social_request.provider}_{provider_id}"
            user = db.query(models.User).filter(models.User.username == username).first()
        
        if not user:
            # Create new user
            username = email.split('@')[0] if email else f"{social_request.provider}_{provider_id}"
            user = models.User(
                email=email or f"{username}@{social_request.provider}.temp",
                username=username,
                hashed_password=get_password_hash("social_auth"),  # Social users don't need password
                first_name=user_info.get("given_name", ""),
                last_name=user_info.get("family_name", "")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Social authentication failed: {str(e)}"
        )