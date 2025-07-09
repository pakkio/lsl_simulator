
// Test script for control flow (if/else, while)

integer i = 0;

default
{
    state_entry()
    {
        llSay(0, "--- Starting Control Flow Test ---");

        // While loop test
        llSay(0, "Starting while loop...");
        while (i < 3)
        {
            llSay(0, "i is " + (string)i);
            i = i + 1;
        }
        llSay(0, "Loop finished. Final i is " + (string)i);

        // If/else test
        if (i == 3)
        {
            llSay(0, "If condition is TRUE (correct).");
        }
        else
        {
            llSay(0, "If condition is FALSE (incorrect).");
        }
        
        if (i != 3)
        {
            llSay(0, "This should NOT be printed.");
        }

        llSay(0, "--- Test Complete ---");
    }
}
