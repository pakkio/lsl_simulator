default {
    state_entry() {
        llSay(0, "Before declaration");
        string handle = llListen(1, "", "", "");
        llSay(0, "After declaration: " + handle);
    }
}