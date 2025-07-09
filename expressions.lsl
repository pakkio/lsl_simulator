
integer i = 0;
string message = "Hello";

default
{
    state_entry()
    {
        llSay(0, "Starting expression test.");
        
        i = i + 1;
        llSay(0, "i is now " + (string)i); // Should be 1
        
        integer j = (5 + 3) * 2;
        llSay(0, "j is " + (string)j); // Should be 16
        
        string full_message = message + ", world!";
        llSay(0, full_message); // Should be "Hello, world!"
        
        llSay(0, "Test complete.");
    }
}
