# Implementation Plan: Fix 404 Error for Text Messages

## Problem
The `/v2/messages` endpoint returns 404 because the chat router is disabled in `backend/main.py` due to Opus library dependency concerns.

## Root Cause
- Chat router imports `decode_files_to_wav` from `routers.sync` at the module level
- `routers.sync` imports `opuslib` at the module level
- This causes import failure even though text endpoints don't need Opus
- Text endpoint `/v2/messages` doesn't use Opus-dependent functions at all

## Solution: Lazy Import Pattern

Make the Opus-dependent imports conditional/lazy so the router can load even if Opus is unavailable.

### Step 1: Modify `backend/routers/chat.py`
**Change:** Move the sync imports inside the voice endpoint functions instead of at module level.

**Current (line 25):**
```python
from routers.sync import retrieve_file_paths, decode_files_to_wav
```

**New approach:**
- Remove the top-level import
- Import inside voice endpoint functions where needed
- Wrap in try/except to handle missing Opus gracefully

### Step 2: Re-enable Chat Router
**File:** `backend/main.py`
- Uncomment line 11: `chat,` in the imports
- Uncomment line 47: `app.include_router(chat.router)`

### Step 3: Add Error Handling
Ensure voice endpoints return proper errors if Opus is unavailable, rather than crashing.

## Implementation Details

### Modified Code Structure

**backend/routers/chat.py:**
1. Remove: `from routers.sync import retrieve_file_paths, decode_files_to_wav` (line 25)
2. Add lazy imports in voice endpoint functions:
   ```python
   @router.post("/v2/voice-messages")
   async def create_voice_message_stream(...):
       try:
           from routers.sync import retrieve_file_paths, decode_files_to_wav
       except ImportError as e:
           raise HTTPException(status_code=503, detail="Voice processing unavailable: Opus library not available")
       # ... rest of function
   ```

3. Do the same for `/v2/voice-message/transcribe` endpoint

### Benefits
- ✅ Text endpoints work immediately (no Opus needed)
- ✅ Router can be imported and registered without Opus
- ✅ Voice endpoints fail gracefully with clear error messages
- ✅ Minimal code changes
- ✅ Backward compatible

## Testing Plan

1. **Test Text Messages:**
   - POST to `/v2/messages` with text - should return 200
   - Verify streaming response works
   - Verify messages are saved

2. **Test Voice Messages (if Opus available):**
   - POST to `/v2/voice-messages` - should work if Opus is available
   - POST to `/v2/voice-messages` - should return 503 if Opus is unavailable

3. **Test Flutter App:**
   - Send text message from app - should work
   - Verify no 404 errors
   - Verify message appears in conversation

## Rollback Plan
If issues occur, simply re-comment the chat router lines in `main.py`.

## Risk Assessment
- **Low Risk**: Text endpoints don't use Opus, so this change is safe
- **Medium Risk**: Need to verify Opus availability in production environment
- **Mitigation**: Graceful error handling for voice endpoints
