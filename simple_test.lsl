test_func() {
    llSay(0, "Hello from test_func!");
}

default {
    state_entry() {
        llSay(0, "Before function");
        test_func();
        llSay(0, "After function");
    }
}