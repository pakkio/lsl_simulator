// Simplified comprehensive test to debug issues
string g_name = "Test Object";
vector g_pos = <128.0, 128.0, 22.0>;

// User function
float distance(vector a, vector b)
{
    vector diff = a - b;
    return llVecMag(diff);
}

default
{
    state_entry()
    {
        llSay(0, "=== Simple Test Started ===");
        
        // Test 1: Basic expressions
        integer result = 5 + 3;
        llSay(0, "5 + 3 = " + (string)result);
        
        // Test 2: Vector operations
        vector pos = llGetPos();
        llSay(0, "Position: " + (string)pos.x + "," + (string)pos.y + "," + (string)pos.z);
        
        // Test 3: Vector math
        vector test_vec = <3.0, 4.0, 0.0>;
        float magnitude = llVecMag(test_vec);
        llSay(0, "Magnitude: " + (string)magnitude);
        
        // Test 4: User function
        float dist = distance(pos, g_pos);
        llSay(0, "Distance: " + (string)dist);
        
        // Test 5: Control flow
        if (magnitude > 4.0)
        {
            llSay(0, "Magnitude is greater than 4");
        }
        
        // Test 6: For loop
        for (integer i = 1; i <= 3; i++)
        {
            llSay(0, "Loop: " + (string)i);
        }
        
        llSay(0, "=== Test Complete ===");
    }
}