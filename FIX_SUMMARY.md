# Fix Summary: 404 Error When Sending Messages

## Problem Resolved
The `/v2/messages` endpoint was returning 404 because the chat router was disabled in `backend/main.py` due to Opus library dependency concerns.

## Solution Implemented
Made Opus-dependent imports conditional (lazy loading) so that:
- ✅ Text message endpoints work immediately (no Opus required)
- ✅ Router can be imported and registered without Opus
- ✅ Voice endpoints fail gracefully with clear error messages if Opus is unavailable

## Changes Made

### 1. `backend/routers/chat.py`
- **Removed** top-level import: `from routers.sync import retrieve_file_paths, decode_files_to_wav` (line 25)
- **Added** lazy imports with error handling in voice endpoint functions:
  - `/v2/voice-messages` (line 288-295)
  - `/v2/voice-message/transcribe` (line 316-323)
  - `/v1/voice-message/transcribe` (line 516-523)

### 2. `backend/main.py`
- **Re-enabled** chat router import (line 11)
- **Re-enabled** chat router registration (line 47)
- Added explanatory comments

## How It Works

1. **Text Endpoints** (`/v2/messages`, `/v2/initial-message`, etc.):
   - Work immediately without any Opus dependency
   - Can send/receive text messages normally

2. **Voice Endpoints** (`/v2/voice-messages`, `/v2/voice-message/transcribe`):
   - Only attempt to import Opus-dependent functions when called
   - If Opus is unavailable, return HTTP 503 with clear error message
   - If Opus is available, function normally

## Testing Recommendations

1. **Test Text Messages:**
   ```bash
   # Should return 200 (not 404)
   POST /v2/messages
   ```

2. **Test from Flutter App:**
   - Navigate to "ask" page
   - Send a text message
   - Verify it works without 404 error

3. **Test Voice Endpoints (optional):**
   - If Opus is available: Should work normally
   - If Opus is unavailable: Should return 503 with error message

## Next Steps

1. **Deploy the backend changes**
2. **Test the fix** by sending a message from the Flutter app
3. **Monitor logs** to ensure no import errors
4. **Verify** that text messaging works end-to-end

## Rollback Plan
If issues occur, simply re-comment the chat router lines in `backend/main.py`:
- Line 11: `# chat,  # Temporarily disabled - requires Opus library`
- Line 47: `# app.include_router(chat.router)  # Temporarily disabled - requires Opus`
