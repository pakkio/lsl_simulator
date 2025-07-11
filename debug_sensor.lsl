// Debug sensor test without using parameters
default {
    state_entry() {
        llSay(0, "Debug sensor test started");
    }
    
    sensor(integer detected) {
        llSay(0, "SENSOR EVENT EXECUTING");
    }
}