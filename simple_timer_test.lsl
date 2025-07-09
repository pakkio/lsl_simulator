// Simple timer test

integer timer_count = 0;

default {
    state_entry() {
        llSetText("Starting timer test", <1,1,0>, 1.0);
        llSetTimerEvent(2.0);
    }
    
    timer() {
        timer_count++;
        llSay(0, "Timer event #" + (string)timer_count);
        
        if (timer_count < 3) {
            llSetTimerEvent(2.0);
        } else {
            llSay(0, "Timer test complete - stopping");
            llSetTimerEvent(0.0);
        }
    }
}