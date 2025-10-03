"""
Authentication Routes for BCM Market Map Generator
Handles Google OAuth via Emergent Auth, user management, and admin functions
"""

from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
import httpx
import logging
from datetime import datetime, timezone
from typing import Optional, List
from auth_models import User, Session, SessionData, UserResponse, AdminUserUpdate

logger = logging.getLogger(__name__)

auth_router = APIRouter()


# Dependency to get database
async def get_db(request: Request):
    return request.app.state.db


# Dependency to get current user from session
async def get_current_user(request: Request, db = Depends(get_db)) -> Optional[User]:
    """Get current user from session token (cookie or header)"""
    # Try to get session token from cookie first
    session_token = request.cookies.get('session_token')
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header.replace('Bearer ', '')
    
    if not session_token:
        return None
    
    # Check if session exists and is valid
    session = await db.sessions.find_one({
        "session_token": session_token,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not session:
        return None
    
    # Get user
    user_data = await db.users.find_one({"id": session["user_id"]})
    if not user_data:
        return None
    
    return User(**user_data)


# Dependency to require authentication
async def require_auth(user: Optional[User] = Depends(get_current_user)) -> User:
    """Require user to be authenticated"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    return user


# Dependency to require admin privileges
async def require_admin(user: User = Depends(require_auth)) -> User:
    """Require user to be an admin"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return user


@auth_router.post("/auth/session")
async def create_session(request: Request, response: Response, db = Depends(get_db)):
    """
    Process session_id from Emergent Auth and create user session
    Called by frontend after Google OAuth redirect
    """
    try:
        # Get session_id from header
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            raise HTTPException(status_code=400, detail="X-Session-ID header required")
        
        # Call Emergent Auth to get session data (correct endpoint from playbook)
        async with httpx.AsyncClient() as client:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            
            logger.info(f"Emergent Auth response status: {auth_response.status_code}")
            if auth_response.status_code != 200:
                logger.error(f"Emergent Auth error: {auth_response.text}")
            
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session ID")
            
            session_data = SessionData(**auth_response.json())
        
        # Validate email domain
        if not session_data.email.endswith('@beebyclarkmeyler.com'):
            raise HTTPException(
                status_code=403, 
                detail="Access restricted to @beebyclarkmeyler.com email addresses only"
            )
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": session_data.email.lower()})
        
        if existing_user:
            # Update last login
            user = User(**existing_user)
            await db.users.update_one(
                {"id": user.id},
                {"$set": {"last_login": datetime.now(timezone.utc)}}
            )
        else:
            # Create new user (first user becomes admin)
            user_count = await db.users.count_documents({})
            is_first_user = user_count == 0
            
            user = User(
                email=session_data.email.lower(),
                name=session_data.name,
                picture=session_data.picture,
                is_admin=is_first_user,  # First user is admin
                last_login=datetime.now(timezone.utc)
            )
            
            await db.users.insert_one(user.dict())
            logger.info(f"New user created: {user.email} (admin: {is_first_user})")
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Your account has been deactivated")
        
        # Create session in database
        session = Session(
            user_id=user.id,
            session_token=session_data.session_token,
            expires_at=Session.create_expiry()
        )
        
        await db.sessions.insert_one(session.dict())
        
        # Set httpOnly cookie
        response.set_cookie(
            key="session_token",
            value=session_data.session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7 * 24 * 60 * 60,  # 7 days
            path="/"
        )
        
        return {
            "user": UserResponse(**user.dict()).dict(),
            "message": "Authentication successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.get("/auth/me")
async def get_current_user_info(user: User = Depends(require_auth)):
    """Get current authenticated user information"""
    return UserResponse(**user.dict())


@auth_router.post("/auth/logout")
async def logout(request: Request, response: Response, db = Depends(get_db)):
    """Logout user and delete session"""
    try:
        session_token = request.cookies.get('session_token')
        
        if session_token:
            # Delete session from database
            await db.sessions.delete_one({"session_token": session_token})
        
        # Clear cookie
        response.delete_cookie(key="session_token", path="/")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Error logging out: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Admin endpoints
@auth_router.get("/admin/users")
async def list_users(
    user: User = Depends(require_admin),
    db = Depends(get_db)
) -> List[UserResponse]:
    """List all users (admin only)"""
    try:
        users = await db.users.find().to_list(length=100)
        return [UserResponse(**u) for u in users]
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.patch("/admin/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: AdminUserUpdate,
    admin: User = Depends(require_admin),
    db = Depends(get_db)
):
    """Update user status (admin only)"""
    try:
        # Don't allow admin to deactivate themselves
        if user_id == admin.id and update_data.is_active is False:
            raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
        
        # Build update dict
        update_dict = {}
        if update_data.is_active is not None:
            update_dict["is_active"] = update_data.is_active
        if update_data.is_admin is not None:
            update_dict["is_admin"] = update_data.is_admin
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        # Update user
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get updated user
        updated_user = await db.users.find_one({"id": user_id})
        return UserResponse(**updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db = Depends(get_db)
):
    """Delete user (admin only)"""
    try:
        # Don't allow admin to delete themselves
        if user_id == admin.id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        # Delete user
        result = await db.users.delete_one({"id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user's sessions
        await db.sessions.delete_many({"user_id": user_id})
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))