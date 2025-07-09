// Test script to demonstrate the notecard reading bug

string NOTECARD_NAME = "npc_profile";
string npc_profile_data = "";
integer notecard_line = 0;
integer notecard_read_complete = FALSE;
integer is_registered = FALSE;

default {
    state_entry() {
        llSay(0, "Starting notecard read test");
        
        // Start reading notecard
        if (llGetInventoryType(NOTECARD_NAME) == INVENTORY_NOTECARD) {
            npc_profile_data = "";
            notecard_line = 0;
            notecard_read_complete = FALSE;
            llGetNotecardLine(NOTECARD_NAME, 0);
        } else {
            llSay(0, "Missing notecard");
        }
    }
    
    dataserver(key query_id, string data) {
        llSay(0, "dataserver event: line=" + (string)notecard_line + " data=" + data + " complete=" + (string)notecard_read_complete);
        
        if (notecard_read_complete) {
            llSay(0, "ERROR: dataserver called after completion!");
            return;
        }
        
        if (data == EOF) {
            llSay(0, "EOF reached - setting completion flag");
            notecard_read_complete = TRUE;
            
            // Simulate what happens in the original script
            if (!is_registered) {
                llSay(0, "Would register with nexus now");
                llSetTimerEvent(5.0);  // This sets up the timer for retry
            }
            return;
        }
        
        // Continue reading
        npc_profile_data += data + "\n";
        notecard_line++;
        
        llSay(0, "Reading next line: " + (string)notecard_line);
        if (!notecard_read_complete) {
            llGetNotecardLine(NOTECARD_NAME, notecard_line);
        }
    }
    
    timer() {
        llSay(0, "Timer fired! registered=" + (string)is_registered + " complete=" + (string)notecard_read_complete);
        
        if (!is_registered && npc_profile_data != "" && notecard_read_complete) {
            llSay(0, "Simulating registration failure - will retry");
            llSetTimerEvent(5.0);  // This continues the timer loop
        }
    }
}