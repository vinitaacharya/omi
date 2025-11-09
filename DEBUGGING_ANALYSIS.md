# Debugging Analysis: 404 Error When Sending Messages

## Problem Summary
When navigating to the "ask" page and sending a message, the Flutter app receives a 404 error:
```
[error] | Failed to send message: 404
```

## Root Cause Identified

### Primary Issue: Chat Router is Disabled
The `/v2/messages` endpoint is not available because the chat router is commented out in `backend/main.py`:

**File:** `backend/main.py`
- **Line 11:** `# chat,  # Temporarily disabled - requires Opus library`
- **Line 47:** `# app.include_router(chat.router)  # Temporarily disabled - requires Opus`

### Why It Was Disabled
The chat router imports functions from `routers.sync` which requires the `opuslib` library. However, analysis shows that:
- The `/v2/messages` endpoint (for text messages) **does NOT directly use Opus**
- Only the `/v2/voice-messages` and `/v2/voice-message/transcribe` endpoints require Opus
- The text message endpoint should work without Opus

### Secondary Issues (Unrelated to 404)
1. **"Frames are empty"** - This is from `app/lib/services/wals.dart` line 583, related to audio frame processing in WAL service, not related to the HTTP 404 error.

2. **Connection Status** - `isConnected: false, isConnecting: true, connectedDevice: null` is about Bluetooth device connection status, not related to HTTP API calls.

## Additional Finding
✅ **`opuslib==3.0.1` IS present in `backend/requirements.txt` (line 137)**

This means the dependency should be available. The router was likely disabled due to:
- Runtime import errors in the deployment environment
- Missing system-level Opus library (see backend/README.md line 36-37)
- Temporary issue that has since been resolved

## Solution Plan

### Option 1: Re-enable Chat Router with Conditional Import (RECOMMENDED)
Make Opus-dependent code conditional so text endpoints always work:
1. Modify `backend/routers/chat.py` to make Opus imports conditional
2. Wrap voice endpoint logic in try/except or availability checks
3. Uncomment the chat router in `backend/main.py`
4. This allows text messaging to work even if Opus has issues
5. Voice endpoints will gracefully fail if Opus is unavailable

### Option 2: Split Chat Router
Separate text message endpoints from voice endpoints:
1. Create a new router file for text messages (`routers/chat_text.py`)
2. Move `/v2/messages`, `/v2/initial-message`, and `/v2/messages` GET endpoint to the new router
3. Keep voice endpoints in the original `chat.py` router
4. Register both routers in `main.py`, but make voice router conditional
5. This provides clean separation and better error handling

### Option 3: Direct Re-enable (Quick Test)
Simply re-enable the router to test if Opus works:
1. Uncomment the chat router import and registration in `backend/main.py`
2. Test if it works - if Opus import fails, we'll see the error
3. Then implement Option 1 if needed

## Recommended Next Steps

1. **Check Opus availability**: Verify if `opuslib` can be installed/available in the deployment environment
2. **Choose solution approach**: Based on Opus availability, choose Option 1, 2, or 3
3. **Implement the fix**: Make the necessary code changes
4. **Test the fix**: 
   - Verify `/v2/messages` POST endpoint works
   - Verify text messages can be sent from Flutter app
   - Test voice endpoints if they're being re-enabled
5. **Deploy and verify**: Deploy the backend changes and test end-to-end

## Files That Need Modification

1. **backend/main.py** - Uncomment or modify router registration
2. **backend/routers/chat.py** - May need refactoring if splitting routers (Option 2)
3. **backend/requirements.txt** - May need `opuslib` if going with Option 1

## Testing Checklist

- [ ] `/v2/messages` POST endpoint returns 200 (not 404)
- [ ] Text messages can be sent from Flutter app
- [ ] Messages are saved correctly
- [ ] Streaming response works correctly
- [ ] Authentication works properly
- [ ] Voice endpoints work (if re-enabled)
