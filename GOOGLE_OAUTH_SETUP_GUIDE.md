# Google OAuth Setup Guide for BCM Market Map Generator

## 🎉 Good News: No Setup Required!

Your application uses **Emergent Managed Authentication** which means:
- ✅ No need to create Google OAuth credentials
- ✅ No need to configure OAuth consent screen
- ✅ No API keys to manage
- ✅ Emergent handles all the OAuth complexity

## How It Works

### Authentication Flow:
1. User clicks "Sign in with Google"
2. Redirected to `https://auth.emergentagent.com/`
3. Google OAuth handled by Emergent
4. User redirected back to your app with session
5. Your backend validates the session
6. Only @beebyclarkmeyler.com emails allowed

### Key Features Implemented:
- ✅ **Domain Restriction**: Only @beebyclarkmeyler.com emails can access
- ✅ **User Management**: All users stored in MongoDB
- ✅ **Admin Panel**: First user becomes admin automatically
- ✅ **Session Management**: 7-day secure sessions
- ✅ **Protected Routes**: Market analysis requires login

## User Roles

### Regular Users (@beebyclarkmeyler.com)
- Can login and use the Market Map Generator
- Can generate market analyses
- Can export PDF and Excel reports
- Can view their analysis history

### Admin Users
- All regular user permissions PLUS:
- Can view all users in admin panel
- Can activate/deactivate users
- Can promote users to admin
- Can delete users
- **First user to login automatically becomes admin**

## Admin Panel Access

Once logged in as an admin, access the admin panel at:
- **URL**: `https://your-app-url.com/admin`
- Or click "Admin Panel" in the navigation (only visible to admins)

### Admin Functions:
1. **View All Users** - See everyone who has logged in
2. **Activate/Deactivate** - Control who can access the app
3. **Make Admin** - Promote users to admin status
4. **Delete Users** - Remove users completely

## Testing the Authentication

### Step 1: First User (Becomes Admin)
1. Go to your app URL
2. Click "Sign in with Google"
3. Use your @beebyclarkmeyler.com Google account
4. You'll be logged in as the first admin

### Step 2: Add More Users
1. Share the app URL with other @beebyclarkmeyler.com users
2. They click "Sign in with Google"
3. They'll be able to login and use the app
4. You (as admin) can see them in the admin panel

### Step 3: Manage Users
1. Go to Admin Panel
2. See all users
3. Toggle "Active" status
4. Promote to admin if needed

## Security Features

### Domain Restriction
```python
@validator('email')
def validate_email_domain(cls, v):
    if not v.endswith('@beebyclarkmeyler.com'):
        raise ValueError('Only @beebyclarkmeyler.com email addresses are allowed')
    return v.lower()
```

**What this means:**
- Only emails ending in @beebyclarkmeyler.com can login
- Anyone with a different domain gets rejected
- Error message: "Access restricted to @beebyclarkmeyler.com email addresses only"

### Session Security
- **HttpOnly cookies**: JavaScript cannot access session tokens
- **Secure flag**: Only transmitted over HTTPS
- **SameSite=none**: Works with cross-origin requests
- **7-day expiry**: Automatic logout after 7 days
- **Database validation**: Every request checks session validity

### Protected Endpoints
These endpoints now require authentication:
- `POST /api/analyze-market` - Generate market analysis
- `GET /api/export-pdf/{id}` - Export PDF
- `GET /api/export-market-map/{id}` - Export Excel

Public endpoints (no login required):
- `GET /api/` - Health check
- `GET /api/test-integrations` - Integration status

## What Happens When...

### Non-BCM Email Tries to Login
```
❌ Error: "Access restricted to @beebyclarkmeyler.com email addresses only"
```

### User Account is Deactivated
```
❌ Error: "Your account has been deactivated"
```

### Session Expires (After 7 Days)
```
→ Automatically logged out
→ Redirected to login page
→ Need to sign in again
```

### Non-Authenticated User Tries to Access
```
→ Immediately shown login page
→ Cannot access any protected features
→ Must sign in with @beebyclarkmeyler.com email
```

## Troubleshooting

### "Not authenticated" Error
**Solution**: User needs to login again
- Session expired (7 days old)
- Cookie was cleared
- Different browser/device

### "Access restricted" Error
**Solution**: User is not using @beebyclarkmeyler.com email
- Must use company Google account
- Personal Gmail won't work
- Contact admin if issue persists

### "Account is inactive" Error
**Solution**: Admin deactivated the account
- Contact administrator
- Admin can reactivate in admin panel

## Architecture

### Backend (FastAPI)
```
/app/backend/
├── server.py           # Main app with protected routes
├── auth_routes.py      # Authentication endpoints
├── auth_models.py      # User and Session models
└── .env               # Contains TOGETHER_API_KEY, etc.
```

### Frontend (React)
```
/app/frontend/src/
├── App.js             # Main app with auth logic
├── components/
│   ├── Login.js       # Login page
│   └── AdminPanel.js  # Admin user management
```

### Database (MongoDB)
```
Collections:
- users         # User accounts
- sessions      # Active sessions
- market_inputs # Market analysis inputs
- market_maps   # Generated market maps
```

## API Endpoints

### Public Endpoints
```
GET  /api/                    # Health check
GET  /api/test-integrations   # Integration status
```

### Authentication Endpoints
```
POST /api/auth/session        # Create session after OAuth
GET  /api/auth/me            # Get current user
POST /api/auth/logout         # Logout
```

### Protected Endpoints (Require Login)
```
POST /api/analyze-market      # Generate market analysis
GET  /api/export-pdf/{id}     # Export PDF
GET  /api/export-market-map/{id} # Export Excel
GET  /api/analysis-history    # View history
```

### Admin Endpoints (Require Admin Role)
```
GET    /api/admin/users         # List all users
PATCH  /api/admin/users/{id}    # Update user status
DELETE /api/admin/users/{id}    # Delete user
```

## Summary

✅ **No OAuth setup needed** - Emergent handles everything  
✅ **Domain restricted** - Only @beebyclarkmeyler.com  
✅ **First user is admin** - Automatic admin assignment  
✅ **Secure sessions** - 7-day httpOnly cookies  
✅ **Admin panel** - Full user management  
✅ **Protected routes** - Authentication required  

**Ready to use immediately - no configuration required!** 🎉

---

**Need Help?**
- All users are stored in MongoDB `users` collection
- All sessions in MongoDB `sessions` collection
- Check backend logs: `/var/log/supervisor/backend.err.log`
- Frontend auth state managed in React context
