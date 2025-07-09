
// Test script for various LSL functions

list test_list = ["apple", "banana", "cherry"];

default
{
    state_entry()
    {
        llSay(0, "--- Starting Function Tests ---");

        // Math Tests
        float pi = 3.14159;
        float sin_val = llSin(pi / 2.0); // Should be 1.0
        llSay(0, "Sine of pi/2 is: " + (string)sin_val);
        
        float sqrt_val = llSqrt(16.0); // Should be 4.0
        llSay(0, "Square root of 16 is: " + (string)sqrt_val);

        // Random Tests
        key random_key = llGenerateKey();
        llSay(0, "Generated Key: " + (string)random_key);
        
        float random_float = llFrand(10.0);
        llSay(0, "Random float between 0 and 10: " + (string)random_float);

        // String Tests
        string test_string = "hello world";
        integer len = llStringLength(test_string); // Should be 11
        llSay(0, "Length of '" + test_string + "' is: " + (string)len);
        
        integer index = llSubStringIndex(test_string, "world"); // Should be 6
        llSay(0, "Index of 'world' is: " + (string)index);

        // List Tests
        integer list_len = llGetListLength(test_list); // Should be 3
        llSay(0, "Length of test_list is: " + (string)list_len);
        
        string item = llList2String(test_list, 1); // Should be "banana"
        llSay(0, "Item at index 1 is: " + item);
        
        llSay(0, "--- Tests Complete ---");
    }
}
