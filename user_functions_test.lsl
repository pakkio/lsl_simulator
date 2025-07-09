
// Test script for user-defined functions and return statements

// A user-defined function
integer multiply(integer a, integer b)
{
    integer result = a * b;
    return result;
}

// A function that doesn't return a value
void sayDouble(integer val)
{
    llSay(0, "The double of " + (string)val + " is " + (string)(val * 2));
}

default
{
    state_entry()
    {
        llSay(0, "--- Starting User Function Tests ---");

        // Call the function that returns a value
        integer calculated_value = multiply(7, 6); // Should be 42
        llSay(0, "Calculated value is: " + (string)calculated_value);

        // Call the void function
        sayDouble(calculated_value); // Should say 84

        llSay(0, "--- Tests Complete ---");
    }
}
