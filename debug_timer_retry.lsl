// Debug script to check timer retry behavior

integer is_registered = FALSE;
string npc_profile_data = "test profile data";
integer timer_count = 0;

default {
    state_entry() {
        llSetText("Starting timer retry test", <1,1,0>, 1.0);
        llSetTimerEvent(2.0);
    }
    
    timer() {
        timer_count++;
        llSay(0, "Timer event #" + (string)timer_count);
        llSay(0, "is_registered: " + (string)is_registered);
        llSay(0, "npc_profile_data: " + npc_profile_data);
        
        if (current_avatar != NULL_KEY) {
            llSay(0, "Would end conversation");
        } else if (!is_registered && npc_profile_data != "") {
            llSay(0, "Would retry registration");
            // Simulate what register_with_nexus() does when it fails
            if (timer_count < 3) {
                llSetTimerEvent(5.0);  // This is the retry timer
                return;  // Don't set timer to 0 below
            } else {
                llSay(0, "Simulating successful registration");
                is_registered = TRUE;
            }
        }
        
        llSetTimerEvent(0.0);
    }
}