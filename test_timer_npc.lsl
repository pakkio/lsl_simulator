// Test timer event specifically
integer is_registered = FALSE;
string npc_profile_data = "test data";

integer check_if_npc() {
    llSetText("Timer check_if_npc called", <1,0,0>, 1.0);
    return osIsNpc(llGetOwner());
}

default {
    state_entry() {
        llSetText("Starting timer test", <1,1,0>, 1.0);
        llSetTimerEvent(3.0);
    }
    
    timer() {
        llSetText("Timer event fired!", <0,1,0>, 1.0);
        llSetText("is_registered: " + (string)is_registered, <0,1,0>, 1.0);
        llSetText("npc_profile_data: " + npc_profile_data, <0,1,0>, 1.0);
        
        if (!is_registered && check_if_npc() && npc_profile_data != "") {
            llSetText("✅ All checks passed - would register", <0,1,0>, 1.0);
        } else {
            llSetText("❌ Some check failed", <1,0,0>, 1.0);
        }
        
        llSetTimerEvent(0.0);
    }
}