
// Test script for for loops

default
{
    state_entry()
    {
        llSay(0, "--- Starting For Loop Test ---");

        integer i;
        for (i = 0; i < 3; i = i + 1)
        {
            llSay(0, "for loop iteration: " + (string)i);
        }
        
        llSay(0, "After loop, i is: " + (string)i); // Should be 3

        llSay(0, "--- Test Complete ---");
    }
}
