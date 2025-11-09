# Troubleshooting: 404 Error Still Persisting

## Steps to Debug

### 1. Check Server Startup Logs
After restarting the server, look for these messages in the console:
```
✓ Chat router registered successfully with X routes
  Registered: POST /v2/messages
  Registered: GET /v2/messages
  ...
```

**If you see an error instead:**
- The router failed to load
- Check the error message and fix the issue

**If you don't see these messages:**
- The router might not be included
- Check that `app.include_router(chat.router)` is uncommented in `main.py`

### 2. Verify Routes via OpenAPI Docs
1. Start your server
2. Open browser to: `http://127.0.0.1:8000/docs`
3. Look for `/v2/messages` in the API documentation
4. If it's not there, the router isn't registered

### 3. Check Route Registration Order
FastAPI processes routes in registration order. Make sure:
- `chat.router` is included BEFORE any catch-all routes
- No other router has a conflicting `/v2/messages` route

### 4. Verify Server is Running Latest Code
1. Stop the server completely (Ctrl+C)
2. Make sure all changes are saved
3. Restart the server: `uvicorn main:app --reload --env-file .env`
4. Check the startup logs

### 5. Test Routes Directly
You can use the verification script:
```bash
cd backend
python verify_routes.py
```

Or test manually:
```bash
# Test GET /v2/messages (will require auth, but should not return 404)
curl -X GET "http://127.0.0.1:8000/v2/messages?app_id=" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test POST /v2/messages (will require auth and body, but should not return 404)
curl -X POST "http://127.0.0.1:8000/v2/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
```

### 6. Check for Import Errors
If the router import fails silently, check:
1. Are there any syntax errors in `routers/chat.py`?
2. Are all dependencies available?
3. Check Python path and virtual environment

### 7. Common Issues

#### Issue: Router imports but routes don't register
**Solution:** Check for exceptions during route decoration. Look for any syntax errors or import issues.

#### Issue: Routes registered but still 404
**Possible causes:**
- Middleware intercepting requests
- Route prefix mismatch
- Authentication failing before route handler

#### Issue: Server reloads but changes don't apply
**Solution:** 
- Stop server completely
- Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`
- Restart server

## Expected Behavior After Fix

1. Server starts without errors
2. Console shows: "✓ Chat router registered successfully"
3. `/v2/messages` appears in `/docs` endpoint
4. Flutter app can send messages without 404 error

## If Still Not Working

1. Share the server startup logs (especially the router registration messages)
2. Share the output of `/openapi.json` endpoint
3. Verify the exact URL the Flutter app is calling
4. Check if there are any middleware or proxy issues
