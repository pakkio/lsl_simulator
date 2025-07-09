// Simple test to see notecard reading sequence

string NOTECARD_NAME = "npc_profile";
integer notecard_line = 0;
integer notecard_read_complete = FALSE;

default {
    state_entry() {
        llSay(0, "Starting notecard read");
        llGetNotecardLine(NOTECARD_NAME, 0);
    }
    
    dataserver(key query_id, string data) {
        llSay(0, "dataserver: line=" + (string)notecard_line + " data=" + data);
        
        if (data == EOF) {
            llSay(0, "EOF reached!");
            notecard_read_complete = TRUE;
            return;
        }
        
        notecard_line++;
        llGetNotecardLine(NOTECARD_NAME, notecard_line);
    }
}