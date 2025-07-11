// Test NPC sensor functionality
key current_avatar = NULL_KEY;

default {
    state_entry() {
        llSay(0, "NPC Sensor Test Started");
    }
    
    sensor(integer detected) {
        llSay(0, "SENSOR: Detected " + (string)detected + " avatars");
        
        if (detected > 0) {
            key avatar_key = llDetectedKey(0);
            string avatar_name = llDetectedName(0);
            float avatar_dist = llDetectedDist(0);
            
            llSay(0, "SENSOR: Found " + avatar_name + " at " + (string)avatar_dist + "m (key: " + (string)avatar_key + ")");
            
            current_avatar = avatar_key;
            llSay(0, "SENSOR: Set current_avatar to " + (string)current_avatar);
        }
    }
    
    listen(integer channel, string name, key id, string message) {
        llSay(0, "LISTEN: Channel " + (string)channel + ", Name: " + name + ", ID: " + (string)id + ", Message: " + message);
        llSay(0, "LISTEN: Current avatar: " + (string)current_avatar + ", ID match: " + (string)(id == current_avatar));
    }
}