# Custom Domain Setup - www.bcmventas.com

## Changes Made for Custom Domain Support

### 1. Auto-Detection of Backend URL

**File:** `/app/frontend/src/App.js`

The app now automatically detects which domain it's running on:

```javascript
const getBackendUrl = () => {
  const hostname = window.location.hostname;
  
  // Custom domain
  if (hostname === 'www.bcmventas.com' || hostname === 'bcmventas.com') {
    return `https://${hostname}`;
  }
  
  // Preview/localhost - use environment variable
  return process.env.REACT_APP_BACKEND_URL || window.location.origin;
};
```

**What This Means:**
- ✅ On `www.bcmventas.com` → Uses `https://www.bcmventas.com/api`
- ✅ On preview → Uses `https://segmentation-pro.preview.emergentagent.com/api`
- ✅ Automatically switches based on current URL

### 2. OAuth Redirect Auto-Configuration

**File:** `/app/frontend/src/components/Login.js`

OAuth redirects now use the current domain:

```javascript
const redirectUrl = window.location.origin;
// On www.bcmventas.com → redirects back to https://www.bcmventas.com
// On preview → redirects back to preview URL
```

### 3. CORS Configuration

**File:** `/app/backend/server.py`

Already configured to allow all origins:
```python
allow_origins=["*"]  # Allows both custom domain and preview
```

---

## How It Works Now

### Preview Site (https://segmentation-pro.preview.emergentagent.com)
1. User clicks "Sign in with Google"
2. Redirects to: `https://auth.emergentagent.com/?redirect=https://segmentation-pro.preview.emergentagent.com`
3. After OAuth: Returns to `https://segmentation-pro.preview.emergentagent.com#session_id=...`
4. Backend URL: `https://segmentation-pro.preview.emergentagent.com/api`

### Custom Domain (https://www.bcmventas.com)
1. User clicks "Sign in with Google"
2. Redirects to: `https://auth.emergentagent.com/?redirect=https://www.bcmventas.com`
3. After OAuth: Returns to `https://www.bcmventas.com#session_id=...`
4. Backend URL: `https://www.bcmventas.com/api`

---

## Testing

### On Preview Site:
1. Go to: `https://segmentation-pro.preview.emergentagent.com`
2. Open console (F12) - should see: `Backend URL: https://segmentation-pro.preview.emergentagent.com`
3. Login should work ✅

### On Custom Domain:
1. Go to: `https://www.bcmventas.com`
2. Open console (F12) - should see: `Backend URL: https://www.bcmventas.com`
3. Login should work ✅

---

## Troubleshooting

### If Authentication Still Fails on Custom Domain:

**1. Check Console Logs**
Open F12 → Console and look for:
```
Backend URL: https://www.bcmventas.com
OAuth Login Details:
- Current domain: https://www.bcmventas.com
- Redirect URL: https://www.bcmventas.com
- Auth URL: https://auth.emergentagent.com/?redirect=...
```

**2. Verify Backend is Accessible**
Try opening: `https://www.bcmventas.com/api/`

Should return:
```json
{
  "message": "Market Map API Ready",
  "version": "2.0.0"
}
```

**3. Check OAuth Redirect**
After signing in with Google:
- URL should have: `https://www.bcmventas.com#session_id=...`
- Look for `session_id` in the URL fragment (after #)

**4. Clear Browser Cache**
- Custom domain might have cached old frontend code
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Or try in Incognito/Private window

**5. Verify Deployment**
- Make sure latest code is deployed to custom domain
- Check deployment logs in Emergent

---

## Environment Variables

### Preview (.env files in repo):
```bash
# Frontend
REACT_APP_BACKEND_URL=https://segmentation-pro.preview.emergentagent.com
REACT_APP_AUTH_URL=https://auth.emergentagent.com

# Backend
MONGO_URL=mongodb://localhost:27017
DB_NAME=market_map_db
TOGETHER_API_KEY=[your-key]
```

### Production (Emergent Deployment Config):
**No environment variable changes needed!**

The code auto-detects the domain, so the same `.env` files work for both preview and production with custom domain.

---

## Verification Checklist

After deploying to custom domain:

- [ ] Navigate to `https://www.bcmventas.com`
- [ ] Check browser console - should show correct backend URL
- [ ] Click "Sign in with Google"
- [ ] Check OAuth redirect includes correct domain
- [ ] Complete Google sign-in
- [ ] Should return to `www.bcmventas.com` with session_id
- [ ] Should be logged in successfully
- [ ] Profile shows in header
- [ ] Can generate market analysis
- [ ] Can access admin panel (if admin)

---

## Additional Notes

### Both Domains Work Simultaneously:
- Preview: `https://segmentation-pro.preview.emergentagent.com` ✅
- Custom: `https://www.bcmventas.com` ✅
- Both use same backend and database
- Users can login on either domain

### Database:
- Shared MongoDB database
- Users authenticated on preview can also use custom domain
- Same user accounts across both domains

### OAuth:
- Emergent Auth works with any redirect URL
- Session IDs work for both domains
- Domain restriction still enforced (@beebyclarkmeyler.com)

---

## Support

If authentication still doesn't work on custom domain:

1. **Check Console** - Look for any red errors
2. **Check Backend URL** - Verify it's using `www.bcmventas.com`
3. **Test API** - Try `https://www.bcmventas.com/api/`
4. **Hard Refresh** - Clear cache (Ctrl+Shift+R)
5. **Incognito Mode** - Test in private window

**Backend Logs:**
```bash
tail -f /var/log/supervisor/backend.err.log
```

Look for authentication attempts and any errors.
