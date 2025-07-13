default {
    state_entry() {
        integer num = 42;
        float fnum = 3.14;
        
        llSay(0, "Testing type casts:");
        llSay(0, "Integer to string: " + (string)num);
        llSay(0, "Float to string: " + (string)fnum);
        llSay(0, "String to integer: " + (string)((integer)"123"));
    }
}