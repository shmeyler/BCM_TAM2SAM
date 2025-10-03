# OAuth Testing and Troubleshooting Guide

## Issue Fixed: Emergent Auth Endpoint

**Problem:** The auth endpoint URL was incorrect
**Fix:** Changed from `/auth/v1/env/oauth/session-data` to `/auth/v1/oauth/session-data`

## Testing Steps

### 1. Open Browser Console (F12)
Before clicking "Sign in with Google", open your browser's Developer Tools (F12) and go to the Console tab.

### 2. Click "Sign in with Google"
You should see in console:
```
Redirecting to: https://auth.emergentagent.com/?redirect=https://your-app-url.com
```

### 3. After Google Login
You'll be redirected back to your app with a `session_id` parameter.

Look for console logs:
```
Checking auth... session_id: [some-id]
Found session_id, creating session...
Creating session with session_id: [some-id]
```

### 4. If Successful
```
Session created successfully: {user: {...}}
```

### 5. If Failed
Check the console error for details. Common issues:

**"Invalid session ID"**
- The session_id from Emergent Auth couldn't be validated
- Check backend logs: `tail -f /var/log/supervisor/backend.err.log`

**"Access restricted to @beebyclarkmeyler.com"**
- You're not using a @beebyclarkmeyler.com email
- Use your company Google account

**Network Error**
- Backend might be down
- Check: `sudo supervisorctl status backend`

## Backend Logs

Check real-time logs:
```bash
tail -f /var/log/supervisor/backend.err.log
```

Look for:
- "HTTP Request: GET https://demobackend.emergentagent.com/auth/v1/oauth/session-data"
- "New user created: email@beebyclarkmeyler.com"
- Any error messages

## Manual Test

Test the auth endpoint directly:
```bash
# This should return "Invalid session ID" (expected)
curl -X POST http://localhost:8001/api/auth/session \
  -H "X-Session-ID: test" \
  -H "Content-Type: application/json"
```

## Common Issues

### Issue 1: Redirects to Login Immediately
**Cause:** Session not being created
**Solution:** Check browser console for errors

### Issue 2: "Not authenticated" after login
**Cause:** Cookies not being set
**Solution:** 
- Ensure HTTPS (required for secure cookies)
- Check if cookies are blocked in browser

### Issue 3: Domain restriction error
**Cause:** Not using @beebyclarkmeyler.com email
**Solution:** Use company Google account

## Debug Mode

Enable verbose logging in auth_routes.py:
```python
logger.setLevel(logging.DEBUG)
```

## Verify Services

```bash
# Check all services
sudo supervisorctl status

# Restart backend
sudo supervisorctl restart backend

# Check backend health
curl http://localhost:8001/api/
```

## Contact Info

If issues persist:
1. Check browser console (F12)
2. Check backend logs
3. Verify you're using @beebyclarkmeyler.com email
4. Ensure backend is running

## Success Indicators

When authentication works, you should see:
- ✅ Login page with Google button
- ✅ Redirected to auth.emergentagent.com
- ✅ Google sign-in page
- ✅ Redirected back to your app
- ✅ Main app interface (not login page)
- ✅ User name and email in header
- ✅ "Admin Panel" button (if first user)
