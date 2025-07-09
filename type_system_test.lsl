
// Test script for the stricter type system

integer g_my_int = 10;
string  g_my_string = "hello";

default
{
    state_entry()
    {
        llSay(0, "--- Starting Type System Test ---");

        // 1. Valid assignment
        integer local_int = 20;
        llSay(0, "local_int is " + (string)local_int);

        // 2. Type mismatch that should generate a warning
        // In LSL, this would cast "30" to an integer. Our sim should warn.
        llSay(0, "About to perform a type-mismatched assignment...");
        local_int = "30"; 
        
        llSay(0, "After assignment, local_int is " + (string)local_int); // Should be 30

        // 3. Assignment to an undeclared variable (should error)
        // undeclared_var = 5; // This would cause a runtime error in the sim

        llSay(0, "--- Test Complete ---");
    }
}
