// Test minimal if statement bug
integer i = 3;

default
{
    state_entry()
    {
        llSay(0, "Starting test");
        
        if (i == 3)
        {
            llSay(0, "TRUE branch executed");
        }
        else
        {
            llSay(0, "FALSE branch executed");
        }
        
        llSay(0, "After if statement");
    }
}