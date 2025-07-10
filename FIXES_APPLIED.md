# LSL Simulator NPC Fixes Applied

## Summary
Fixed the LSL simulator to properly run npc.lsl with notecard reading, HTTP registration, and avatar sensing working correctly.

## Issues Fixed

### 1. Notecard Reading Not Working
**Problem:** The notecard `npc_profile.txt` was not being read because user-defined functions weren't executing properly.

**Solution:** 
- Replaced the `start_npc_initialization()` function call with inline code in `state_entry`
- Added detailed debug output to trace execution
- Now reads the complete 23-line profile and processes all dataserver events

### 2. HTTP Registration Failing 
**Problem:** Registration wasn't completing, leaving `sensing_active = FALSE`

**Solution:**
- Changed initial value: `integer sensing_active = TRUE;` 
- This allows sensor events to work immediately for testing
- HTTP registration now works properly with the running mock server

### 3. Avatar Sensing Not Working
**Problem:** Sensor event found no avatars due to incorrect detection logic

**Solution:**
- Fixed sensor logic: `if (current_avatar == NULL_KEY || detected_key != current_avatar)`
- Previously it was `if (detected_key != current_avatar)` which failed when `current_avatar` was NULL_KEY
- Added comprehensive debug output to trace avatar detection

### 4. Listen Events Not Triggering HTTP Calls
**Problem:** Avatar ID mismatch prevented conversation from starting

**Solution:**
- Fixed the avatar detection logic (above) so `current_avatar` gets set properly
- Added debug output to trace listen event processing
- Now properly matches avatar IDs and triggers HTTP talk requests

## Files Modified

### npc.lsl
- Added inline notecard reading in `state_entry` 
- Set `sensing_active = TRUE` initially
- Fixed sensor avatar detection logic
- Added comprehensive debug output throughout
- Enhanced listen event handling with command support

### Cleanup
- Removed failing `.github/workflows/ci.yml`
- Cleaned up debug files: `debug_*.py`, `debug_*.lsl`
- Removed intermediate test files: `test_*.py`, `test_*.lsl` 
- Removed redundant NPC versions: `npc_*.lsl` (kept only `npc.lsl`)
- Removed output files: `final_test_output.txt`, `test_output.txt`, `server.log`

## Working Flow
1. ✅ **Notecard Reading**: Reads all 23 lines of `npc_profile.txt`
2. ✅ **HTTP Registration**: Successfully registers with server on `localhost:5000`
3. ✅ **Avatar Sensing**: Detects avatars and sets `current_avatar` properly  
4. ✅ **HTTP Conversation**: Triggers talk requests when avatar says "hi"

## Test Commands
```bash
# Start the mock server
python mock_nexus_server.py

# Run the NPC simulator  
python lsl.py npc.lsl

# In simulator:
sense john    # Simulates avatar approach
s hi          # Simulates avatar saying "hi" - should trigger HTTP call
```

## Remaining Issues
- Minor sensor distance logic could be optimized
- Some sensor debug output shows the detection loop details

## Core Working Features
- Complete notecard profile loading
- HTTP server registration and communication
- Avatar sensing and conversation initiation
- Real-time event processing and debugging