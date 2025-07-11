// Simple sensor test
default {
    state_entry() {
        llSay(0, "Simple sensor test started");
    }
    
    sensor(integer detected) {
        llSay(0, "SIMPLE SENSOR: detected=" + (string)detected);
        
        if (detected > 0) {
            key avatar_key = llDetectedKey(0);
            string avatar_name = llDetectedName(0);
            float avatar_dist = llDetectedDist(0);
            
            llSay(0, "SIMPLE SENSOR: Found avatar " + avatar_name + " at " + (string)avatar_dist + "m");
            llSay(0, "SIMPLE SENSOR: Avatar key = " + (string)avatar_key);
        }
    }
}