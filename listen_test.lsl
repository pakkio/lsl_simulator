
default
{
    state_entry()
    {
        llSay(0, "Listen example started. Say 'hello' on channel 1.");
        // Listen for the exact message "hello" on channel 1 from anyone.
        llListen(1, "", "", "hello"); 
    }

    listen(integer channel, string name, key id, string message)
    {
        llSay(0, "I heard '" + message + "' from " + name + " on channel " + (string)channel + ".");
        
        // Now, listen for 'goodbye' to demonstrate changing listeners.
        llSay(0, "Now listening for 'goodbye'.");
        llListen(1, "", "", "goodbye"); 
    }
}
