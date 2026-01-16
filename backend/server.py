from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import resend
from bson import ObjectId
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable must be set")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Resend Configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Create the main app
app = FastAPI(title="Wolmer's Transcript Tracker API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Upload directory
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ==================== MODELS ====================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "student"  # student, staff, admin

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TranscriptRequestCreate(BaseModel):
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str
    school_id: str
    enrollment_status: str  # enrolled, graduate, withdrawn
    academic_year: str
    wolmers_email: str
    personal_email: EmailStr
    phone_number: str
    reason: str
    needed_by_date: str
    collection_method: str  # pickup, emailed, delivery
    institution_name: Optional[str] = ""
    institution_address: Optional[str] = ""
    institution_phone: Optional[str] = ""
    institution_email: Optional[str] = ""

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class TranscriptRequestUpdate(BaseModel):
    status: Optional[str] = None
    assigned_staff_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    staff_notes: Optional[str] = None

class TranscriptRequestResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    student_email: str
    first_name: str
    middle_name: str
    last_name: str
    school_id: str
    enrollment_status: str
    academic_year: str
    wolmers_email: str
    personal_email: str
    phone_number: str
    reason: str
    needed_by_date: str
    collection_method: str
    institution_name: str = ""
    institution_address: str
    institution_phone: str
    institution_email: str
    status: str
    assigned_staff_id: Optional[str] = None
    assigned_staff_name: Optional[str] = None
    rejection_reason: Optional[str] = None
    staff_notes: Optional[str] = None
    documents: List[dict] = []
    timeline: List[dict] = []
    created_at: str
    updated_at: str

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    read: bool
    request_id: Optional[str] = None
    created_at: str

class StaffCreateByAdmin(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str  # staff or admin

class AnalyticsResponse(BaseModel):
    total_requests: int
    pending_requests: int
    in_progress_requests: int
    processing_requests: int
    ready_requests: int
    completed_requests: int
    rejected_requests: int
    requests_by_month: List[dict]
    requests_by_enrollment: List[dict]
    requests_by_collection_method: List[dict]

# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def require_role(roles: List[str]):
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

async def send_email_notification(to_email: str, subject: str, html_content: str):
    if not RESEND_API_KEY:
        logger.warning("Resend API key not configured, skipping email")
        return None
    try:
        params = {
            "from": SENDER_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return None

async def create_notification(user_id: str, title: str, message: str, notif_type: str, request_id: str = None):
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": notif_type,
        "read": False,
        "request_id": request_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    return notification

async def notify_status_change(request_data: dict, old_status: str, new_status: str):
    student = await db.users.find_one({"id": request_data["student_id"]}, {"_id": 0})
    if not student:
        return
    
    title = f"Request Status Updated"
    message = f"Your transcript request has been updated from '{old_status}' to '{new_status}'."
    
    # Create in-app notification
    await create_notification(student["id"], title, message, "status_update", request_data["id"])
    
    # Send email notification
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #800000; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">Wolmer's Boys' School</h1>
            <p style="margin: 5px 0;">Transcript Tracker</p>
        </div>
        <div style="padding: 20px; background-color: #f5f5f5;">
            <h2 style="color: #800000;">Request Status Update</h2>
            <p>Dear {student['full_name']},</p>
            <p>Your transcript request status has been updated:</p>
            <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>Previous Status:</strong> {old_status}</p>
                <p><strong>New Status:</strong> <span style="color: #800000; font-weight: bold;">{new_status}</span></p>
            </div>
            <p>Log in to view more details about your request.</p>
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                This is an automated message from Wolmer's Boys' School Transcript Tracker.
            </p>
        </div>
    </div>
    """
    await send_email_notification(student["email"], f"Transcript Request: {new_status}", html_content)

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if email already exists
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Only students can self-register
    if user_data.role != "student":
        raise HTTPException(status_code=400, detail="Only students can self-register")
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "password_hash": hash_password(user_data.password),
        "role": "student",
        "created_at": now,
        "updated_at": now
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id, user_data.email, "student")
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            role="student",
            created_at=now
        )
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user["id"], user["email"], user["role"])
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            created_at=user["created_at"]
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        created_at=user["created_at"]
    )

# ==================== PASSWORD RESET ====================

@api_router.post("/auth/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    user = await db.users.find_one({"email": request.email}, {"_id": 0})
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If an account with this email exists, a password reset link has been sent."}
    
    # Generate reset token (valid for 1 hour)
    reset_token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    # Store reset token in database
    await db.password_resets.delete_many({"email": request.email})  # Remove old tokens
    await db.password_resets.insert_one({
        "token": reset_token,
        "email": request.email,
        "user_id": user["id"],
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    # Send email with reset link
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #800000; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">Wolmer's Boys' School</h1>
            <p style="margin: 5px 0;">Transcript Tracker</p>
        </div>
        <div style="padding: 20px; background-color: #f5f5f5;">
            <h2 style="color: #800000;">Password Reset Request</h2>
            <p>Dear {user['full_name']},</p>
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="background-color: #800000; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
            </div>
            <p style="color: #666; font-size: 14px;">This link will expire in 1 hour.</p>
            <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                This is an automated message from Wolmer's Boys' School Transcript Tracker.
            </p>
        </div>
    </div>
    """
    await send_email_notification(request.email, "Password Reset Request", html_content)
    
    # For development: log the token
    logger.info(f"Password reset token for {request.email}: {reset_token}")
    
    return {"message": "If an account with this email exists, a password reset link has been sent.", "token": reset_token}

@api_router.post("/auth/reset-password")
async def reset_password(request: PasswordResetConfirm):
    # Find the reset token
    reset_record = await db.password_resets.find_one({"token": request.token}, {"_id": 0})
    
    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Check if token is expired
    expires_at = datetime.fromisoformat(reset_record["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        await db.password_resets.delete_one({"token": request.token})
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Update user's password
    new_password_hash = hash_password(request.new_password)
    await db.users.update_one(
        {"id": reset_record["user_id"]},
        {"$set": {"password_hash": new_password_hash, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Delete the used token
    await db.password_resets.delete_one({"token": request.token})
    
    return {"message": "Password has been reset successfully"}

@api_router.get("/auth/verify-reset-token/{token}")
async def verify_reset_token(token: str):
    reset_record = await db.password_resets.find_one({"token": token}, {"_id": 0})
    
    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    expires_at = datetime.fromisoformat(reset_record["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        await db.password_resets.delete_one({"token": token})
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    return {"valid": True, "email": reset_record["email"]}

# ==================== USER MANAGEMENT (ADMIN) ====================

@api_router.post("/admin/users", response_model=UserResponse)
async def create_user_by_admin(user_data: StaffCreateByAdmin, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "password_hash": hash_password(user_data.password),
        "role": user_data.role,
        "created_at": now,
        "updated_at": now
    }
    
    await db.users.insert_one(user_doc)
    
    return UserResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        created_at=now
    )

@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all users")
    
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return [UserResponse(**u) for u in users]

@api_router.get("/admin/staff", response_model=List[UserResponse])
async def get_staff_members(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    staff = await db.users.find({"role": "staff"}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return [UserResponse(**s) for s in staff]

@api_router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

class AdminResetPassword(BaseModel):
    new_password: str

@api_router.post("/admin/users/{user_id}/reset-password")
async def admin_reset_user_password(user_id: str, data: AdminResetPassword, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can reset passwords")
    
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot reset your own password this way. Use the forgot password feature.")
    
    # Find the user
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    new_password_hash = hash_password(data.new_password)
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"password_hash": new_password_hash, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Send notification email to user
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #800000; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">Wolmer's Boys' School</h1>
            <p style="margin: 5px 0;">Transcript Tracker</p>
        </div>
        <div style="padding: 20px; background-color: #f5f5f5;">
            <h2 style="color: #800000;">Password Reset by Administrator</h2>
            <p>Dear {user['full_name']},</p>
            <p>Your password has been reset by an administrator.</p>
            <p>If you did not request this change, please contact the administrator immediately.</p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                This is an automated message from Wolmer's Boys' School Transcript Tracker.
            </p>
        </div>
    </div>
    """
    await send_email_notification(user["email"], "Your Password Has Been Reset", html_content)
    
    return {"message": f"Password reset successfully for {user['full_name']}"}

# ==================== TRANSCRIPT REQUESTS ====================

@api_router.post("/requests", response_model=TranscriptRequestResponse)
async def create_transcript_request(request_data: TranscriptRequestCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can create transcript requests")
    
    request_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    timeline_entry = {
        "status": "Pending",
        "timestamp": now,
        "note": "Request submitted",
        "updated_by": current_user["full_name"]
    }
    
    doc = {
        "id": request_id,
        "student_id": current_user["id"],
        "student_name": current_user["full_name"],
        "student_email": current_user["email"],
        "first_name": request_data.first_name,
        "middle_name": request_data.middle_name or "",
        "last_name": request_data.last_name,
        "school_id": request_data.school_id,
        "enrollment_status": request_data.enrollment_status,
        "academic_year": request_data.academic_year,
        "wolmers_email": request_data.wolmers_email,
        "personal_email": request_data.personal_email,
        "phone_number": request_data.phone_number,
        "reason": request_data.reason,
        "needed_by_date": request_data.needed_by_date,
        "collection_method": request_data.collection_method,
        "institution_name": request_data.institution_name or "",
        "institution_address": request_data.institution_address or "",
        "institution_phone": request_data.institution_phone or "",
        "institution_email": request_data.institution_email or "",
        "status": "Pending",
        "assigned_staff_id": None,
        "assigned_staff_name": None,
        "rejection_reason": None,
        "staff_notes": None,
        "documents": [],
        "timeline": [timeline_entry],
        "created_at": now,
        "updated_at": now
    }
    
    await db.transcript_requests.insert_one(doc)
    
    # Notify admins
    admins = await db.users.find({"role": "admin"}, {"_id": 0}).to_list(100)
    for admin in admins:
        await create_notification(
            admin["id"],
            "New Transcript Request",
            f"New request from {current_user['full_name']}",
            "new_request",
            request_id
        )
    
    return TranscriptRequestResponse(**doc)

@api_router.get("/requests", response_model=List[TranscriptRequestResponse])
async def get_requests(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "student":
        # Students can only see their own requests
        requests = await db.transcript_requests.find(
            {"student_id": current_user["id"]},
            {"_id": 0}
        ).sort("created_at", -1).to_list(1000)
    elif current_user["role"] == "staff":
        # Staff can see assigned requests
        requests = await db.transcript_requests.find(
            {"assigned_staff_id": current_user["id"]},
            {"_id": 0}
        ).sort("created_at", -1).to_list(1000)
    else:
        # Admin can see all requests
        requests = await db.transcript_requests.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    return [TranscriptRequestResponse(**r) for r in requests]

@api_router.get("/requests/all", response_model=List[TranscriptRequestResponse])
async def get_all_requests(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    requests = await db.transcript_requests.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [TranscriptRequestResponse(**r) for r in requests]

@api_router.get("/requests/{request_id}", response_model=TranscriptRequestResponse)
async def get_request(request_id: str, current_user: dict = Depends(get_current_user)):
    request_doc = await db.transcript_requests.find_one({"id": request_id}, {"_id": 0})
    if not request_doc:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check permissions
    if current_user["role"] == "student" and request_doc["student_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only view your own requests")
    
    return TranscriptRequestResponse(**request_doc)

class StudentRequestUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    school_id: Optional[str] = None
    enrollment_status: Optional[str] = None
    academic_year: Optional[str] = None
    wolmers_email: Optional[str] = None
    personal_email: Optional[str] = None
    phone_number: Optional[str] = None
    reason: Optional[str] = None
    needed_by_date: Optional[str] = None
    collection_method: Optional[str] = None
    institution_name: Optional[str] = None
    institution_address: Optional[str] = None
    institution_phone: Optional[str] = None
    institution_email: Optional[str] = None

@api_router.put("/requests/{request_id}/edit", response_model=TranscriptRequestResponse)
async def student_edit_request(request_id: str, update_data: StudentRequestUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can edit their own requests")
    
    request_doc = await db.transcript_requests.find_one({"id": request_id}, {"_id": 0})
    if not request_doc:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check ownership
    if request_doc["student_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only edit your own requests")
    
    # Check status - only pending requests can be edited
    if request_doc["status"] != "Pending":
        raise HTTPException(
            status_code=400, 
            detail=f"This request cannot be edited because its status is '{request_doc['status']}'. Only pending requests can be modified."
        )
    
    now = datetime.now(timezone.utc).isoformat()
    updates = {"updated_at": now}
    
    # Update only provided fields
    update_fields = update_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        if value is not None:
            updates[field] = value
    
    # Add timeline entry for edit
    timeline_entry = {
        "status": "Pending",
        "timestamp": now,
        "note": "Request details updated by student",
        "updated_by": current_user["full_name"]
    }
    
    await db.transcript_requests.update_one(
        {"id": request_id},
        {
            "$set": updates,
            "$push": {"timeline": timeline_entry}
        }
    )
    
    updated_request = await db.transcript_requests.find_one({"id": request_id}, {"_id": 0})
    return TranscriptRequestResponse(**updated_request)

@api_router.patch("/requests/{request_id}", response_model=TranscriptRequestResponse)
async def update_request(request_id: str, update_data: TranscriptRequestUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "student":
        raise HTTPException(status_code=403, detail="Students cannot update request status")
    
    request_doc = await db.transcript_requests.find_one({"id": request_id}, {"_id": 0})
    if not request_doc:
        raise HTTPException(status_code=404, detail="Request not found")
    
    now = datetime.now(timezone.utc).isoformat()
    updates = {"updated_at": now}
    
    old_status = request_doc["status"]
    
    if update_data.status:
        updates["status"] = update_data.status
        timeline_entry = {
            "status": update_data.status,
            "timestamp": now,
            "note": f"Status changed to {update_data.status}",
            "updated_by": current_user["full_name"]
        }
        await db.transcript_requests.update_one(
            {"id": request_id},
            {"$push": {"timeline": timeline_entry}}
        )
    
    if update_data.assigned_staff_id:
        staff = await db.users.find_one({"id": update_data.assigned_staff_id}, {"_id": 0})
        if staff:
            updates["assigned_staff_id"] = update_data.assigned_staff_id
            updates["assigned_staff_name"] = staff["full_name"]
            # Notify staff
            await create_notification(
                staff["id"],
                "New Assignment",
                f"You have been assigned a transcript request",
                "assignment",
                request_id
            )
    
    if update_data.rejection_reason:
        updates["rejection_reason"] = update_data.rejection_reason
        updates["status"] = "Rejected"
        timeline_entry = {
            "status": "Rejected",
            "timestamp": now,
            "note": f"Request rejected: {update_data.rejection_reason}",
            "updated_by": current_user["full_name"]
        }
        await db.transcript_requests.update_one(
            {"id": request_id},
            {"$push": {"timeline": timeline_entry}}
        )
    
    if update_data.staff_notes:
        updates["staff_notes"] = update_data.staff_notes
    
    await db.transcript_requests.update_one({"id": request_id}, {"$set": updates})
    
    # Notify student of status change
    if update_data.status and update_data.status != old_status:
        updated_doc = await db.transcript_requests.find_one({"id": request_id}, {"_id": 0})
        await notify_status_change(updated_doc, old_status, update_data.status)
    
    updated_request = await db.transcript_requests.find_one({"id": request_id}, {"_id": 0})
    return TranscriptRequestResponse(**updated_request)

# ==================== FILE UPLOAD ====================

@api_router.post("/requests/{request_id}/documents")
async def upload_document(request_id: str, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Only staff and admin can upload documents")
    
    request_doc = await db.transcript_requests.find_one({"id": request_id}, {"_id": 0})
    if not request_doc:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
        "image/gif"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Save file
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    file_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    now = datetime.now(timezone.utc).isoformat()
    doc_entry = {
        "id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "path": str(file_path),
        "uploaded_by": current_user["full_name"],
        "uploaded_at": now
    }
    
    await db.transcript_requests.update_one(
        {"id": request_id},
        {
            "$push": {"documents": doc_entry},
            "$set": {"updated_at": now}
        }
    )
    
    # Add timeline entry
    timeline_entry = {
        "status": request_doc["status"],
        "timestamp": now,
        "note": f"Document uploaded: {file.filename}",
        "updated_by": current_user["full_name"]
    }
    await db.transcript_requests.update_one(
        {"id": request_id},
        {"$push": {"timeline": timeline_entry}}
    )
    
    # Notify student
    await create_notification(
        request_doc["student_id"],
        "Document Uploaded",
        f"A document has been uploaded to your transcript request",
        "document",
        request_id
    )
    
    return {"message": "Document uploaded successfully", "document": doc_entry}

@api_router.get("/documents/{document_id}")
async def get_document(document_id: str, current_user: dict = Depends(get_current_user)):
    # Find the request containing this document
    request_doc = await db.transcript_requests.find_one(
        {"documents.id": document_id},
        {"_id": 0}
    )
    
    if not request_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    if current_user["role"] == "student" and request_doc["student_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Find the document
    doc = next((d for d in request_doc["documents"] if d["id"] == document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = Path(doc["path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode('utf-8')
    
    return {
        "filename": doc["filename"],
        "content_type": doc["content_type"],
        "content": content
    }

# ==================== NOTIFICATIONS ====================

@api_router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await db.notifications.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return [NotificationResponse(**n) for n in notifications]

@api_router.get("/notifications/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    count = await db.notifications.count_documents({
        "user_id": current_user["id"],
        "read": False
    })
    return {"count": count}

@api_router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@api_router.patch("/notifications/read-all")
async def mark_all_notifications_read(current_user: dict = Depends(get_current_user)):
    await db.notifications.update_many(
        {"user_id": current_user["id"], "read": False},
        {"$set": {"read": True}}
    )
    return {"message": "All notifications marked as read"}

# ==================== ANALYTICS ====================

@api_router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view analytics")
    
    # Use aggregation pipeline for optimized queries
    pipeline = [
        {
            "$facet": {
                "status_counts": [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                ],
                "enrollment_counts": [
                    {"$group": {"_id": "$enrollment_status", "count": {"$sum": 1}}}
                ],
                "collection_counts": [
                    {"$group": {"_id": "$collection_method", "count": {"$sum": 1}}}
                ],
                "total": [
                    {"$count": "count"}
                ]
            }
        }
    ]
    
    result = await db.transcript_requests.aggregate(pipeline).to_list(1)
    
    # Parse aggregation results
    if result:
        data = result[0]
        
        # Get total
        total = data["total"][0]["count"] if data["total"] else 0
        
        # Parse status counts
        status_map = {item["_id"]: item["count"] for item in data["status_counts"]}
        pending = status_map.get("Pending", 0)
        in_progress = status_map.get("In Progress", 0)
        processing = status_map.get("Processing", 0)
        ready = status_map.get("Ready", 0)
        completed = status_map.get("Completed", 0)
        rejected = status_map.get("Rejected", 0)
        
        # Parse enrollment counts
        enrollment_map = {item["_id"]: item["count"] for item in data["enrollment_counts"]}
        requests_by_enrollment = [
            {"name": "Enrolled", "value": enrollment_map.get("enrolled", 0)},
            {"name": "Graduate", "value": enrollment_map.get("graduate", 0)},
            {"name": "Withdrawn", "value": enrollment_map.get("withdrawn", 0)}
        ]
        
        # Parse collection method counts
        collection_map = {item["_id"]: item["count"] for item in data["collection_counts"]}
        requests_by_collection_method = [
            {"name": "Pickup at Bursary", "value": collection_map.get("pickup", 0)},
            {"name": "Emailed to Institution", "value": collection_map.get("emailed", 0)},
            {"name": "Physical Delivery", "value": collection_map.get("delivery", 0)}
        ]
    else:
        total = pending = in_progress = processing = ready = completed = rejected = 0
        requests_by_enrollment = [
            {"name": "Enrolled", "value": 0},
            {"name": "Graduate", "value": 0},
            {"name": "Withdrawn", "value": 0}
        ]
        requests_by_collection_method = [
            {"name": "Pickup at Bursary", "value": 0},
            {"name": "Emailed to Institution", "value": 0},
            {"name": "Physical Delivery", "value": 0}
        ]
    
    # Requests by month (last 6 months) - using aggregation
    now = datetime.now(timezone.utc)
    requests_by_month = []
    
    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        count = await db.transcript_requests.count_documents({
            "created_at": {
                "$gte": month_start.isoformat(),
                "$lt": month_end.isoformat()
            }
        })
        requests_by_month.append({
            "month": month_start.strftime("%b %Y"),
            "count": count
        })
    
    return AnalyticsResponse(
        total_requests=total,
        pending_requests=pending,
        in_progress_requests=in_progress,
        processing_requests=processing,
        ready_requests=ready,
        completed_requests=completed,
        rejected_requests=rejected,
        requests_by_month=requests_by_month,
        requests_by_enrollment=requests_by_enrollment,
        requests_by_collection_method=requests_by_collection_method
    )

# ==================== HEALTH CHECK ====================

@api_router.get("/")
async def root():
    return {"message": "Wolmer's Transcript Tracker API", "status": "running"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# ==================== SEED DEFAULT ADMIN ====================

@app.on_event("startup")
async def seed_default_admin():
    admin_email = "admin@wolmers.org"
    existing = await db.users.find_one({"email": admin_email}, {"_id": 0})
    
    if not existing:
        admin_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        admin_doc = {
            "id": admin_id,
            "email": admin_email,
            "full_name": "System Administrator",
            "password_hash": hash_password("Admin123!"),
            "role": "admin",
            "created_at": now,
            "updated_at": now
        }
        
        await db.users.insert_one(admin_doc)
        logger.info("Default admin account created: admin@wolmers.org / Admin123!")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
