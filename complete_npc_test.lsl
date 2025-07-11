// Complete NPC test with listeners
key current_avatar = NULL_KEY;

default {
    state_entry() {
        llSay(0, "Complete NPC Test Started");
        // Set up listeners like the real NPC
        llListen(0, "", NULL_KEY, "");  // Public channel
        llSay(0, "Listeners set up, ready for testing");
    }
    
    sensor(integer detected) {
        llSay(0, "SENSOR: Detected " + (string)detected + " avatars");
        
        if (detected > 0) {
            key avatar_key = llDetectedKey(0);
            string avatar_name = llDetectedName(0);
            float avatar_dist = llDetectedDist(0);
            
            llSay(0, "SENSOR: Found " + avatar_name + " at " + (string)avatar_dist + "m");
            llSay(0, "SENSOR: Avatar key: " + (string)avatar_key);
            
            current_avatar = avatar_key;
            llSay(0, "SENSOR: Set current_avatar to " + (string)current_avatar);
        }
    }
    
    listen(integer channel, string name, key id, string message) {
        llSay(0, "LISTEN: Got message '" + message + "' from " + name);
        llSay(0, "LISTEN: Current avatar: " + (string)current_avatar);
        llSay(0, "LISTEN: Speaker ID: " + (string)id);
        llSay(0, "LISTEN: ID Match: " + (string)(id == current_avatar));
        
        if (id == current_avatar) {
            llSay(0, "NPC: Hello " + name + "! Nice to meet you.");
        }
    }
}