test_function() {
    llSay(0, "Inside test_function!");
    llSetAlpha(0.5, ALL_SIDES);
}

default {
    state_entry() {
        llSay(0, "Before function call");
        test_function();
        llSay(0, "After function call");
    }
}