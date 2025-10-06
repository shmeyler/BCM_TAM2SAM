# OAuth Debugging Instructions

## Step-by-Step Debug Process

### 1. Open Browser Developer Console
- Press **F12** or right-click → "Inspect"
- Go to **Console** tab
- Keep it open during the entire process

### 2. Clear Console
- Click the 🚫 (clear) button in the console

### 3. Click "Sign in with Google"
- Watch the console for the first log: "Redirecting to: https://auth.emergentagent.com/..."

### 4. Complete Google Sign-in
- Sign in with your @beebyclarkmeyler.com account
- Allow permissions if asked

### 5. After Redirect Back to App
**IMMEDIATELY look at the console output**. You should see:

```
Checking auth...
- Full URL: [YOUR_APP_URL]
- Query params: [THIS IS IMPORTANT - COPY THIS]
- Hash: [THIS IS IMPORTANT - COPY THIS]
- Session ID found: [VALUE OR null]
All URL params: {...}
All hash params: {...}
```

### 6. Copy and Share
**Please copy the ENTIRE console output** and share it, especially:
- The "Full URL" line
- The "Query params" line  
- The "Hash" line
- The "All URL params" object
- The "All hash params" object

### What We're Looking For

The session identifier could be in:
1. Query parameter: `?session_id=xxx` or `?code=xxx`
2. Hash parameter: `#session_id=xxx` or `#code=xxx`
3. Some other parameter name we haven't checked yet

### Example of What to Share

```
Checking auth...
- Full URL: https://market-insights-60.preview.emergentagent.com/?some_param=value
- Query params: ?some_param=value
- Hash: #another_param=value
- Session ID found: null
All URL params: {some_param: "value"}
All hash params: {another_param: "value"}
```

## Alternative: Check URL Manually

After you're redirected back from Google:
1. Look at your browser's **address bar**
2. Copy the **entire URL**
3. Share it (the session ID in the URL is temporary and expires quickly, so it's safe to share)

Example:
```
https://market-insights-60.preview.emergentagent.com/?session_id=abc123
```

or

```
https://market-insights-60.preview.emergentagent.com/#session_id=abc123
```

## What Happens Next

Once we see the actual URL structure, we can:
1. Identify the correct parameter name
2. Fix the code to read it properly
3. Complete the authentication flow

## Current Code Checks

The app currently looks for:
- `?session_id=...` (query parameter)
- `?code=...` (query parameter)
- `#session_id=...` (hash parameter)
- `#code=...` (hash parameter)

If Emergent Auth uses a different parameter name or structure, we'll update the code accordingly.
