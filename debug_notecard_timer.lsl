// Debug script to isolate the timer/notecard issue

string NOTECARD_NAME = "npc_profile";
string npc_profile_data = "";
integer notecard_line = 0;
integer notecard_read_complete = FALSE;
integer is_registered = FALSE;

default {
    state_entry() {
        llSetText("DEBUG: Starting notecard read", <1,1,0>, 1.0);
        
        // Start reading notecard
        if (llGetInventoryType(NOTECARD_NAME) == INVENTORY_NOTECARD) {
            npc_profile_data = "";
            notecard_line = 0;
            notecard_read_complete = FALSE;
            llGetNotecardLine(NOTECARD_NAME, 0);
        } else {
            llSetText("❌ Missing " + NOTECARD_NAME, <1,0,0>, 1.0);
            llSetTimerEvent(30.0);
        }
    }
    
    dataserver(key query_id, string data) {
        llSay(0, "DEBUG: dataserver called with: " + data + " (complete=" + (string)notecard_read_complete + ")");
        
        if (notecard_read_complete) {
            llSay(0, "DEBUG: Ignoring dataserver event - already complete");
            return;
        }
        
        if (data == EOF) {
            llSay(0, "DEBUG: EOF reached - setting complete flag");
            notecard_read_complete = TRUE;
            
            // Now check if we should register
            if (!is_registered) {
                llSay(0, "DEBUG: Not registered yet - would call register");
                // simulate register failure for testing
                llSetTimerEvent(5.0);
            }
            return;
        }
        
        // Continue reading
        npc_profile_data += data + "\n";
        notecard_line++;
        
        llSay(0, "DEBUG: Read line " + (string)notecard_line + " - requesting next");
        if (!notecard_read_complete) {
            llGetNotecardLine(NOTECARD_NAME, notecard_line);
        }
    }
    
    timer() {
        llSay(0, "DEBUG: Timer fired! is_registered=" + (string)is_registered + 
              " notecard_complete=" + (string)notecard_read_complete +
              " profile_data_len=" + (string)llStringLength(npc_profile_data));
        
        if (!is_registered && npc_profile_data != "") {
            llSay(0, "DEBUG: Conditions met for registration retry");
            // In real script, this would call register_with_nexus()
            // For testing, let's simulate registration failure
            llSetTimerEvent(5.0);
        }
        
        // Note: The original script sets timer to 0.0 here, but only after the if-else
        llSetTimerEvent(0.0);
    }
}